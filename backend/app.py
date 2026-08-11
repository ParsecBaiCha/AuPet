# -*- coding: utf-8 -*-
"""萌宠智伴 - Flask 后端服务
连接 MySQL 数据库 teacher_psych_system，为 Vue3 前端提供全部 API。
启动: python app.py  ->  http://localhost:8000
"""
import hashlib
import json
import random
import datetime
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import llm_service

app = Flask(__name__)
CORS(app)

# ============ 数据库配置 ============
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '092236',
    'database': 'teacher_psych_system',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_db():
    return pymysql.connect(**DB_CONFIG)


def query(sql, args=(), one=False):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        rows = cur.fetchall()
        return rows[0] if one and rows else (None if one else rows)
    finally:
        conn.close()


def execute(sql, args=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def execute_return_id(sql, args=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def ok(data=None, message='操作成功'):
    return jsonify({'success': True, 'data': data, 'message': message})


def now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# ============ 简易 token 校验 ============
def get_login_user():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth[7:]
    try:
        parts = token.split('_')
        if len(parts) >= 3:
            return {'role': parts[1], 'id': int(parts[2]), 'username': parts[0]}
    except Exception:
        pass
    return None


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        u = get_login_user()
        if not u:
            return jsonify({'success': False, 'message': '未登录'}), 401
        request.login_user = u
        return f(*a, **kw)
    return wrapper


# ================================================================
#  认证模块
# ================================================================
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'message': '请输入用户名和密码'}), 400

    # ---- admin 特殊账号 ----
    if username == 'admin':
        if password in ('admin', '092236', '123456'):
            token = f'admin_admin_0'
            return jsonify({
                'token': token,
                'user': {'id': 0, 'username': 'admin', 'role': 'admin',
                         'name': '系统管理员', 'avatar': ''}
            })
        return jsonify({'message': '管理员密码错误'}), 400

    # ---- 教师登录(工号,明文密码) ----
    teacher = query(
        'SELECT * FROM teachers WHERE employee_id=%s', (username,), one=True)
    if teacher:
        if password == teacher['password']:
            token = f"{teacher['employee_id']}_teacher_{teacher['id']}"
            return jsonify({
                'token': token,
                'user': {'id': teacher['id'], 'username': teacher['employee_id'],
                         'role': teacher['role'] or 'teacher',
                         'name': teacher['name'],
                         'avatar': teacher.get('avatar') or ''}
            })
        return jsonify({'message': '密码错误'}), 400

    # ---- 学生登录(学号,MD5 密码) ----
    student = query(
        'SELECT * FROM students WHERE student_no=%s', (username,), one=True)
    if student:
        if md5(password) == student['password']:
            token = f"{student['student_no']}_student_{student['id']}"
            return jsonify({
                'token': token,
                'user': {'id': student['id'], 'username': student['student_no'],
                         'role': 'student', 'name': student['name'],
                         'avatar': student.get('avatar') or ''}
            })
        return jsonify({'message': '密码错误'}), 400

    return jsonify({'message': '用户不存在'}), 400


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    name = data.get('name') or username
    password = data.get('password') or '123456'
    role = data.get('role') or 'student'
    email = data.get('email')
    if role == 'student':
        execute(
            'INSERT INTO students(name,student_no,password,class_id,gender,points,mood_status) '
            'VALUES(%s,%s,%s,NULL,NULL,0,%s)',
            (name, username, md5(password), '良好'))
    elif role == 'teacher':
        execute(
            'INSERT INTO teachers(name,employee_id,password,level,role) '
            'VALUES(%s,%s,%s,%s,%s)',
            (name, username, password, '任课教师', 'teacher'))
    return ok(message='注册成功')


@app.route('/api/auth/me', methods=['GET'])
@login_required
def auth_me():
    u = request.login_user
    return jsonify({'id': u['id'], 'username': u['username'],
                    'role': u['role'], 'name': u.get('name', u['username'])})


# ================================================================
#  学生端接口
# ================================================================
@app.route('/api/student/dashboard', methods=['GET'])
@login_required
def student_dashboard():
    sid = request.login_user['id']
    s = query('SELECT s.*, c.name class_name FROM students s '
              'LEFT JOIN classes c ON s.class_id=c.id WHERE s.id=%s', (sid,), one=True)
    sp = query('SELECT sp.*, p.image_url pet_img, p.type pet_type FROM student_pets sp '
               'LEFT JOIN pets p ON sp.pet_id=p.id WHERE sp.student_id=%s AND sp.is_active=1',
               (sid,), one=True)
    rank = query('SELECT COUNT(*)+1 r FROM students WHERE points>(SELECT points FROM students WHERE id=%s)',
                 (sid,), one=True)
    classmates = query(
        'SELECT s.id, s.name student_name, s.points, s.task_completion_rate progress, '
        'sp.pet_level level, p.image_url pet_image, sp.pet_name '
        'FROM students s LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 '
        'LEFT JOIN pets p ON sp.pet_id=p.id '
        'WHERE s.class_id=%s ORDER BY s.points DESC LIMIT 8', (s['class_id'],))
    return jsonify({
        'studentName': s['name'], 'avatar': s.get('avatar') or '/images/avatars/dz.jpg',
        'className': s.get('class_name') or '未分班',
        'petName': sp['pet_name'] if sp else '球球',
        'petImage': sp['pet_img'] if sp else '/images/pets/dog1.jpg',
        'points': s['points'], 'rank': rank['r'] if rank else 1,
        'completedTasks': s.get('task_completion_rate', 0),
        'classPets': [{'id': c['id'], 'studentName': c['student_name'],
                       'petName': c['pet_name'] or '小宠', 'petImage': c['pet_image'] or '/images/pets/dog1.jpg',
                       'points': c['points'], 'level': c['level'] or 'B',
                       'progress': c['progress'] or 0} for c in classmates]
    })


@app.route('/api/student/mypet', methods=['GET'])
@login_required
def student_mypet():
    sid = request.login_user['id']
    s = query('SELECT s.*, c.name class_name FROM students s '
              'LEFT JOIN classes c ON s.class_id=c.id WHERE s.id=%s', (sid,), one=True)
    sp = query('SELECT sp.*, p.image_url pet_img FROM student_pets sp '
               'JOIN pets p ON sp.pet_id=p.id WHERE sp.student_id=%s AND sp.is_active=1', (sid,), one=True)
    rank = query('SELECT COUNT(*)+1 r FROM students WHERE points>(SELECT points FROM students WHERE id=%s)',
                 (sid,), one=True)
    goods = query('SELECT id,name,image_url image,points_price price FROM point_goods WHERE is_active=1')
    return jsonify({
        'pet': {'name': sp['pet_name'] if sp else '球球',
                'type': sp['pet_img'] if sp else '/images/pets/dog1.jpg',
                'level': (sp['pet_level'] if sp else 'B'),
                'exp': sp['pet_exp'] if sp else 750, 'maxExp': 1000,
                'health': 95, 'hunger': 80, 'happiness': 90,
                'adoptDate': str(sp['obtained_at'])[:10] if sp else '2026-01-15'},
        'student': {'name': s['name'], 'avatar': s.get('avatar') or '/images/avatars/dz.jpg',
                    'className': s.get('class_name') or '未分班', 'points': s['points'],
                    'completedTasks': s.get('task_completion_rate', 0),
                    'rank': rank['r'] if rank else 1},
        'shopItems': [{'id': g['id'], 'name': g['name'], 'image': g['image'],
                       'price': g['price'], 'exp': 20} for g in goods]
    })


