-- 2026-09-17 高中 AI 通识课扩充：新增 3 门课程（原 5 门 → 8 门）
-- 其他学段课程未做任何改动。
-- 说明：quiz_content / animation_content 留空，学生端首次进入「云笺小试」「动画讲解」时按需生成并回写。
-- 执行方式：mysql -uroot -p teacher_psych_system < 20260917_add_high_school_courses.sql

INSERT INTO `ai_courses`
  (`title`, `description`, `grade_level`, `category`, `difficulty`, `sort_order`, `suggested_questions`)
SELECT '自然语言处理入门', '分词、词向量与情感分析', 'high_school', '机器学习', 'hard', 6,
       '["机器怎么把一句话拆成词？","词向量是什么？","怎么判断一段评论是好评还是差评？"]'
WHERE NOT EXISTS (SELECT 1 FROM `ai_courses` WHERE `title` = '自然语言处理入门' AND `grade_level` = 'high_school');

INSERT INTO `ai_courses`
  (`title`, `description`, `grade_level`, `category`, `difficulty`, `sort_order`, `suggested_questions`)
SELECT '强化学习初步', '智能体、奖励机制与试错学习', 'high_school', '算法思维', 'hard', 7,
       '["强化学习和监督学习有什么不同？","奖励机制是怎么设计的？","为什么要让智能体不断试错？"]'
WHERE NOT EXISTS (SELECT 1 FROM `ai_courses` WHERE `title` = '强化学习初步' AND `grade_level` = 'high_school');

INSERT INTO `ai_courses`
  (`title`, `description`, `grade_level`, `category`, `difficulty`, `sort_order`, `suggested_questions`)
SELECT 'AI伦理与社会责任', '算法偏见、数据隐私与深度伪造识别', 'high_school', '伦理安全', 'medium', 8,
       '["算法偏见是怎么产生的？","怎么保护训练数据里的隐私？","如何识别深度伪造的音视频？"]'
WHERE NOT EXISTS (SELECT 1 FROM `ai_courses` WHERE `title` = 'AI伦理与社会责任' AND `grade_level` = 'high_school');

-- 校验：高中课程应为 8 门，其余学段不变
-- SELECT grade_level, COUNT(*) FROM ai_courses GROUP BY grade_level;
