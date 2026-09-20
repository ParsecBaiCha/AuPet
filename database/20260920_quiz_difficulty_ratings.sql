-- 学生自评题目难度表：用于收集「云笺小试」难题反馈，并同步到教师干预页
CREATE TABLE IF NOT EXISTS quiz_difficulty_ratings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  topic VARCHAR(200) NOT NULL DEFAULT '',
  question VARCHAR(500) NOT NULL DEFAULT '',
  stars INT NOT NULL,
  tags VARCHAR(500) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY student_time (student_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
