-- 萌宠智伴：低年级 / 高年级页面与测试账号初始化
-- 在 MySQL 的 teacher_psych_system 数据库中执行一次即可；重复执行不会重复创建账号。

USE teacher_psych_system;

-- grade_level 列已存在，无需 ALTER TABLE。如需新建请取消注释下行：
-- ALTER TABLE students ADD COLUMN grade_level varchar(30) NULL COMMENT 'AI 学习阶段';

INSERT INTO classes (name, grade, room, total_points, student_count, avg_points, psychology_status, status)
SELECT '高一1班', '高一', 'A101', 0, 1, 0, '良好', 'normal'
WHERE NOT EXISTS (SELECT 1 FROM classes WHERE name = '高一1班');

INSERT INTO students
  (name, student_no, password, class_id, gender, avatar, email, points, task_completion_rate, mood_index, mood_status, personality, grade_level)
SELECT
  '林知远', '20260101', MD5('123456'), c.id, 'male', '/images/avatars/boy1.jpg',
  'linzhiyuan@school.com', 1260, 72, 5, '良好', '自律、善于思考，喜欢探索人工智能与科学问题', 'high_school'
FROM classes c
WHERE c.name = '高一1班'
  AND NOT EXISTS (SELECT 1 FROM students WHERE student_no = '20260101');

-- 已有的张小明账号对应一年级；给其补上低年级 AI 学习阶段。
UPDATE students SET grade_level = 'lower_primary'
WHERE student_no = '20250101';
