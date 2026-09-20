# -*- coding: utf-8 -*-
"""按照新的课程结构更新 ai_courses 表。
运行方式: python update_courses.py
"""
from app import get_db, query, execute

# 每个学段的完整课程结构
# 格式: (grade_level, [(category, [(title, description, difficulty), ...]), ...])

NEW_COURSES = {
    # ===== 小学低年级（1-3年级）=====
    'lower_primary': [
        ('AI基础', [
            ('什么是人工智能', '了解AI是什么，生活中有哪些AI', 'easy'),
            ('计算机是怎么思考的', '用生活比喻理解计算机的工作方式', 'easy'),
            ('和AI做朋友', '学习如何与AI对话，培养提问能力', 'easy'),
            ('创意天地', '与AI的创意作品-故事，绘画', 'easy'),
            ('发现生活中的AI', '发现生活中的AI', 'easy'),
            ('AI会画画吗？', '看看AI能画出什么，感受AI的创造力', 'easy'),
            ('AI怎么认出小猫小狗？', '从图片小游戏里理解"特征"是什么', 'easy'),
        ]),
        ('编程入门', [
            ('简单的指令', '理解什么是指令，学会给计算机下命令', 'easy'),
            ('顺序执行', '让计算机按步骤完成任务', 'easy'),
            ('条件判断', '让计算机根据条件做选择', 'easy'),
            ('找bug小侦探', '找出错误的指令，培养调试思维', 'easy'),
        ]),
    ],

    # ===== 小学高年级（4-6年级）=====
    'upper_primary': [
        ('AI基础', [
            ('机器学习是什么', '了解机器学习的基本概念和用途', 'easy'),
            ('AI如何学会分类', '从例子中发现特征，学习规律，再进行分类', 'easy'),
            ('让AI学会区分猫和狗', '通过图片训练，观察AI如何学习和分类', 'medium'),
            ('设计我的AI学习助手', '围绕校园等主题，设计有明确功能的AI', 'medium'),
            ('人机协作初体验', '借助AI完成学习任务，学习人与AI如何分工', 'medium'),
        ]),
        ('编程入门', [
            ('Scratch编程入门', '用图形化编程理解程序逻辑', 'easy'),
            ('条件判断', '学习if-else条件语句', 'medium'),
            ('循环结构', '理解for循环和while循环', 'medium'),
        ]),
        ('算法思维', [
            ('排序算法', '理解冒泡排序等简单算法', 'medium'),
        ]),
        ('伦理安全', [
            ('AI能做什么和不能做什么', '认识AI的能力边界', 'easy'),
        ]),
    ],

    # ===== 初中 =====
    'middle_school': [
        ('编程入门', [
            ('Python编程基础', '变量、数据类型、基本运算', 'medium'),
            ('基本数据结构', '理解列表和字典', 'medium'),
        ]),
        ('算法思维', [
            ('算法基础', '理解算法的基本概念和解决问题的方法', 'medium'),
            ('数据进阶', '数据清洗和数据的可视化', 'medium'),
            ('二分查找算法', '理解二分查找的原理和实现', 'medium'),
        ]),
        ('机器学习', [
            ('神经网络入门', '了解神经元和简单的网络结构', 'hard'),
            ('数据与AI的关系', '理解数据如何训练AI模型', 'medium'),
            ('机器学习实践', '制作成绩模型预测，体验简单回归任务', 'hard'),
        ]),
        ('伦理安全', [
            ('AI伦理与隐私', '讨论AI使用中的道德问题', 'medium'),
        ]),
        ('生成式AI', [
            ('生成式AI基础', '了解大语言模型的基本原理，认识AI幻觉与提示词', 'medium'),
            ('提示词基础', '学习通过清晰指令与AI进行有效交流', 'medium'),
        ]),
    ],

    # ===== 高中（只调换AI基础和机器学习顺序：机器学习在前）=====
    'high_school': [
        ('机器学习', [
            ('机器学习算法', '线性回归、决策树、KNN等', 'hard'),
            ('深度学习基础', '了解CNN、RNN等网络结构', 'hard'),
            ('自然语言处理入门', '分词、词向量与情感分析', 'hard'),
        ]),
        ('AI基础', [
            ('智能体基础', 'Agent、工具调用、多步骤任务执行', 'hard'),
            ('AI项目实践', '用机器学习解决实际问题', 'hard'),
        ]),
        ('编程入门', [
            ('Python数据分析', 'Pandas、NumPy基础', 'medium'),
        ]),
        ('算法思维', [
            ('排序算法进阶', '快速排序、归并排序的复杂度分析', 'hard'),
            ('强化学习初步', '智能体、奖励机制与试错学习', 'hard'),
        ]),
        ('伦理安全', [
            ('AI伦理与社会责任', 'AI伦理与社会责任', 'medium'),
        ]),
    ],
}


def main():
    conn = get_db()
    try:
        cur = conn.cursor()

        total_added = 0
        total_updated = 0

        for grade_level, categories in NEW_COURSES.items():
            sort_order = 0
            for category, courses in categories:
                for title, description, difficulty in courses:
                    sort_order += 1
                    # 检查是否已存在（同同学段 + 同标题）
                    cur.execute(
                        'SELECT id, sort_order FROM ai_courses WHERE title=%s AND grade_level=%s LIMIT 1',
                        (title, grade_level),
                    )
                    row = cur.fetchone()
                    if row:
                        # 更新分类、描述、难度、排序
                        cur.execute(
                            'UPDATE ai_courses SET category=%s, description=%s, difficulty=%s, sort_order=%s WHERE id=%s',
                            (category, description, difficulty, sort_order, row['id']),
                        )
                        total_updated += 1
                    else:
                        # 新增
                        cur.execute(
                            'INSERT INTO ai_courses (title, description, category, difficulty, grade_level, sort_order) '
                            'VALUES (%s, %s, %s, %s, %s, %s)',
                            (title, description, category, difficulty, grade_level, sort_order),
                        )
                        total_added += 1

        conn.commit()
        print(f'课程同步完成：新增 {total_added} 门，更新 {total_updated} 门。')

        # 打印最终结果
        print('\n===== 最终课程结构 =====')
        for grade_level, categories in NEW_COURSES.items():
            print(f'\n[{grade_level}]')
            for category, courses in categories:
                print(f'  {category}:')
                for title, desc, diff in courses:
                    print(f'    - {title} ({diff})')

    finally:
        conn.close()


if __name__ == '__main__':
    main()
