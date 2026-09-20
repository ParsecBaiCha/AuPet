-- 云笺小试答题进度暂存表
-- 进度存后端，学生换设备/换浏览器登录也能接着做；前端 localStorage 仅作离线兜底。
-- 同一学生只保留最新一份暂存，重复提交按主键 student_id 覆盖。
CREATE TABLE IF NOT EXISTS quiz_progress (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id INT NOT NULL DEFAULT 0,
  topic VARCHAR(100) NOT NULL DEFAULT '',
  payload MEDIUMTEXT NOT NULL,
  saved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY student_only (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
