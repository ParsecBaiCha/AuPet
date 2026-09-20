-- 2026-09-21 家长知情同意（监护人同意）机制
-- 配合 backend/guardian_consent.py 使用。
-- 幂等：可重复执行；建表使用 IF NOT EXISTS，历史存量登记使用 NOT EXISTS 判断。
-- 执行：mysql -uroot -p teacher_psych_system < 20260921_guardian_consent.sql
--
-- 设计说明：
-- 1. 同意是「分项」的，编号见 CONSENT_SCOPES：
--    1=账号基本信息（必需） 2=保存AI对话记录 3=情绪与困难关键词标记
--    4=教师查看与家校沟通 5=去标识化研究与模型改进（可选，默认不勾）
-- 2. 每次同意或撤回都新增一条记录，以该学生最新一条（最大 id）为准，不修改历史记录。
-- 3. 只要最新一条不是 agreed，或者 scopes 里没有 2，该学生就不保存对话、
--    教师端与管理员端也查不到其对话内容。

-- ============ 1. 同意登记表 ============
CREATE TABLE IF NOT EXISTS `guardian_consents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL COMMENT '学生ID',
  `guardian_name` varchar(50) NOT NULL DEFAULT '' COMMENT '监护人姓名',
  `guardian_relation` varchar(20) NOT NULL DEFAULT '监护人' COMMENT '与学生关系',
  `guardian_phone` varchar(20) NOT NULL DEFAULT '' COMMENT '监护人手机号',
  `scopes` varchar(100) NOT NULL DEFAULT '' COMMENT '同意项编号，逗号分隔',
  `terms_version` varchar(20) NOT NULL DEFAULT '' COMMENT '同意的条款版本',
  `status` varchar(10) NOT NULL DEFAULT 'agreed' COMMENT 'agreed/revoked',
  `method` varchar(20) NOT NULL DEFAULT 'sms' COMMENT 'sms/paper_batch/legacy_import',
  `under_14` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否不满十四周岁',
  `note` varchar(255) DEFAULT NULL,
  `operator_id` int DEFAULT NULL COMMENT '代登记的老师或管理员ID',
  `consented_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `revoked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_student` (`student_id`,`id`),
  KEY `idx_state` (`status`,`consented_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='家长知情同意登记（每次同意或撤回新增一条，以最新一条为准）';

-- ============ 2. 监护人短信验证码 ============
CREATE TABLE IF NOT EXISTS `guardian_consent_codes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `guardian_phone` varchar(20) NOT NULL,
  `code` varchar(10) NOT NULL,
  `used` tinyint(1) NOT NULL DEFAULT '0',
  `expires_at` datetime NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_student` (`student_id`,`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='监护人短信验证码';

-- ============ 3. 历史存量学生登记（只需执行一次） ============
-- 说明：同意机制启用前已经在册的学生，按「学校已统一告知」处理并标注为历史存量，
--       避免老师端某天突然看不到对话；后续应尽快回收纸质《告家长书》并重新登记。
INSERT INTO `guardian_consents`
  (`student_id`,`guardian_name`,`guardian_relation`,`guardian_phone`,`scopes`,`terms_version`,`status`,`method`,`under_14`,`note`)
SELECT s.id, '（历史存量）', '未采集', '', '1,2,3,4', '2026-09-v1', 'agreed', 'legacy_import', 0,
       '启用同意机制前的存量学生，按学校统一告知处理，待补齐纸质《告家长书》'
FROM `students` s
WHERE NOT EXISTS (SELECT 1 FROM `guardian_consents` g WHERE g.student_id = s.id);

-- ============ 4. 常用运维语句 ============

-- 4.1 查看某个学生的当前同意状态（以最新一条为准）
-- SELECT id, student_id, status, scopes, method, guardian_name, consented_at, revoked_at
-- FROM guardian_consents WHERE student_id = 2 ORDER BY id DESC;

-- 4.2 查看全校/全班登记覆盖率
-- SELECT c.name 班级, COUNT(*) 人数,
--        SUM(CASE WHEN g.status='agreed' AND FIND_IN_SET('2', g.scopes) THEN 1 ELSE 0 END) 已同意保存对话,
--        SUM(CASE WHEN g.status='revoked' THEN 1 ELSE 0 END) 已撤回
-- FROM students s LEFT JOIN classes c ON c.id=s.class_id
-- LEFT JOIN guardian_consents g ON g.id=(SELECT MAX(id) FROM guardian_consents x WHERE x.student_id=s.id)
-- GROUP BY c.name;

-- 4.3 演示用：模拟家长撤回同意（把 id=2 换成你的测试学生）
-- INSERT INTO guardian_consents(student_id,guardian_name,guardian_relation,guardian_phone,scopes,
--   terms_version,status,method,under_14,note,revoked_at)
-- VALUES(2,'（演示撤回）','监护人','','','2026-09-v1','revoked','sms',0,'演示用撤回记录',NOW());

-- 4.4 演示用：恢复同意（挂在 4.3 之后执行，恢复为已同意）
-- INSERT INTO guardian_consents(student_id,guardian_name,guardian_relation,guardian_phone,scopes,
--   terms_version,status,method,under_14,note)
-- VALUES(2,'（演示恢复）','监护人','13800000000','1,2,3,4','2026-09-v1','agreed','sms',0,'演示用恢复正常状态');

-- 4.5 到期清理：一年前的验证码记录
-- DELETE FROM guardian_consent_codes WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- ============ 5. 校验 ============
-- SHOW COLUMNS FROM guardian_consents;
-- SELECT status, COUNT(*) FROM guardian_consents GROUP BY status;