@app.route('/api/student/shop', methods=['GET'])
@login_required
def student_shop():
    goods = query('SELECT id,name,image_url image,points_price price FROM point_goods WHERE is_active=1')
    return jsonify([{'id': g['id'], 'name': g['name'], 'image': g['image'],
                     'price': g['price'], 'exp': 20} for g in goods])


@app.route('/api/student/shop/buy', methods=['POST'])
@login_required
def student_shop_buy():
    data = request.get_json(silent=True) or {}
    sid = request.login_user['id']
    g = query('SELECT * FROM point_goods WHERE id=%s', (data.get('itemId'),), one=True)
    if not g:
        return jsonify({'success': False, 'message': '商品不存在'}), 400
    execute('UPDATE students SET points=points-%s WHERE id=%s AND points>=%s',
            (g['points_price'], sid, g['points_price']))
    return ok(message='购买成功')


@app.route('/api/student/chat', methods=['GET'])
@login_required
def student_chat_get():
    sid = request.login_user['id']
    sp = query('SELECT pet_name FROM student_pets WHERE student_id=%s AND is_active=1', (sid,), one=True)
    pet_name = sp['pet_name'] if sp else 'AI学习伙伴'
    rows = query('SELECT id, role, content, DATE_FORMAT(created_at,"%%H:%%i") t FROM chat_history '
                 'WHERE student_id=%s ORDER BY id DESC LIMIT 30', (sid,))
    if rows:
        return jsonify([{'id': r['id'], 'type': r['role'], 'content': r['content'], 'time': r['t']}
                        for r in reversed(rows)])
    # 没有历史时返回欢迎消息
    return jsonify([
        {'id': 0, 'type': 'assistant', 'content': f'你好呀！我是{pet_name}，你的AI学习伙伴！\n想了解人工智能的什么知识呢？可以问我任何问题哦~', 'time': '09:00'},
    ])


@app.route('/api/student/chat', methods=['POST'])
@login_required
def student_chat_post():
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'message': '消息不能为空'}), 400

    # 获取学生年级和宠物名
    s = query('SELECT grade_level FROM students WHERE id=%s', (sid,), one=True)
    sp = query('SELECT pet_name FROM student_pets WHERE student_id=%s AND is_active=1', (sid,), one=True)
    grade_level = (s['grade_level'] if s and s['grade_level'] else 'upper_primary') or 'upper_primary'
    pet_name = sp['pet_name'] if sp else '球球'

    # 获取最近聊天历史
    history_rows = query(
        'SELECT role, content FROM chat_history WHERE student_id=%s ORDER BY id DESC LIMIT 6',
        (sid,))
    history = [{'role': h['role'], 'content': h['content']} for h in reversed(history_rows)] if history_rows else None

    # 保存用户消息
    user_msg_id = execute_return_id(
        'INSERT INTO chat_history(student_id,role,content,grade_level) VALUES(%s,%s,%s,%s)',
        (sid, 'user', message, grade_level))

    # 调用大模型
    reply = llm_service.chat(message, grade_level, history, pet_name)
    t = datetime.datetime.now().strftime('%H:%M')

    # 保存AI回复
    ai_msg_id = execute_return_id(
        'INSERT INTO chat_history(student_id,role,content,grade_level) VALUES(%s,%s,%s,%s)',
        (sid, 'assistant', reply, grade_level))

    return jsonify({'reply': reply, 'time': t, 'pet_name': pet_name,
                    'userMsgId': user_msg_id, 'aiMsgId': ai_msg_id})


@app.route('/api/student/diaries', methods=['GET'])
@login_required
def student_diaries_get():
    sid = request.login_user['id']
    recs = query('SELECT * FROM point_records WHERE student_id=%s ORDER BY created_at DESC LIMIT 7', (sid,))
    point_history = [{'date': str(r['created_at'])[:10], 'points': r['points']} for r in recs]
    return jsonify({
        'moodEntries': {str(r['created_at'])[:10]: {'date': str(r['created_at'])[:10],
                     'mood': '/images/Mood_Diary/happy.jpg', 'note': r['reason']} for r in recs},
        'goals': [{'id': 1, 'title': '每天背诵20个单词', 'completed': True, 'deadline': '2026-04-30'},
                  {'id': 2, 'title': '完成本周周记', 'completed': False, 'deadline': '2026-05-05'}],
        'achievements': [{'id': 1, 'title': '任务达人', 'icon': '/images/Student_Icons/TaskMaster.jpg',
                          'description': '完成10个任务', 'unlocked': True}],
        'pointHistory': point_history
    })


@app.route('/api/student/diaries', methods=['POST'])
@login_required
def student_diaries_post():
    return ok(message='记录成功')


@app.route('/api/student/emotions', methods=['GET'])
@login_required
def student_emotions_get():
    return jsonify({'moodEntries': {}})


@app.route('/api/student/emotions', methods=['POST'])
@login_required
def student_emotions_post():
    return ok(message='记录成功')


@app.route('/api/student/tasks', methods=['GET'])
@login_required
def student_tasks_get():
    sid = request.login_user['id']
    s = query('SELECT class_id FROM students WHERE id=%s', (sid,), one=True)
    cid = s['class_id'] if s else None
    tasks = query('SELECT t.*, tea.name teacher_name FROM tasks t '
                  'LEFT JOIN teachers tea ON t.teacher_id=tea.id '
                  'WHERE t.class_id=%s ORDER BY t.id', (cid,)) if cid else []
    daily, weekly = [], []
    for i, t in enumerate(tasks):
        item = {'id': t['id'], 'title': t['name'], 'description': t['name'],
                'points': t['points'] or 0, 'completed': i % 3 == 0,
                'category': '语文', 'deadline': str(t['deadline']) if t['deadline'] else '今日 18:00',
                'teacher': t['teacher_name'] or '王老师'}
        (daily if i % 2 == 0 else weekly).append(item)
    return jsonify({'dailyTasks': daily, 'weeklyTasks': weekly})


@app.route('/api/student/tasks/<int:tid>', methods=['PUT'])
@login_required
def student_tasks_update(tid):
    return ok(message='任务已更新')


