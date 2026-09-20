"""Learning support signals and teacher-controlled, per-student practice difficulty."""
import datetime
from flask import jsonify, request


class LearningSupport:
    def __init__(self, app, get_db, query, execute, login_required, teacher_classes):
        self.query = query
        self.execute = execute
        self.get_db = get_db

        # 学生自评题目难度表
        self.execute('''
            CREATE TABLE IF NOT EXISTS quiz_difficulty_ratings (
              id INT AUTO_INCREMENT PRIMARY KEY,
              student_id INT NOT NULL,
              topic VARCHAR(200) NOT NULL DEFAULT '',
              question VARCHAR(500) NOT NULL DEFAULT '',
              stars INT NOT NULL,
              tags VARCHAR(500) NOT NULL DEFAULT '',
              created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              KEY student_time (student_id, created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        @app.route('/api/student/learning-support/help', methods=['POST'])
        @login_required
        def request_help():
            if request.login_user['role'] != 'student':
                return jsonify(message='仅学生可提交'), 403
            data = request.get_json(silent=True) or {}
            kind = data.get('kind', 'study')
            if kind not in ('study', 'mood'):
                return jsonify(message='无效的求助类型'), 400
            self.signal(request.login_user['id'], kind,
                        '学生主动反馈：' + ('做题有困难，希望老师帮助' if kind == 'study' else '心情低落，希望老师关心'))
            return jsonify(success=True, message='已告诉老师，你可以先休息一下')

        @app.route('/api/teacher/learning-support', methods=['GET'])
        @login_required
        def alerts():
            if request.login_user['role'] != 'teacher':
                return jsonify(message='仅教师可查看'), 403
            cids = teacher_classes(request.login_user['id'])
            if not cids:
                return jsonify(items=[], pendingCount=0)
            slots = ','.join(['%s'] * len(cids))
            rows = query(
                'SELECT a.*, s.name studentName, c.name className, '
                "COALESCE(p.difficulty, 'normal') difficulty FROM learning_support_alerts a "
                'JOIN students s ON s.id=a.student_id JOIN classes c ON c.id=s.class_id '
                'LEFT JOIN student_learning_support p ON p.student_id=s.id '
                f'WHERE s.class_id IN ({slots}) '
                "ORDER BY (a.status='pending') DESC, a.updated_at DESC, a.id DESC LIMIT 200", tuple(cids))
            count = query('SELECT COUNT(*) n FROM learning_support_alerts a '
                          'JOIN students s ON s.id=a.student_id '
                          f"WHERE s.class_id IN ({slots}) AND a.status='pending'", tuple(cids), one=True)
            student_ids = [r['student_id'] for r in rows]
            rating_map = {}
            if student_ids:
                rslots = ','.join(['%s'] * len(student_ids))
                ratings = query(
                    'SELECT r1.student_id, r1.topic, r1.question, r1.stars, r1.tags, r1.created_at '
                    'FROM quiz_difficulty_ratings r1 '
                    'WHERE r1.student_id IN (%s) AND r1.stars >= 4 '
                    'AND r1.created_at = (SELECT MAX(created_at) FROM quiz_difficulty_ratings r2 '
                    'WHERE r2.student_id = r1.student_id AND r2.stars >= 4)' % rslots,
                    tuple(student_ids))
                for r in ratings:
                    rating_map[r['student_id']] = r
            for row in rows:
                row['created_at'] = str(row['created_at'])
                row['updated_at'] = str(row['updated_at'])
                row['alert_date'] = str(row['alert_date'])
                row['actions'] = query(
                    'SELECT x.action, x.note, x.created_at, t.name teacherName '
                    'FROM learning_support_actions x LEFT JOIN teachers t ON t.id=x.teacher_id '
                    'WHERE x.alert_id=%s ORDER BY x.id DESC', (row['id'],))
                for action in row['actions']:
                    action['created_at'] = str(action['created_at'])
                rating = rating_map.get(row['student_id'])
                if rating:
                    row['studentRating'] = {
                        'topic': rating['topic'],
                        'question': rating['question'],
                        'stars': rating['stars'],
                        'tags': [t for t in (rating['tags'] or '').split(',') if t],
                        'time': str(rating['created_at'])
                    }
            return jsonify(items=rows, pendingCount=count['n'])

        @app.route('/api/teacher/learning-support/<int:aid>', methods=['POST'])
        @login_required
        def intervene(aid):
            if request.login_user['role'] != 'teacher':
                return jsonify(message='仅教师可操作'), 403
            data = request.get_json(silent=True) or {}
            action = data.get('action')
            note = data.get('note', '')
            if action not in ('easy', 'normal', 'observe') or not isinstance(note, str) or len(note) > 500:
                return jsonify(message='干预方式或备注无效'), 400
            tid = request.login_user['id']
            cids = teacher_classes(tid)
            conn = get_db()
            try:
                with conn.cursor() as cur:
                    cur.execute('SELECT a.student_id, s.class_id FROM learning_support_alerts a '
                                'JOIN students s ON s.id=a.student_id WHERE a.id=%s FOR UPDATE', (aid,))
                    alert = cur.fetchone()
                    if not alert or alert['class_id'] not in cids:
                        return jsonify(message='提醒不存在或不属于任教班级'), 404
                    sid = alert['student_id']
                    if action != 'observe':
                        cur.execute('INSERT INTO student_learning_support(student_id,difficulty,teacher_id) '
                                    'VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE difficulty=VALUES(difficulty), '
                                    'teacher_id=VALUES(teacher_id), updated_at=CURRENT_TIMESTAMP', (sid, action, tid))
                    cur.execute("UPDATE learning_support_alerts SET status='handled' WHERE id=%s", (aid,))
                    cur.execute('INSERT INTO learning_support_actions(alert_id,student_id,teacher_id,action,note) '
                                'VALUES(%s,%s,%s,%s,%s)', (aid, sid, tid, action, note.strip()))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            return jsonify(success=True, message='已保存，下次生成练习时生效')

        @app.route('/api/student/learning-support/rating', methods=['POST'])
        @login_required
        def submit_rating():
            if request.login_user['role'] != 'student':
                return jsonify(message='仅学生可提交'), 403
            data = request.get_json(silent=True) or {}
            stars = data.get('stars')
            topic = (data.get('topic') or '').strip()
            question = (data.get('question') or '').strip()
            tags = data.get('tags') or []
            if not isinstance(stars, int) or stars < 1 or stars > 5:
                return jsonify(message='评分应为1-5星'), 400
            if not isinstance(tags, list):
                return jsonify(message='标签格式错误'), 400
            sid = request.login_user['id']
            tags_str = ','.join(str(t) for t in tags)[:500]
            self.execute('INSERT INTO quiz_difficulty_ratings(student_id,topic,question,stars,tags) '
                         'VALUES(%s,%s,%s,%s,%s)',
                         (sid, topic[:200], question[:500], stars, tags_str))
            if stars >= 4:
                self.signal(sid, 'study', f'学生自评《{topic or "云笺小试"}》题目偏难（{stars}星）')
            return jsonify(success=True, message='评价已提交')

    def signal(self, sid, kind, reason, date=None):
        self.execute('INSERT INTO learning_support_alerts(student_id,kind,alert_date,reason) '
                     'VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE reason=VALUES(reason), '
                     "status='pending', updated_at=CURRENT_TIMESTAMP",
                     (sid, kind, date or datetime.date.today(), reason[:500]))

    def difficulty(self, sid):
        row = self.query('SELECT difficulty FROM student_learning_support WHERE student_id=%s', (sid,), one=True)
        return row['difficulty'] if row else 'normal'

    def emotions(self, sid):
        rows = self.query('SELECT emotion_date, mood, note FROM student_emotions '
                          'WHERE student_id=%s ORDER BY emotion_date DESC LIMIT 365', (sid,))
        return {str(r['emotion_date']): {'date': str(r['emotion_date']), 'mood': r['mood'],
                                       'note': r['note'] or ''} for r in rows}

    def record_emotion(self, sid, data):
        mood = data.get('mood')
        valid = ('happy', 'relax', 'puzzled', 'sad', 'angry', 'shock')
        if mood not in [f'/images/Mood_Diary/{m}.jpg' for m in valid]:
            return jsonify(message='请选择有效的心情'), 400
        try:
            date = datetime.date.fromisoformat(data.get('date') or str(datetime.date.today()))
            if date > datetime.date.today():
                raise ValueError()
        except (TypeError, ValueError):
            return jsonify(message='心情日期无效'), 400
        note = data.get('note')
        if note is not None and (not isinstance(note, str) or len(note) > 5000):
            return jsonify(message='日记最多5000字'), 400
        self.execute('INSERT INTO student_emotions(student_id,emotion_date,mood,note) VALUES(%s,%s,%s,%s) '
                     'ON DUPLICATE KEY UPDATE mood=VALUES(mood), note=COALESCE(VALUES(note),note)',
                     (sid, date, mood, note))
        if mood.endswith('/sad.jpg'):
            self.signal(sid, 'mood', f'学生在{date}的心情记录中选择了“难过”', date)
        return jsonify(success=True, message='记录成功')
