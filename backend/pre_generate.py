# -*- coding: utf-8 -*-
"""预生成脚本：为所有 AI 通识课程预生成测试题与绘本，写入 ai_courses 缓存字段。

运行方式: python pre_generate.py [--force] [--only quiz|book]
已生成的会自动跳过，可重复运行补全失败项；--force 强制重新生成全部，--only 只处理指定类型。
"""
import sys
import time
import json
import pymysql

sys.path.insert(0, '.')
import llm_service

DB_CONFIG = {
    'host': '127.0.0.1', 'user': 'root', 'password': '092236',
    'database': 'teacher_psych_system', 'port': 3306,
    'charset': 'utf8mb4', 'cursorclass': pymysql.cursors.DictCursor,
}

QUIZ_GROUPS = 3      # 每门课生成几组题
FORCE = '--force' in sys.argv
ONLY = None
if '--only' in sys.argv:
    idx = sys.argv.index('--only')
    if idx + 1 < len(sys.argv):
        ONLY = sys.argv[idx + 1]


def get_db():
    return pymysql.connect(**DB_CONFIG)


def has_content(cur, cid, col):
    cur.execute(f'SELECT {col} FROM ai_courses WHERE id=%s', (cid,))
    r = cur.fetchone()
    return bool(r and r[col])


def main():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, grade_level FROM ai_courses ORDER BY grade_level, sort_order')
    courses = cur.fetchall()
    total = len(courses)
    print(f'共 {total} 门课程，每门生成 {QUIZ_GROUPS} 组题 + 1 本绘本')

    quiz_ok = book_ok = 0
    quiz_fail = book_fail = 0
    for i, c in enumerate(courses, 1):
        cid, title, grade = c['id'], c['title'], c['grade_level']
        print(f'[{i}/{total}] {title} ({grade}) ...', flush=True)

        # ---- 测试题 ----
        if ONLY and ONLY != 'quiz':
            print('    quiz skipped (--only)', flush=True)
        else:
            need_quiz = FORCE or not has_content(cur, cid, 'quiz_content')
            if need_quiz:
                groups = []
                for g in range(QUIZ_GROUPS):
                    qs = llm_service.generate_quiz(title, grade, 3)
                    if qs and '生成失败' not in qs[0].get('question', ''):
                        groups.append(qs)
                        print(f'    quiz group {g + 1} ok', flush=True)
                    else:
                        print(f'    quiz group {g + 1} FAILED', flush=True)
                    time.sleep(0.8)
                if groups:
                    cur.execute('UPDATE ai_courses SET quiz_content=%s WHERE id=%s',
                                (json.dumps(groups, ensure_ascii=False), cid))
                    conn.commit()
                    quiz_ok += 1
                else:
                    quiz_fail += 1
            else:
                print('    quiz already cached, skip', flush=True)
                quiz_ok += 1

        # ---- 绘本 ----
        if ONLY and ONLY != 'book':
            print('    book skipped (--only)', flush=True)
        else:
            need_book = FORCE or not has_content(cur, cid, 'book_content')
            if need_book:
                book = llm_service.generate_picture_book(title, grade)
                if book and '生成失败' not in str(book.get('pages', [{}])[0].get('text', '')):
                    cur.execute('UPDATE ai_courses SET book_content=%s WHERE id=%s',
                                (json.dumps(book, ensure_ascii=False), cid))
                    conn.commit()
                    book_ok += 1
                    print(f'    book ok ({len(book.get("pages", []))} pages)', flush=True)
                else:
                    book_fail += 1
                    print('    book FAILED', flush=True)
                time.sleep(0.8)
            else:
                print('    book already cached, skip', flush=True)
                book_ok += 1

        print('', flush=True)

    cur.close()
    conn.close()
    print('=' * 50)
    print(f'完成！测试题: {quiz_ok} 成功 / {quiz_fail} 失败；绘本: {book_ok} 成功 / {book_fail} 失败')
    if quiz_fail or book_fail:
        print('有失败项，可重跑本脚本自动重试（已成功的会跳过）')


if __name__ == '__main__':
    main()