@app.route('/api/student/classmates', methods=['GET'])
@login_required
def student_classmates():
    sid = request.login_user['id']
    s = query('SELECT class_id FROM students WHERE id=%s', (sid,), one=True)
    cid = s['class_id'] if s else None
    rows = query(
        'SELECT s.id, s.name student_name, s.points, s.task_completion_rate progress, '
        'sp.pet_level level, p.image_url pet_image, sp.pet_name '
        'FROM students s LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 '
        'LEFT JOIN pets p ON sp.pet_id=p.id WHERE s.class_id=%s ORDER BY s.points DESC', (cid,)) if cid else []
    return jsonify([{'id': r['id'], 'studentName': r['student_name'],
                     'petName': r['pet_name'] or '小宠', 'petImage': r['pet_image'] or '/images/pets/dog1.jpg',
                     'points': r['points'], 'level': r['level'] or 'B', 'progress': r['progress'] or 0} for r in rows])


@app.route('/api/student/class-stats', methods=['GET'])
@login_required
def student_class_stats():
    sid = request.login_user['id']
    s = query('SELECT class_id FROM students WHERE id=%s', (sid,), one=True)
    cid = s['class_id'] if s else None
    c = query('SELECT * FROM classes WHERE id=%s', (cid,), one=True) if cid else None
    return jsonify({'className': c['name'] if c else '', 'totalStudents': c['student_count'] if c else 0,
                    'avgPoints': float(c['avg_points']) if c else 0, 'totalPoints': c['total_points'] if c else 0})


@app.route('/api/student/pet-shop', methods=['GET'])
@login_required
def student_pet_shop():
    pets = query('SELECT id, type name, image_url image FROM pets')
    return jsonify([{'id': p['id'], 'name': p['name'], 'image': p['image'], 'price': 500} for p in pets])


@app.route('/api/student/pet-shop/buy', methods=['POST'])
@login_required
def student_pet_shop_buy():
    data = request.get_json(silent=True) or {}
    sid = request.login_user['id']
    execute('INSERT INTO student_pets(student_id,pet_id,pet_name,pet_exp,pet_level,is_active) '
            'VALUES(%s,%s,%s,0,%s,0)', (sid, data.get('petId'), '新宠物', 'B'))
    return ok(message='购买成功')


@app.route('/api/student/points', methods=['GET'])
@login_required
def student_points():
    sid = request.login_user['id']
    recs = query('SELECT * FROM point_records WHERE student_id=%s ORDER BY created_at DESC LIMIT 7', (sid,))
    return jsonify([{'date': str(r['created_at'])[:10], 'points': r['points']} for r in recs])


# ================================================================
#  教师端接口
# ================================================================
def _teacher_classes(tid):
    t = query('SELECT class_ids FROM teachers WHERE id=%s', (tid,), one=True)
    if not t or not t['class_ids']:
        return []
    try:
        return json.loads(t['class_ids']) if isinstance(t['class_ids'], str) else t['class_ids']
    except Exception:
        return []


@app.route('/api/teacher/dashboard', methods=['GET'])
@login_required
def teacher_dashboard():
    tid = request.login_user['id']
    cids = _teacher_classes(tid)
    placeholders = ','.join(['%s'] * len(cids)) if cids else '0'
    stu_cnt = query(f'SELECT COUNT(*) c FROM students WHERE class_id IN ({placeholders})', tuple(cids), one=True)
    classes = query(f'SELECT * FROM classes WHERE id IN ({placeholders})', tuple(cids)) if cids else []
    abnormal = query(f'SELECT a.*, s.name student_name, c.name class_name FROM abnormal_students a '
                     f'JOIN students s ON a.student_id=s.id JOIN classes c ON s.class_id=c.id '
                     f'WHERE a.teacher_id=%s ORDER BY a.id DESC LIMIT 5', (tid,))
    return jsonify({
        'stats': {'studentCount': stu_cnt['c'] if stu_cnt else 0, 'classCount': len(cids),
                  'todayTask': 5, 'noticeCount': 2},
        'abnormalStudents': [{'id': a['id'], 'name': a['student_name'], 'class': a['class_name'],
                              'type': a['abnormal_type'], 'date': str(a['detected_date'])} for a in abnormal],
        'weekTrend': [{'label': d, 'value': random.randint(60, 95)} for d in ['一', '二', '三', '四', '五', '六', '日']],
        'recentActivities': [{'name': '李小红 - 课堂积极发言', 'points': 5}],
        'schedule': [{'time': '08:00', 'title': '语文课 · 一年级1班', 'desc': '第1-2节'}],
        'classes': [{'id': c['id'], 'name': c['name'], 'studentCount': c['student_count'],
                     'attendence': 96, 'totalPoints': c['total_points']} for c in classes],
        'activities': [{'author': '系统', 'action': '发布了新公告', 'avatar': '', 'time': '2小时前'}]
    })


@app.route('/api/teacher/points', methods=['GET'])
@login_required
def teacher_points():
    tid = request.login_user['id']
    cids = _teacher_classes(tid)
    placeholders = ','.join(['%s'] * len(cids)) if cids else '0'
    rows = query(f'SELECT s.*, c.name class_name, sp.pet_level, gm.group_id, sg.id gid '
                 f'FROM students s LEFT JOIN classes c ON s.class_id=c.id '
                 f'LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 '
                 f'LEFT JOIN group_members gm ON gm.student_id=s.id '
                 f'LEFT JOIN study_groups sg ON sg.id=gm.group_id '
                 f'WHERE s.class_id IN ({placeholders}) ORDER BY s.points DESC', tuple(cids)) if cids else []
    return jsonify([{'id': r['id'], 'name': r['name'], 'class': r['class_name'],
                     'groupId': r['group_id'] or r['id'], 'groupName': '星光组' if r['group_id'] else '未分组',
                     'points': r['points'], 'status': 'active',
                     'petLevel': (r['pet_level'] or 'B') + '级',
                     'taskCompletionRate': r['task_completion_rate'] or 0,
                     'moodIndex': (r['mood_index'] or 3) * 20,
                     'personality': r['personality'] or ''} for r in rows])


@app.route('/api/teacher/points/records', methods=['GET'])
@login_required
def teacher_points_records():
    sid = request.args.get('studentId')
    rows = query('SELECT * FROM point_records WHERE student_id=%s ORDER BY created_at DESC LIMIT 10', (sid,)) if sid else []
    return jsonify([{'name': r['reason'], 'points': r['points'],
                     'time': str(r['created_at'])[:16]} for r in rows])


@app.route('/api/teacher/points/award', methods=['POST'])
@login_required
def teacher_points_award():
    data = request.get_json(silent=True) or {}
    tid = request.login_user['id']
    sid = data.get('studentId')
    pts = data.get('points', 0)
    reason = data.get('reason', '教师奖励')
    if sid:
        execute('UPDATE students SET points=points+%s WHERE id=%s', (pts, sid))
        execute('INSERT INTO point_records(student_id,teacher_id,points,reason,rule_id,type) '
                'VALUES(%s,%s,%s,%s,0,%s)', (sid, tid, pts, reason, 'add' if pts >= 0 else 'reduce'))
    return ok(message='操作成功')


