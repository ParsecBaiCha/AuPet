# -*- coding: utf-8 -*-
"""补齐 AI 通识课所需数据库字段与缺失的初高中课程。

运行方式: python setup_ai_learning.py
脚本可重复运行：只增加缺失字段和不存在的课程，不覆盖已有小学课程。
"""
from app import get_db


REQUIRED_COLUMNS = {
    'ai_courses': {
        'quiz_content': 'LONGTEXT NULL',
        'book_content': 'LONGTEXT NULL',
    },
    'picture_books': {
        'is_favorite': 'TINYINT(1) NOT NULL DEFAULT 0',
    },
}

MISSING_GRADE_COURSES = [
    ('机器学习原理', '监督与无监督学习', '机器学习', 'medium', 'middle_school', 1),
    ('Python编程', '变量、循环、函数', '编程实践', 'medium', 'middle_school', 2),
    ('排序算法', '冒泡、选择、插入排序', '算法思维', 'hard', 'middle_school', 3),
    ('神经网络基础', '认识神经元和层', '深度学习', 'hard', 'middle_school', 4),
    ('深度学习', 'CNN与RNN原理', '深度学习', 'hard', 'high_school', 1),
    ('数据科学', '数据处理与可视化', '数据科学', 'medium', 'high_school', 2),
    ('AI伦理', '人工智能的边界与责任', 'AI伦理', 'medium', 'high_school', 3),
    ('项目实战', '构建简单AI应用', '项目实践', 'hard', 'high_school', 4),
]


def main():
    conn = get_db()
    try:
        cur = conn.cursor()
        added_columns = []
        for table, columns in REQUIRED_COLUMNS.items():
            cur.execute(f'SHOW COLUMNS FROM `{table}`')
            existing = {row['Field'] for row in cur.fetchall()}
            for column, definition in columns.items():
                if column not in existing:
                    cur.execute(f'ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}')
                    added_columns.append(f'{table}.{column}')

        added_courses = 0
        for course in MISSING_GRADE_COURSES:
            title, description, category, difficulty, grade_level, sort_order = course
            cur.execute(
                'SELECT id FROM ai_courses WHERE title=%s AND grade_level=%s LIMIT 1',
                (title, grade_level),
            )
            if not cur.fetchone():
                cur.execute(
                    'INSERT INTO ai_courses '
                    '(title,description,category,difficulty,grade_level,sort_order) '
                    'VALUES(%s,%s,%s,%s,%s,%s)',
                    course,
                )
                added_courses += 1

        conn.commit()
        print(f'数据库同步完成：新增字段 {len(added_columns)} 个，新增课程 {added_courses} 门。')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
