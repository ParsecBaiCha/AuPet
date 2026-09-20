-- ============================================================
-- 在线编程练习记录表（2026-09-17）
-- 目的：把学生在 /online-programming 页面写的代码与判题结果
--       从"仅浏览器 localStorage"升级为"后端留痕 + 教师可见 +
--       学习路径可统计"。
-- 使用：mysql -u root -p teacher_psych_system < 20260917_programming_records.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS `programming_submissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL COMMENT '关联 students.id',
  `course_key` varchar(40) NOT NULL COMMENT '在线编程课程标识，如 deep/data',
  `course_title` varchar(100) DEFAULT NULL COMMENT '课程标题，用于匹配 ai_courses.title',
  `course_id` int DEFAULT '0' COMMENT '关联 ai_courses.id，0 表示未匹配到课程',
  `task_index` int NOT NULL DEFAULT '0' COMMENT '题目序号，从 0 开始',
  `task_title` varchar(200) DEFAULT NULL COMMENT '题目名称',
  `language` varchar(20) DEFAULT 'Python' COMMENT '编程语言',
  `code` mediumtext COMMENT '学生本次提交的代码',
  `passed` int DEFAULT '0' COMMENT '通过的测试数',
  `total` int DEFAULT '0' COMMENT '测试用例总数',
  `all_passed` tinyint DEFAULT '0' COMMENT '1=全部测试通过',
  `output` text COMMENT '运行输出（截断保存）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_student_time` (`student_id`,`created_at`),
  KEY `idx_student_course` (`student_id`,`course_key`,`task_index`),
  KEY `idx_course_time` (`course_id`,`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='在线编程练习提交记录';

-- 说明：
-- 1) 学生端每次点「运行代码」都会写入一条记录，便于教师回看练习过程；
-- 2) 题目全部测试通过时，会额外向 learning_records 写入一条
--    learn_type='programming'、score=100、topic=题目名称 的记录，
--    供「学习路径」与教师看板统计复用，无需额外建表；
-- 3) 该表为新增表，不影响任何既有表结构与数据。