@app.route('/api/teacher/points/rules', methods=['GET'])
@login_required
def teacher_points_rules():
    rows = query('SELECT * FROM point_rules ORDER BY id')
    return jsonify([{'id': r['id'], 'name': r['name'], 'points': r['points']} for r in rows])


@app.route('/api/teacher/points/rules', methods=['POST'])
@login_required
def teacher_points_rules_create():
    data = request.get_json(silent=True) or {}
    execute('INSERT INTO point_rules(name,points,category,is_active) VALUES(%s,%s,%s,1)',
            (data.get('name'), data.get('points', 0), 'add'))
    return ok(message='创建成功')


@app.route('/api/teacher/classes', methods=['GET'])
@login_required
def teacher_classes():
    tid = request.login_user['id']
    cids = _teacher_classes(tid)
    placeholders = ','.join(['%s'] * len(cids)) if cids else '0'
    rows = query(f'SELECT c.*, t.name teacher_name FROM classes c '
                 f'LEFT JOIN teachers t ON c.teacher_id=t.id WHERE c.id IN ({placeholders})', tuple(cids)) if cids else []
    return jsonify([{'id': r['id'], 'name': r['name'], 'grade': r['grade'],
                     'teacher': r['teacher_name'] or '', 'studentCount': r['student_count'],
                     'room': r['room'] or '', 'totalPoints': r['total_points'],
                     'avgPoints': float(r['avg_points']), 'psychologyStatus': r['psychology_status'],
                     'status': r['status']} for r in rows])


@app.route('/api/teacher/classes', methods=['POST'])
@login_required
def teacher_classes_create():
    data = request.get_json(silent=True) or {}
    tid = request.login_user['id']
    execute('INSERT INTO classes(name,grade,teacher_id,room) VALUES(%s,%s,%s,%s)',
            (data.get('name'), data.get('grade'), tid, data.get('room')))
    return ok(message='创建成功')


@app.route('/api/teacher/classes/import', methods=['POST'])
@login_required
def teacher_classes_import():
    return ok(message='导入成功')


@app.route('/api/teacher/classes/<int:cid>/students', methods=['GET'])
@login_required
def teacher_class_students(cid):
    rows = query('SELECT s.*, sp.pet_level FROM students s '
                 'LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 '
                 'WHERE s.class_id=%s ORDER BY s.points DESC', (cid,))
    return jsonify([{'name': r['name'], 'gender': r['gender'], 'points': r['points'],
                     'petLevel': r['pet_level'] or 'B', 'taskRate': r['task_completion_rate'] or 0,
                     'moodIndex': r['mood_index'] or 3, 'moodStatus': r['mood_status']} for r in rows])


@app.route('/api/teacher/students/<int:sid>', methods=['GET'])
@login_required
def teacher_student_detail(sid):
    r = query('SELECT s.*, c.name class_name, sp.pet_level, sp.pet_name, sp.pet_exp '
              'FROM students s LEFT JOIN classes c ON s.class_id=c.id '
              'LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 WHERE s.id=%s', (sid,), one=True)
    recs = query('SELECT * FROM point_records WHERE student_id=%s ORDER BY created_at DESC LIMIT 5', (sid,))
    return jsonify({'id': r['id'], 'name': r['name'], 'class': r['class_name'],
                    'groupName': '星光组', 'points': r['points'],
                    'petLevel': (r['pet_level'] or 'B') + '级',
                    'taskCompletionRate': r['task_completion_rate'] or 0,
                    'moodIndex': (r['mood_index'] or 3) * 20,
                    'personality': r['personality'] or '',
                    'records': [{'name': x['reason'], 'points': x['points'], 'time': str(x['created_at'])[:16]} for x in recs]})


@app.route('/api/teacher/interventions', methods=['GET'])
@login_required
def teacher_interventions():
    tid = request.login_user['id']
    rows = query('SELECT a.*, s.name student_name, c.name class_name, '
                 '(SELECT COUNT(*) FROM intervention_records ir WHERE ir.abnormal_id=a.id) icount '
                 'FROM abnormal_students a JOIN students s ON a.student_id=s.id '
                 'JOIN classes c ON s.class_id=c.id WHERE a.teacher_id=%s ORDER BY a.id DESC', (tid,))
    return jsonify([{'id': r['id'], 'name': r['student_name'], 'class': r['class_name'],
                     'abnormalType': r['abnormal_type'], 'detectedDate': str(r['detected_date']),
                     'severity': r['severity'], 'status': r['status'],
                     'interventionCount': r['icount']} for r in rows])


@app.route('/api/teacher/interventions/<int:aid>', methods=['GET'])
@login_required
def teacher_intervention_detail(aid):
    r = query('SELECT a.*, s.name student_name, c.name class_name FROM abnormal_students a '
              'JOIN students s ON a.student_id=s.id JOIN classes c ON s.class_id=c.id WHERE a.id=%s', (aid,), one=True)
    return jsonify({'id': r['id'], 'name': r['student_name'], 'class': r['class_name'],
                    'abnormalType': r['abnormal_type'], 'detectedDate': str(r['detected_date']),
                    'severity': r['severity'], 'status': r['status'], 'interventionCount': 0,
                    'description': r['description'] or '', 'suggestions': ['加强家校沟通', '增加集体活动']})


@app.route('/api/teacher/interventions', methods=['POST'])
@login_required
def teacher_interventions_create():
    data = request.get_json(silent=True) or {}
    tid = request.login_user['id']
    execute('INSERT INTO intervention_records(abnormal_id,teacher_id,title,content,record_date) '
            'VALUES(%s,%s,%s,%s,%s)', (data.get('studentId', 1), tid, data.get('goal', '干预记录'),
                                       data.get('goal', ''), datetime.date.today()))
    return ok(message='干预已创建')


@app.route('/api/teacher/group-roles', methods=['GET'])
@login_required
def teacher_group_roles():
    tid = request.login_user['id']
    cids = _teacher_classes(tid)
    placeholders = ','.join(['%s'] * len(cids)) if cids else '0'
    rows = query(f'SELECT s.id, s.name, c.name class_name, s.personality, '
                 f'(SELECT e.score FROM evaluations e WHERE e.student_id=s.id ORDER BY e.id DESC LIMIT 1) last_score, '
                 f'(SELECT e.created_at FROM evaluations e WHERE e.student_id=s.id ORDER BY e.id DESC LIMIT 1) last_time '
                 f'FROM students s JOIN classes c ON s.class_id=c.id '
                 f'WHERE s.class_id IN ({placeholders}) LIMIT 20', tuple(cids)) if cids else []
    return jsonify([{'id': r['id'], 'name': r['name'], 'class': r['class_name'],
                     'lastEvaluation': f"{r['last_score']}分" if r['last_score'] else '未评价',
                     'lastEvalTime': str(r['last_time'])[:10] if r['last_time'] else '',
                     'chatRate': random.randint(60, 90), 'positiveRate': random.randint(50, 80),
                     'negativeRate': random.randint(3, 15),
                     'aiTraits': ['情绪稳定', '任务执行力强']} for r in rows])


