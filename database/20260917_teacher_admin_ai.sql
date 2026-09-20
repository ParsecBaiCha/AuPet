-- 2026-09-17 AI 研习配套：教师端与管理员端表结构变更
-- 与 backend/app.py 中「AI 研习配套接口」一节配合使用。
-- 幂等：可重复执行；已存在的列、索引、表会跳过。
-- 执行：mysql -uroot -p teacher_psych_system < 20260917_teacher_admin_ai.sql

-- 1. chat_history：对话需要按关键词类型与处理状态筛选
ALTER TABLE `chat_history`
  ADD COLUMN `flag_type` varchar(20) NULL COMMENT '关键词命中类型: mood/bully/study/other',
  ADD COLUMN `handled` tinyint(1) NOT NULL DEFAULT 0 COMMENT '教师是否已处理',
  ADD COLUMN `handled_by` int NULL COMMENT '处理教师ID',
  ADD COLUMN `handled_at` datetime NULL COMMENT '处理时间',
  ADD KEY `idx_handled_time` (`handled`, `created_at`);

-- 2. learning_records：看板按课程 + 时间范围统计
ALTER TABLE `learning_records` ADD KEY `idx_course_time` (`course_id`, `created_at`);

-- 3. ai_courses：上下架状态 + 照片绘本目录名（替代"目录名必须等于课程标题"的隐性约定）
ALTER TABLE `ai_courses`
  ADD COLUMN `status` varchar(10) NOT NULL DEFAULT 'published' COMMENT 'published/archived',
  ADD COLUMN `book_dir` varchar(120) NULL COMMENT '照片绘本目录名，默认同课程标题';

UPDATE `ai_courses` SET `book_dir` = `title` WHERE `book_dir` IS NULL OR `book_dir` = '';

-- 4. 内容审核记录
CREATE TABLE IF NOT EXISTS `ai_content_reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `object_type` varchar(20) NOT NULL COMMENT 'chat=学生对话 / material=教师资料',
  `object_id` int NOT NULL COMMENT '被审对象ID',
  `student_id` int DEFAULT NULL COMMENT '涉及学生',
  `reviewer_id` int NOT NULL COMMENT '审核人ID',
  `result` varchar(20) NOT NULL COMMENT 'approved/rejected/removed',
  `remark` varchar(255) DEFAULT NULL COMMENT '驳回原因等',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_object` (`object_type`, `object_id`),
  KEY `idx_reviewer` (`reviewer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI 内容审核记录';

-- 5. 教师查看学生对话的操作留痕
CREATE TABLE IF NOT EXISTS `teacher_ai_audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` int NOT NULL COMMENT '操作教师',
  `student_id` int DEFAULT NULL COMMENT '涉及学生',
  `action` varchar(40) NOT NULL COMMENT 'view_chat/convert_focus/ignore_chat',
  `chat_id` int DEFAULT NULL COMMENT '相关对话ID',
  `detail` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_teacher_time` (`teacher_id`, `created_at`),
  KEY `idx_student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='教师查看学生对话的操作留痕';

-- 校验：高中课程 8 门、各表已有新列
-- SELECT grade_level, COUNT(*) FROM ai_courses GROUP BY grade_level;
-- SHOW COLUMNS FROM chat_history;