@app.route('/api/teacher/evaluations', methods=['POST'])
@login_required
def teacher_evaluations():
    data = request.get_json(silent=True) or {}
    tid = request.login_user['id']
    execute('INSERT INTO evaluations(student_id,teacher_id,score,tags,comment) VALUES(%s,%s,%s,%s,%s)',
            (data.get('studentId'), tid, data.get('score', 5),
             json.dumps(data.get('tags', []), ensure_ascii=False), data.get('comment', '')))
    return ok(message='评价已保存')


@app.route('/api/teacher/role-network', methods=['GET'])
@login_required
def teacher_role_network():
    tid = request.login_user['id']
    cids = _teacher_classes(tid)
    placeholders = ','.join(['%s'] * len(cids)) if cids else '0'
    students = query(f'SELECT id,name FROM students WHERE class_id IN ({placeholders}) LIMIT 12', tuple(cids)) if cids else []
    colors = ['#8985cf', '#f6d365', '#84fab0', '#ff9a9e', '#a18cd1', '#a6c0fe']
    agents = [{'id': s['id'], 'name': s['name'],
               'x': 100 + (i % 4) * 180 + random.randint(-30, 30),
               'y': 80 + (i // 4) * 160 + random.randint(-20, 20),
               'color': colors[i % len(colors)],
               'role': ['leader', 'active', 'quiet', 'helper'][i % 4]} for i, s in enumerate(students)]
    links = [{'source': students[i]['id'], 'target': students[j]['id'], 'strength': round(random.uniform(0.3, 0.9), 2)}
             for i in range(len(students)) for j in range(i + 1, min(i + 3, len(students)))] if len(students) > 1 else []
    return jsonify({'agents': agents, 'links': links, 'clusters': min(3, max(1, len(students) // 4))})


@app.route('/api/teacher/predictions', methods=['GET'])
@login_required
def teacher_predictions():
    tid = request.login_user['id']
    rows = query('SELECT * FROM predictions WHERE teacher_id=%s ORDER BY id DESC', (tid,))
    return jsonify([{'id': r['id'], 'title': r.get('scene') or '趋势预测',
                     'description': r.get('decision') or '', 'createdAt': str(r['created_at'])[:10]} for r in rows])


@app.route('/api/teacher/predictions', methods=['POST'])
@login_required
def teacher_predictions_create():
    data = request.get_json(silent=True) or {}
    tid = request.login_user['id']
    execute('INSERT INTO predictions(teacher_id,class_id,scene,decision,result) VALUES(%s,%s,%s,%s,%s)',
            (tid, 1, data.get('title', '预测'), data.get('description', ''), '{}'))
    return ok(message='预测已创建')


@app.route('/api/teacher/predictions/<int:pid>', methods=['GET'])
@login_required
def teacher_prediction_detail(pid):
    r = query('SELECT * FROM predictions WHERE id=%s', (pid,), one=True)
    return jsonify({'id': r['id'], 'title': r.get('scene') or '预测',
                    'description': r.get('decision') or '', 'createdAt': str(r['created_at'])[:10]})


@app.route('/api/teacher/forum', methods=['GET'])
@login_required
def teacher_forum():
    rows = query('SELECT p.*, f.name forum_name, f.type forum_type, '
                 'COALESCE(s.name, t.name) author_name, t.level author_level '
                 'FROM posts p JOIN forums f ON p.forum_id=f.id '
                 'LEFT JOIN students s ON p.author_id=s.id '
                 'LEFT JOIN teachers t ON p.author_id=t.id '
                 'WHERE p.review_status=%s ORDER BY p.is_top DESC, p.id DESC', ('approved',))
    return jsonify([{'id': r['id'], 'title': r['title'], 'content': r['content'],
                     'author': r['author_name'] or '匿名', 'avatar': '',
                     'forumId': r['forum_id'], 'forumName': r['forum_name'],
                     'createTime': str(r['created_at']).replace('T', ' ')[:16] if r['created_at'] else '',
                     'views': r['views'], 'replies': r['replies'], 'likes': r['likes'],
                     'top': bool(r['is_top']), 'level': r['author_level'] or '任课教师'} for r in rows])


@app.route('/api/teacher/forum', methods=['POST'])
@login_required
def teacher_forum_create():
    data = request.get_json(silent=True) or {}
    tid = request.login_user['id']
    execute('INSERT INTO posts(forum_id,author_id,title,content,review_status) VALUES(%s,%s,%s,%s,%s)',
            (data.get('forumId', 1), tid, data.get('title', ''), data.get('content', ''), 'pending'))
    return ok(message='发布成功,待审核')


@app.route('/api/teacher/forum/mine', methods=['GET'])
@login_required
def teacher_forum_mine():
    tid = request.login_user['id']
    rows = query('SELECT p.*, f.name forum_name FROM posts p JOIN forums f ON p.forum_id=f.id '
                 'WHERE p.author_id=%s ORDER BY p.id DESC', (tid,))
    return jsonify([{'id': r['id'], 'title': r['title'], 'content': r['content'],
                     'author': '我', 'avatar': '', 'forumId': r['forum_id'], 'forumName': r['forum_name'],
                     'createTime': str(r['created_at']).replace('T', ' ')[:16] if r['created_at'] else '',
                     'views': r['views'], 'replies': r['replies'], 'likes': r['likes'],
                     'top': bool(r['is_top']), 'level': '我'} for r in rows])


@app.route('/api/teacher/forum/boards', methods=['GET'])
@login_required
def teacher_forum_boards():
    rows = query('SELECT f.id, f.name, f.post_count count FROM forums f ORDER BY f.sort_order')
    return jsonify([{'id': r['id'], 'name': r['name'], 'count': r['count']} for r in rows])


# ================================================================
#  管理员端接口
# ================================================================
@app.route('/api/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    total = query('SELECT SUM(points) t FROM students', one=True)
    classes = query('SELECT name, total_points score FROM classes ORDER BY total_points DESC LIMIT 6')
    return jsonify({
        'totalScore': total['t'] if total else 0,
        'classScores': [{'class': c['name'], 'score': c['score']} for c in classes],
        'questionDistribution': {'daily': 28, '语文': 18, '数学': 15, '英语': 12, '科学': 10, '体育': 8, '美术': 7},
        'behaviorCompliance': 87,
        'classActivity': {'出勤率': 95, '课堂参与度': 88, '作业完成率': 92, '纪律表现': 78, '积分获取': 85}
    })


@app.route('/api/admin/students', methods=['GET'])
@login_required
def admin_students():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    offset = (page - 1) * size
    rows = query('SELECT s.*, c.name class_name, sp.pet_level FROM students s '
                 'LEFT JOIN classes c ON s.class_id=c.id '
                 'LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 '
                 'ORDER BY s.id LIMIT %s,%s', (offset, size))
    return jsonify({'success': True, 'data': [
        {'sno': r['student_no'], 'name': r['name'], 'className': r['class_name'] or '未分班',
         'points': r['points'], 'petLevel': (r['pet_level'] or 'B') + '级',
         'taskCompletionRate': r['task_completion_rate'] or 0,
         'moodIndex': r['mood_index'] or 3, 'status': 1} for r in rows]})


@app.route('/api/admin/students', methods=['POST'])
@login_required
def admin_student_create():
    data = request.get_json(silent=True) or {}
    c = query('SELECT id FROM classes WHERE name=%s', (data.get('className'),), one=True)
    execute('INSERT INTO students(name,student_no,password,class_id,points,mood_status) '
            'VALUES(%s,%s,%s,%s,%s,%s)',
            (data.get('name'), f'2026{random.randint(10000, 99999)}', md5('123456'),
             c['id'] if c else None, 0, '良好'))
    return ok(message='添加成功')


@app.route('/api/admin/students/<sid>', methods=['PUT'])
@login_required
def admin_student_update(sid):
    data = request.get_json(silent=True) or {}
    c = query('SELECT id FROM classes WHERE name=%s', (data.get('className'),), one=True)
    execute('UPDATE students SET name=%s, class_id=%s, points=%s, mood_index=%s, '
            'task_completion_rate=%s WHERE id=%s',
            (data.get('name'), c['id'] if c else None, data.get('points', 0),
             data.get('moodIndex', 3), data.get('taskCompletionRate', 0), sid))
    return ok(message='更新成功')


@app.route('/api/admin/students/<sid>', methods=['DELETE'])
@login_required
def admin_student_delete(sid):
    execute('DELETE FROM students WHERE id=%s', (sid,))
    return ok(message='删除成功')


@app.route('/api/admin/students/<sid>', methods=['GET'])
@login_required
def admin_student_detail(sid):
    r = query('SELECT s.*, c.name class_name, sp.pet_level FROM students s '
              'LEFT JOIN classes c ON s.class_id=c.id '
              'LEFT JOIN student_pets sp ON sp.student_id=s.id AND sp.is_active=1 WHERE s.id=%s', (sid,), one=True)
    return jsonify({'sno': r['student_no'], 'name': r['name'], 'className': r['class_name'] or '未分班',
                    'points': r['points'], 'petLevel': (r['pet_level'] or 'B') + '级',
                    'taskCompletionRate': r['task_completion_rate'] or 0,
                    'moodIndex': r['mood_index'] or 3, 'status': 1})


@app.route('/api/admin/teachers', methods=['GET'])
@login_required
def admin_teachers():
    rows = query('SELECT * FROM teachers ORDER BY id')
    return jsonify({'success': True, 'data': [
        {'tno': r['employee_id'], 'name': r['name'], 'subject': r['department'] or '',
         'teachingClass': _class_names(r['class_ids']), 'qualification': r['level'],
         'status': 1, 'simulationCount': r['simulation_count'] or 0} for r in rows]})


def _class_names(class_ids):
    if not class_ids:
        return ''
    try:
        ids = json.loads(class_ids) if isinstance(class_ids, str) else class_ids
    except Exception:
        return ''
    if not ids:
        return ''
    placeholders = ','.join(['%s'] * len(ids))
    classes = query(f'SELECT name FROM classes WHERE id IN ({placeholders})', tuple(ids))
    return ','.join(c['name'] for c in classes)


@app.route('/api/admin/teachers', methods=['POST'])
@login_required
def admin_teacher_create():
    data = request.get_json(silent=True) or {}
    execute('INSERT INTO teachers(name,employee_id,password,department,level,role) '
            'VALUES(%s,%s,%s,%s,%s,%s)',
            (data.get('name'), f'T{random.randint(100, 999)}', md5('123456'),
             data.get('subject', ''), data.get('qualification', '任课教师'), 'teacher'))
    return ok(message='添加成功')


@app.route('/api/admin/teachers/<tid>', methods=['PUT'])
@login_required
def admin_teacher_update(tid):
    data = request.get_json(silent=True) or {}
    execute('UPDATE teachers SET name=%s, department=%s, level=%s, simulation_count=%s WHERE id=%s',
            (data.get('name'), data.get('subject'), data.get('qualification'),
             data.get('simulationCount', 0), tid))
    return ok(message='更新成功')


@app.route('/api/admin/teachers/<tid>', methods=['DELETE'])
@login_required
def admin_teacher_delete(tid):
    execute('DELETE FROM teachers WHERE id=%s', (tid,))
    return ok(message='删除成功')


@app.route('/api/admin/teachers/<tid>', methods=['GET'])
@login_required
def admin_teacher_detail(tid):
    r = query('SELECT * FROM teachers WHERE id=%s', (tid,), one=True)
    return jsonify({'tno': r['employee_id'], 'name': r['name'], 'subject': r['department'] or '',
                    'teachingClass': _class_names(r['class_ids']), 'qualification': r['level'],
                    'status': 1, 'simulationCount': r['simulation_count'] or 0})


@app.route('/api/admin/forum/daily', methods=['GET'])
@login_required
def admin_forum_daily():
    rows = query('SELECT p.*, f.name forum_name, f.type forum_type, '
                 'COALESCE(s.name, t.name) author_name FROM posts p '
                 'JOIN forums f ON p.forum_id=f.id '
                 'LEFT JOIN students s ON p.author_id=s.id '
                 'LEFT JOIN teachers t ON p.author_id=t.id '
                 'WHERE f.type=%s ORDER BY p.is_top DESC, p.id DESC', ('daily',))
    return jsonify({'success': True, 'data': [
        {'id': r['id'], 'title': r['title'], 'content': r['content'][:100] if r['content'] else '',
         'authorName': r['author_name'] or '匿名', 'type': 'daily',
         'status': r['review_status'], 'isTop': r['is_top'],
         'createTime': str(r['created_at']) if r['created_at'] else ''} for r in rows]})


@app.route('/api/admin/forum/subject', methods=['GET'])
@login_required
def admin_forum_subject():
    subject = request.args.get('subject')
    sql = ('SELECT p.*, f.name forum_name, f.type forum_type, '
           'COALESCE(s.name, t.name) author_name FROM posts p '
           'JOIN forums f ON p.forum_id=f.id '
           'LEFT JOIN students s ON p.author_id=s.id '
           'LEFT JOIN teachers t ON p.author_id=t.id '
           'WHERE f.type=%s')
    args = ('subject',)
    if subject:
        sql += ' AND f.name=%s'
        args = ('subject', subject)
    sql += ' ORDER BY p.is_top DESC, p.id DESC'
    rows = query(sql, args)
    return jsonify({'success': True, 'data': [
        {'id': r['id'], 'title': r['title'], 'content': r['content'][:100] if r['content'] else '',
         'authorName': r['author_name'] or '匿名', 'subject': r['forum_name'], 'type': 'subject',
         'status': r['review_status'], 'isTop': r['is_top'],
         'createTime': str(r['created_at']) if r['created_at'] else ''} for r in rows]})


@app.route('/api/admin/forum/posts/<int:pid>/review', methods=['PUT'])
@login_required
def admin_forum_review(pid):
    data = request.get_json(silent=True) or {}
    execute('UPDATE posts SET review_status=%s WHERE id=%s', (data.get('status', 'approved'), pid))
    return ok(message='审核完成')


@app.route('/api/admin/forum/posts/<int:pid>/top', methods=['PUT'])
@login_required
def admin_forum_top(pid):
    execute('UPDATE posts SET is_top=1-is_top WHERE id=%s', (pid,))
    return ok(message='置顶状态已切换')


@app.route('/api/admin/forum/posts/<int:pid>', methods=['DELETE'])
@login_required
def admin_forum_delete(pid):
    execute('DELETE FROM posts WHERE id=%s', (pid,))
    return ok(message='删除成功')


@app.route('/api/admin/forum/announcement', methods=['POST'])
@login_required
def admin_forum_announcement():
    data = request.get_json(silent=True) or {}
    execute('INSERT INTO posts(forum_id,author_id,title,content,review_status,is_top) '
            'VALUES(1,0,%s,%s,%s,1)', (data.get('title', ''), data.get('content', ''), 'approved'))
    return ok(message='公告已发布')


@app.route('/api/admin/forum/boards', methods=['GET'])
@login_required
def admin_forum_boards():
    rows = query('SELECT id, name, post_count FROM forums ORDER BY sort_order')
    return jsonify([{'id': r['id'], 'name': r['name'], 'count': r['post_count']} for r in rows])


@app.route('/api/admin/forum/boards', methods=['POST'])
@login_required
def admin_forum_board_create():
    data = request.get_json(silent=True) or {}
    execute('INSERT INTO forums(name,type,sort_order) VALUES(%s,%s,99)',
            (data.get('name', ''), data.get('type', 'daily')))
    return ok(message='板块已创建')


@app.route('/api/admin/forum/boards/<int:bid>', methods=['PUT'])
@login_required
def admin_forum_board_update(bid):
    data = request.get_json(silent=True) or {}
    execute('UPDATE forums SET name=%s WHERE id=%s', (data.get('name', ''), bid))
    return ok(message='更新成功')


@app.route('/api/admin/points/overview', methods=['GET'])
@login_required
def admin_points_overview():
    rules = query('SELECT * FROM point_rules ORDER BY id')
    classes = query('SELECT name, total_points, student_count, avg_points FROM classes ORDER BY total_points DESC')
    return jsonify({
        'rules': [{'id': r['id'], 'name': r['name'], 'type': r['category'], 'points': r['points']} for r in rules],
        'classPoints': [{'className': c['name'], 'total': c['total_points'], 'count': c['student_count'],
                         'avg': float(c['avg_points'])} for c in classes],
        'dailyPointsData': [{'day': d, 'increase': random.randint(40, 80), 'decrease': random.randint(5, 20)}
                            for d in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']],
        'ruleDistribution': [{'value': r['points'], 'name': r['name']} for r in rules[:5]]
    })


@app.route('/api/admin/points/rankings', methods=['GET'])
@login_required
def admin_points_rankings():
    rows = query('SELECT s.name, c.name class_name, s.points FROM students s '
                 'LEFT JOIN classes c ON s.class_id=c.id ORDER BY s.points DESC LIMIT 20')
    return jsonify([{'name': r['name'], 'class': r['class_name'] or '未分班', 'points': r['points']} for r in rows])


@app.route('/api/admin/points/trend', methods=['GET'])
@login_required
def admin_points_trend():
    classes = query('SELECT name, total_points FROM classes ORDER BY total_points DESC LIMIT 6')
    return jsonify({'trend': [{'day': d, 'value': random.randint(500, 1000)}
                              for d in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']],
                    'classRank': [{'class': c['name'], 'points': c['total_points']} for c in classes]})


# ================================================================
#  AI通识课教学助手接口
# ================================================================

@app.route('/api/student/ai/courses', methods=['GET'])
@login_required
def ai_courses_list():
    grade = request.args.get('grade', 'upper_primary')
    rows = query('SELECT * FROM ai_courses WHERE grade_level=%s ORDER BY sort_order', (grade,))
    return jsonify([{'id': r['id'], 'title': r['title'], 'description': r['description'],
                     'category': r['category'], 'difficulty': r['difficulty']} for r in rows])


@app.route('/api/student/ai/grade', methods=['POST'])
@login_required
def ai_set_grade():
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    grade = data.get('grade', 'upper_primary')
    if grade not in ('lower_primary', 'upper_primary', 'middle_school', 'high_school'):
        return jsonify({'message': '无效的年级'}), 400
    execute('UPDATE students SET grade_level=%s WHERE id=%s', (grade, sid))
    return ok(message=f'已切换到{llm_service.GRADE_NAMES[grade]}')


@app.route('/api/student/ai/grade', methods=['GET'])
@login_required
def ai_get_grade():
    sid = request.login_user['id']
    s = query('SELECT grade_level FROM students WHERE id=%s', (sid,), one=True)
    grade = (s['grade_level'] if s and s['grade_level'] else 'upper_primary') or 'upper_primary'
    return jsonify({'grade': grade, 'gradeName': llm_service.GRADE_NAMES.get(grade, '小学高年级')})


@app.route('/api/student/ai/quiz/generate', methods=['POST'])
@login_required
def ai_quiz_generate():
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '人工智能基础')
    count = min(data.get('count', 3), 5)
    s = query('SELECT grade_level FROM students WHERE id=%s', (sid,), one=True)
    grade = (s['grade_level'] if s and s['grade_level'] else 'upper_primary') or 'upper_primary'
    questions = llm_service.generate_quiz(topic, grade, count)
    # 记录学习行为
    execute('INSERT INTO learning_records(student_id,course_id,topic,learn_type) VALUES(%s,%s,%s,%s)',
            (sid, data.get('courseId', 0), topic, 'quiz'))
    return jsonify({'questions': questions, 'topic': topic})


@app.route('/api/student/ai/quiz/grade', methods=['POST'])
@login_required
def ai_quiz_grade():
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    questions = data.get('questions', [])
    answers = data.get('answers', [])
    result = llm_service.grade_quiz(questions, answers)
    # 记录测验成绩
    execute('INSERT INTO learning_records(student_id,course_id,topic,learn_type,score) VALUES(%s,%s,%s,%s,%s)',
            (sid, data.get('courseId', 0), data.get('topic', ''), 'quiz', result['score']))
    # 答对一题奖励积分
    if result['correct'] > 0:
        execute('UPDATE students SET points=points+%s WHERE id=%s', (result['correct'] * 3, sid))
    return jsonify(result)


@app.route('/api/student/ai/picture-book/generate', methods=['POST'])
@login_required
def ai_book_generate():
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '什么是人工智能')
    s = query('SELECT grade_level FROM students WHERE id=%s', (sid,), one=True)
    grade = (s['grade_level'] if s and s['grade_level'] else 'lower_primary') or 'lower_primary'
    book = llm_service.generate_picture_book(topic, grade)
    # 保存绘本
    execute('INSERT INTO picture_books(student_id,title,topic,content) VALUES(%s,%s,%s,%s)',
            (sid, book.get('title', topic), topic, json.dumps(book, ensure_ascii=False)))
    # 记录学习行为
    execute('INSERT INTO learning_records(student_id,course_id,topic,learn_type) VALUES(%s,%s,%s,%s)',
            (sid, data.get('courseId', 0), topic, 'book'))
    return jsonify(book)


@app.route('/api/student/ai/picture-books', methods=['GET'])
@login_required
def ai_book_list():
    sid = request.login_user['id']
    rows = query('SELECT * FROM picture_books WHERE student_id=%s ORDER BY id DESC LIMIT 10', (sid,))
    return jsonify([{'id': r['id'], 'title': r['title'], 'topic': r['topic'],
                     'createdAt': str(r['created_at'])[:10]} for r in rows])


@app.route('/api/student/ai/animation/generate', methods=['POST'])
@login_required
def ai_animation_generate():
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '冒泡排序')
    s = query('SELECT grade_level FROM students WHERE id=%s', (sid,), one=True)
    grade = (s['grade_level'] if s and s['grade_level'] else 'upper_primary') or 'upper_primary'
    result = llm_service.generate_animation(topic, grade)
    # 记录学习行为
    execute('INSERT INTO learning_records(student_id,course_id,topic,learn_type) VALUES(%s,%s,%s,%s)',
            (sid, data.get('courseId', 0), topic, 'animation'))
    return jsonify(result)


@app.route('/api/student/ai/learning-path', methods=['GET'])
@login_required
def ai_learning_path():
    sid = request.login_user['id']
    s = query('SELECT grade_level FROM students WHERE id=%s', (sid,), one=True)
    grade = (s['grade_level'] if s and s['grade_level'] else 'upper_primary') or 'upper_primary'
    # 获取已学知识点
    learned = query('SELECT DISTINCT topic FROM learning_records WHERE student_id=%s AND topic IS NOT NULL', (sid,))
    learned_topics = [r['topic'] for r in learned] if learned else []
    # 获取最近测验成绩
    quizzes = query('SELECT score FROM learning_records WHERE student_id=%s AND learn_type=%s ORDER BY id DESC LIMIT 3',
                    (sid, 'quiz'))
    scores = [r['score'] for r in quizzes] if quizzes else []
    suggestion = llm_service.generate_learning_suggestion(grade, learned_topics, scores)
    return jsonify({
        'grade': grade,
        'gradeName': llm_service.GRADE_NAMES.get(grade, '小学高年级'),
        'learnedTopics': learned_topics,
        'recentScores': scores,
        'suggestions': suggestion.get('suggestions', []),
    })


@app.route('/api/student/ai/chat/history', methods=['GET'])
@login_required
def ai_chat_history():
    sid = request.login_user['id']
    rows = query('SELECT id, role, content, DATE_FORMAT(created_at,"%%H:%%i") t FROM chat_history '
                 'WHERE student_id=%s ORDER BY id DESC LIMIT 30', (sid,))
    return jsonify([{'id': r['id'], 'type': r['role'], 'content': r['content'], 'time': r['t']}
                    for r in reversed(rows)] if rows else [])


# ---- 聊天记录删除 ----
@app.route('/api/student/chat/<int:msg_id>', methods=['DELETE'])
@login_required
def student_chat_delete(msg_id):
    sid = request.login_user['id']
    execute('DELETE FROM chat_history WHERE id=%s AND student_id=%s', (msg_id, sid))
    return ok(message='已删除')


# ---- 聊天记录修改 ----
@app.route('/api/student/chat/<int:msg_id>', methods=['PUT'])
@login_required
def student_chat_update(msg_id):
    sid = request.login_user['id']
    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'success': False, 'message': '内容不能为空'}), 400
    execute('UPDATE chat_history SET content=%s WHERE id=%s AND student_id=%s',
            (content, msg_id, sid))
    return ok(message='已修改')


@app.route('/api/student/chat/clear', methods=['POST'])
@login_required
def student_chat_clear():
    sid = request.login_user['id']
    execute('DELETE FROM chat_history WHERE student_id=%s', (sid,))
    return ok(message='聊天记录已清空')


@app.route('/api/student/chat/rollback', methods=['POST'])
@login_required
def student_chat_rollback():
    sid = request.login_user['id']
    # 找到最近一条AI回复，删除它和对应的用户消息
    last_ai = query('SELECT id FROM chat_history WHERE student_id=%s AND role=%s ORDER BY id DESC LIMIT 1',
                    (sid, 'assistant'), one=True)
    if last_ai:
        execute('DELETE FROM chat_history WHERE id=%s AND student_id=%s', (last_ai['id'], sid))
    last_user = query('SELECT id FROM chat_history WHERE student_id=%s AND role=%s ORDER BY id DESC LIMIT 1',
                      (sid, 'user'), one=True)
    if last_user:
        execute('DELETE FROM chat_history WHERE id=%s AND student_id=%s', (last_user['id'], sid))
    return ok(message='已撤回上一轮对话')


# ---- 学习资料 ----
@app.route('/api/student/ai/materials', methods=['GET'])
@login_required
def ai_materials_list():
    course_id = request.args.get('courseId', 0, type=int)
    if course_id:
        rows = query('SELECT * FROM learning_materials WHERE course_id=%s ORDER BY sort_order', (course_id,))
    else:
        rows = query('SELECT * FROM learning_materials ORDER BY course_id, sort_order')
    return jsonify([{'id': r['id'], 'courseId': r['course_id'], 'title': r['title'],
                     'type': r['material_type'], 'url': r['url'],
                     'description': r['description']} for r in rows])


# ---- 课程推荐问题 ----
@app.route('/api/student/ai/suggested-questions', methods=['GET'])
@login_required
def ai_suggested_questions():
    course_id = request.args.get('courseId', 0, type=int)
    topic = request.args.get('topic', '')
    questions = []
    if course_id:
        row = query('SELECT suggested_questions FROM ai_courses WHERE id=%s', (course_id,), one=True)
        if row and row['suggested_questions']:
            try:
                questions = json.loads(row['suggested_questions'])
            except json.JSONDecodeError:
                pass
    if not questions and topic:
        # 默认推荐问题
        questions = [
            f'什么是{topic}？',
            f'{topic}有什么用处？',
            f'能举个例子解释{topic}吗？',
        ]
    if not questions:
        questions = [
            '什么是人工智能？',
            '机器学习和人类学习有什么区别？',
            '编程入门需要学什么？',
        ]
    return jsonify({'questions': questions, 'topic': topic})


if __name__ == '__main__':
    print('萌宠智伴后端启动: http://localhost:8000')
    app.run(host='0.0.0.0', port=8000, debug=True)
