# -*- coding: utf-8 -*-
"""家长知情同意（监护人同意）机制

背景：学生与 AI 的对话内容会反映情绪与心理状态，属于敏感个人信息；使用者多为未成年人，
其中不满十四周岁的还需取得监护人同意并制定专门的处理规则。因此系统需要做到：

1. 分项同意：账号基本信息为使用所必需；保存对话记录、情绪关键词标记、教师查看三项单独列出；
   研究用途必须单独勾选且默认不勾。
2. 可撤回：家长随时可以撤回同意，撤回后对话不再保存，教师与管理员也不再可见。
3. 可留证：记录同意人、与孩子的关系、手机号、条款版本、同意方式与时间。
4. 可查询：学生本人/监护人可查看自己的同意状态与登记明细。

两种登记方式并存：
- 短信验证：家长在学生端页面上填写手机号并输入收到的验证码（method='sms'）。
- 纸质回收：学校统一发放《告家长书》，由班主任或管理员批量登记（method='paper_batch'）。

注意：本模块内的角色判断只用于防止误操作。当前后端的 token 尚未做签名校验，角色字段可以从
请求头伪造，鉴权加固（admin_required 装饰器 + 签名 token）需要另行处理。
"""
import datetime
import random

from flask import jsonify, request

# 条款版本号：条款正文有任何改动都要改这里，已登记的记录会保留旧版本号
TERMS_VERSION = '2026-09-v1'

# 同意项定义：编号 -> (标题, 说明, 是否必需, 是否依赖第 2 项)
CONSENT_SCOPES = {
    '1': {'title': '账号基本信息', 'desc': '姓名、学号、班级、头像，用于账号登录和老师识别孩子身份',
          'required': True, 'dependsOnChat': False},
    '2': {'title': '保存 AI 对话记录', 'desc': '保存孩子与 AI 的聊天内容和 AI 的回复，用于让对话接得上上下文、及时发现异常',
          'required': False, 'dependsOnChat': False},
    '3': {'title': '情绪与困难关键词标记', 'desc': '对聊天内容做关键词标记（情绪低落 / 关系冲突 / 学业压力），用于从大量对话中筛出需要关心的孩子',
          'required': False, 'dependsOnChat': True},
    '4': {'title': '教师查看与家校沟通', 'desc': '出现预警信号时，班主任可以查看相关对话内容并与家长联系',
          'required': False, 'dependsOnChat': True},
    '5': {'title': '去标识化研究与模型改进（可选）', 'desc': '在去掉姓名学号等身份标识后，用于改进 AI 对话效果和教学研究。此项可以不同意，不影响其它功能',
          'required': False, 'dependsOnChat': False},
}

# 条款正文：前端可直接渲染，也用于公开个人信息处理规则
CONSENT_TERMS = {
    'version': TERMS_VERSION,
    'title': '萌宠智伴 · 家长知情同意书',
    'updatedAt': '2026-09-21',
    'intro': '在孩子使用萌宠智伴之前，请您先了解我们会收集孩子的哪些信息、这些信息用来做什么、'
             '谁会看到、保存多久。除账号基本信息外，其余各项您都可以不同意；您也可以随时撤回同意。',
    'sections': [
        {'title': '一、我们收集哪些信息',
         'body': '孩子的姓名、学号、班级、头像；孩子与 AI 宠物的聊天内容和 AI 的回复、聊天时间；'
                 '孩子自己记录的心情与学习情况。'},
        {'title': '二、这些信息用来做什么',
         'body': '让 AI 能接着上文与孩子对话；在孩子表达情绪低落、被欺负或学业压力时，让老师及时发现问题；'
                 '用于本班教学情况统计。不用于任何商业用途，不对外提供。'},
        {'title': '三、谁可以看到',
         'body': '班主任在出现预警信号时可以看到相关对话内容；系统管理员进行内容合规检查；'
                 '其他学生和家长看不到。每次查看都会留下记录，供学校核查。'},
        {'title': '四、保存多久',
         'body': '对话记录默认保存一个学年，到期后只保留不包含身份信息的统计数据，原文删除。'},
        {'title': '五、您可以不同意哪些内容',
         'body': '第 1 项账号基本信息是使用系统所必需的；第 2、3、4 项您可以每一项单独选择；'
                 '第 5 项研究用途默认不勾选。如果不同意第 2 项，孩子的 AI 对话功能将暂停，'
                 '课程学习、练习题、宠物养成等其它功能正常使用。'},
        {'title': '六、您和孩子的权利',
         'body': '可以随时撤回同意；可以查阅、复制孩子的信息；可以要求更正或删除；'
                 '撤回或删除后，我们会停止相应的处理并删除对应数据。'},
        {'title': '七、我们的承诺',
         'body': '不把孩子的信息用于评优、处分等自动决策；不向第三方提供；不在公开场合展示孩子的聊天内容；'
                 '如果使用目的、方式或信息种类发生变化，会重新征求您的同意。'},
    ],
    'items': [dict(code=code, **info) for code, info in CONSENT_SCOPES.items()],
    'note': '如您对以上内容有疑问，请联系班主任或学校信息中心。',
}

# 同意方式文案
METHOD_TEXT = {
    'sms': '监护人短信确认',
    'paper_batch': '纸质《告家长书》回收登记',
    'legacy_import': '历史存量学生（启用同意机制前）',
}

STATE_TEXT = {
    'none': '未登记',
    'agreed': '已同意',
    'revoked': '已撤回',
}


class GuardianConsent:
    """家长知情同意：登记、查询、撤回与访问拦截。"""

    def __init__(self, app, get_db, query, execute, login_required,
                 teacher_classes, execute_return_id=None, setting=None):
        self.query = query
        self.execute = execute
        self.get_db = get_db
        self.teacher_classes = teacher_classes
        self.execute_return_id = execute_return_id
        # CONSENT_ENFORCE=0 时只记录同意情况，不做访问拦截（便于过渡期灰度）
        self.enforce = (setting('CONSENT_ENFORCE', '1') if setting else '1') != '0'

        existed = self._table_exists('guardian_consents')
        self._ensure_schema()
        if not existed:
            self._backfill_legacy()

        # ---------- 条款与同意项 ----------
        @app.route('/api/consent/terms', methods=['GET'])
        def consent_terms():
            """公开条款正文，家长无需登录即可查看（个人信息处理规则需公开、易于访问）。"""
            return jsonify(CONSENT_TERMS)

        # ---------- 查询同意状态 ----------
        @app.route('/api/consent/status', methods=['GET'])
        @login_required
        def consent_status():
            student_id, err = self._resolve_student(request.args.get('studentId', type=int))
            if err:
                return err
            return jsonify(self.status(student_id))

        # ---------- 监护人短信验证码 ----------
        @app.route('/api/consent/send-code', methods=['POST'])
        @login_required
        def consent_send_code():
            data = request.get_json(silent=True) or {}
            student_id, err = self._resolve_student(data.get('studentId'))
            if err:
                return err
            phone = self._normalize_phone(data.get('guardianPhone'))
            if len(phone) != 11 or not phone.isdigit():
                return jsonify({'success': False, 'message': '请填写 11 位监护人手机号'}), 400
            recent = self.query(
                'SELECT created_at FROM guardian_consent_codes WHERE student_id=%s '
                'ORDER BY id DESC LIMIT 1', (student_id,), one=True)
            if recent and recent['created_at']:
                gap = (datetime.datetime.now() - recent['created_at']).total_seconds()
                if gap < 60:
                    return jsonify({'success': False,
                                    'message': f'验证码发送过于频繁，请 {int(60 - gap)} 秒后再试'}), 429
            code = ''.join(random.choice('0123456789') for _ in range(6))
            self.execute(
                'INSERT INTO guardian_consent_codes(student_id,guardian_phone,code,expires_at) '
                'VALUES(%s,%s,%s,%s)',
                (student_id, phone, code,
                 datetime.datetime.now() + datetime.timedelta(minutes=10)))
            # 短信通道未接入时进入开发模式：直接返回验证码，方便演示与联调
            sms_ready = (setting('CONSENT_SMS_PROVIDER', '') if setting else '')
            if not sms_ready:
                return jsonify({'success': True, 'devMode': True, 'code': code,
                                'message': f'短信通道未配置，开发模式验证码：{code}（10 分钟内有效）'})
            return jsonify({'success': True, 'devMode': False,
                            'message': f'验证码已发送至 {self._mask_phone(phone)}，10 分钟内有效'})

        # ---------- 提交同意 ----------
        @app.route('/api/consent/submit', methods=['POST'])
        @login_required
        def consent_submit():
            data = request.get_json(silent=True) or {}
            student_id, err = self._resolve_student(data.get('studentId'))
            if err:
                return err
            scopes = self._normalize_scopes(data.get('scopes'))
            if '1' not in scopes:
                return jsonify({'success': False,
                                'message': '未同意第 1 项账号基本信息，无法在系统中建立账号。'
                                           '如不接受，请向班主任说明，我们会停止使用该系统。'}), 400
            # 未同意保存对话记录时，情绪标记与教师查看都失去依据，一并去除
            if '2' not in scopes:
                scopes = [s for s in scopes if s not in ('3', '4')]
            guardian_name = (data.get('guardianName') or '').strip()[:50]
            relation = (data.get('guardianRelation') or '监护人').strip()[:20]
            phone = self._normalize_phone(data.get('guardianPhone'))
            if not guardian_name:
                return jsonify({'success': False, 'message': '请填写监护人姓名'}), 400
            if len(phone) != 11 or not phone.isdigit():
                return jsonify({'success': False, 'message': '请填写 11 位监护人手机号'}), 400

            method = (data.get('method') or 'sms').strip()
            operator_id = None
            if method == 'paper_batch':
                # 纸质同意书由老师/管理员代登记，需要校验操作人身份与班级范围
                if request.login_user['role'] not in ('teacher', 'admin'):
                    return jsonify({'success': False, 'message': '仅教师或管理员可以代登记纸质同意书'}), 403
                operator_id = request.login_user['id']
            else:
                method = 'sms'
                code = (data.get('code') or '').strip()
                if not code:
                    return jsonify({'success': False, 'message': '请填写监护人收到的验证码'}), 400
                row = self.query(
                    'SELECT id FROM guardian_consent_codes WHERE student_id=%s AND guardian_phone=%s '
                    'AND code=%s AND used=0 AND expires_at>NOW() ORDER BY id DESC LIMIT 1',
                    (student_id, phone, code), one=True)
                if not row:
                    return jsonify({'success': False, 'message': '验证码不正确或已过期'}), 400
                self.execute('UPDATE guardian_consent_codes SET used=1 WHERE id=%s', (row['id'],))

            grade = self._grade_of(student_id)
            rid = self._insert_record(student_id, guardian_name, relation, phone, scopes,
                                      method, operator_id, under_14=self._is_under_14(grade),
                                      note=(data.get('note') or '').strip()[:255] or None)
            state = self.status(student_id)
            return jsonify({'success': True, 'id': rid, 'status': state,
                            'message': self._submit_message(scopes)})

        # ---------- 撤回同意 ----------
        @app.route('/api/consent/revoke', methods=['POST'])
        @login_required
        def consent_revoke():
            data = request.get_json(silent=True) or {}
            student_id, err = self._resolve_student(data.get('studentId'))
            if err:
                return err
            cur = self.status(student_id)
            if cur['state'] != 'agreed':
                return jsonify({'success': False, 'message': '当前没有可撤回的同意记录'}), 400
            self.execute(
                'INSERT INTO guardian_consents(student_id,guardian_name,guardian_relation,guardian_phone,'
                'scopes,terms_version,status,method,under_14,note,revoked_at) '
                'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())',
                (student_id, cur['guardianName'], cur['guardianRelation'], cur['guardianPhoneRaw'],
                 '', TERMS_VERSION, 'revoked', cur['method'],
                 1 if cur['under14'] else 0,
                 (data.get('reason') or '监护人撤回同意').strip()[:255]))
            return jsonify({'success': True, 'message': '已撤回同意，该学生的对话记录不再保存，'
                                                       '教师端也不再展示其对话内容'})

        # ---------- 按班级批量登记（回收纸质《告家长书》时使用） ----------
        @app.route('/api/consent/batch', methods=['POST'])
        @login_required
        def consent_batch():
            role = request.login_user['role']
            if role not in ('teacher', 'admin'):
                return jsonify({'success': False, 'message': '仅教师或管理员可以批量登记'}), 403
            data = request.get_json(silent=True) or {}
            scopes = self._normalize_scopes(data.get('scopes') or ['1', '2', '3', '4'])
            if '1' not in scopes:
                return jsonify({'success': False, 'message': '第 1 项为使用必需项，不能取消'}), 400
            if '2' not in scopes:
                scopes = [s for s in scopes if s not in ('3', '4')]
            class_id = data.get('classId')
            if role == 'teacher':
                cids = self.teacher_classes(request.login_user['id'])
                if not cids:
                    return jsonify({'success': False, 'message': '您还没有负责的班级'}), 403
                if not class_id:
                    return jsonify({'success': False, 'message': '请选择班级'}), 400
                if int(class_id) not in [int(c) for c in cids]:
                    return jsonify({'success': False, 'message': '只能登记自己负责的班级'}), 403
            students = self.query(
                'SELECT s.id, s.name, c.grade FROM students s LEFT JOIN classes c ON c.id=s.class_id '
                'WHERE s.class_id=%s ORDER BY s.id', (class_id,))
            note = (data.get('note') or '已回收纸质《家长知情同意书》').strip()[:255]
            operator_id = request.login_user['id']
            done = 0
            for s in students:
                if self.status(s['id'])['state'] == 'agreed':
                    continue
                self._insert_record(s['id'], data.get('guardianName') or '（纸质同意书）',
                                    '监护人', self._normalize_phone(data.get('guardianPhone')),
                                    scopes, 'paper_batch', operator_id,
                                    under_14=self._is_under_14(s['grade']), note=note)
                done += 1
            return jsonify({'success': True, 'count': done,
                            'message': f'已登记 {done} 名学生（班级共 {len(students)} 人，已同意的会跳过）'})

        # ---------- 登记明细（教师看本班 / 管理员看全校） ----------
        @app.route('/api/consent/list', methods=['GET'])
        @login_required
        def consent_list():
            role = request.login_user['role']
            class_id = request.args.get('classId', type=int) or 0
            if role == 'teacher':
                cids = [int(c) for c in self.teacher_classes(request.login_user['id'])]
                if class_id:
                    if class_id not in cids:
                        return jsonify({'success': False, 'message': '只能查看自己负责的班级'}), 403
                    cids = [class_id]
            elif role == 'admin':
                cids = [class_id] if class_id else [r['id'] for r in self.query('SELECT id FROM classes')]
            else:
                return jsonify({'success': False, 'message': '无查看权限'}), 403
            if not cids:
                return jsonify({'items': [], 'summary': self._empty_summary()})
            ph = ','.join(['%s'] * len(cids))
            rows = self.query(
                'SELECT s.id student_id, s.name student_name, c.name class_name, c.grade '
                'FROM students s LEFT JOIN classes c ON c.id=s.class_id '
                f'WHERE s.class_id IN ({ph}) ORDER BY s.id', tuple(cids))
            items = []
            summary = {'total': len(rows), 'agreed': 0, 'revoked': 0, 'none': 0, 'chatEnabled': 0}
            for r in rows:
                st = self.status(r['student_id'])
                summary[st['state'] if st['state'] in summary else 'none'] += 1
                if st['chatEnabled']:
                    summary['chatEnabled'] += 1
                items.append({
                    'studentId': r['student_id'], 'studentName': r['student_name'],
                    'className': r['class_name'], 'grade': r['grade'],
                    'state': st['state'], 'stateText': st['stateText'],
                    'scopes': st['scopes'], 'scopeText': st['scopeText'],
                    'chatEnabled': st['chatEnabled'],
                    'guardianName': st['guardianName'], 'guardianRelation': st['guardianRelation'],
                    'guardianPhone': st['guardianPhone'], 'method': st['method'],
                    'methodText': st['methodText'], 'termsVersion': st['termsVersion'],
                    'under14': st['under14'], 'consentedAt': st['consentedAt'],
                    'revokedAt': st['revokedAt'],
                })
            return jsonify({'items': items, 'summary': summary})

        @app.route('/api/consent/classes', methods=['GET'])
        @login_required
        def consent_classes():
            role = request.login_user['role']
            if role == 'teacher':
                cids = self.teacher_classes(request.login_user['id'])
                if not cids:
                    return jsonify([])
                ph = ','.join(['%s'] * len(cids))
                return jsonify(self.query(
                    f'SELECT id, name, grade FROM classes WHERE id IN ({ph}) ORDER BY id', tuple(cids)))
            if role == 'admin':
                return jsonify(self.query('SELECT id, name, grade FROM classes ORDER BY id'))
            return jsonify({'success': False, 'message': '无查看权限'}), 403

    # ================= 供 app.py 调用的判定方法 =================

    def status(self, student_id):
        """返回某学生的同意状态（以最新一条记录为准）。"""
        row = self.query('SELECT * FROM guardian_consents WHERE student_id=%s ORDER BY id DESC LIMIT 1',
                         (student_id,), one=True)
        if not row:
            return {'studentId': student_id, 'state': 'none', 'stateText': STATE_TEXT['none'],
                    'scopes': [], 'scopeText': '', 'chatEnabled': False, 'guardianName': '',
                    'guardianRelation': '', 'guardianPhone': '', 'guardianPhoneRaw': '',
                    'method': '', 'methodText': '', 'termsVersion': '', 'under14': False,
                    'consentedAt': '', 'revokedAt': ''}
        scopes = [s for s in (row['scopes'] or '').split(',') if s]
        agreed = (row['status'] or 'agreed') == 'agreed'
        return {
            'studentId': student_id,
            'state': 'agreed' if agreed else 'revoked',
            'stateText': STATE_TEXT['agreed' if agreed else 'revoked'],
            'scopes': scopes if agreed else [],
            'scopeText': '、'.join(f"{s}.{CONSENT_SCOPES[s]['title']}" for s in scopes
                                   if s in CONSENT_SCOPES) if agreed else '',
            'chatEnabled': bool(agreed and '2' in scopes),
            'guardianName': row['guardian_name'] or '',
            'guardianRelation': row['guardian_relation'] or '',
            'guardianPhone': self._mask_phone(row['guardian_phone'] or ''),
            'guardianPhoneRaw': row['guardian_phone'] or '',
            'method': row['method'] or '',
            'methodText': METHOD_TEXT.get(row['method'] or '', row['method'] or ''),
            'termsVersion': row['terms_version'] or '',
            'under14': bool(row['under_14']),
            'consentedAt': str(row['consented_at'])[:19] if row['consented_at'] else '',
            'revokedAt': str(row['revoked_at'])[:19] if row['revoked_at'] else '',
        }

    def chat_block_reason(self, student_id):
        """AI 对话功能是否可用；返回 None 表示可用，否则返回给学生的提示语。"""
        if not self.enforce:
            return None
        st = self.status(student_id)
        if st['state'] == 'agreed' and st['chatEnabled']:
            return None
        if st['state'] == 'agreed':
            return ('家长未同意「保存 AI 对话记录」，AI 伙伴功能已暂停，其它功能可以正常使用。'
                    '如需开启，请家长在《家长知情同意书》中勾选第 2 项。')
        if st['state'] == 'revoked':
            return ('家长已撤回同意，系统不再保存对话记录，AI 伙伴功能已暂停。'
                    '如需恢复，请家长重新完成《家长知情同意书》。')
        return ('尚未完成家长知情同意登记，AI 伙伴功能暂不可用。'
                '请家长完成《家长知情同意书》，或由老师登记已回收的纸质同意书。')

    def enabled_condition(self, alias='s', scope='2'):
        """供教师端/管理员端 SQL 拼接：只查询已获得指定授权项的学生。

        scope='2' 表示允许保存对话记录（管理员做内容合规检查用）；
        scope='4' 表示额外允许教师查看对话内容（教师端列表用）。
        同意状态完全由 guardian_consents 的最新一条记录推导，不依赖任何冗余字段，
        因此家长撤回同意后，教师端和管理员端会立即查不到该学生的对话。
        """
        if not self.enforce:
            return None
        if scope not in CONSENT_SCOPES:
            scope = '2'
        return (f"EXISTS (SELECT 1 FROM guardian_consents gc WHERE gc.student_id={alias}.id "
                f"AND gc.status='agreed' AND FIND_IN_SET('{scope}', gc.scopes) "
                f"AND gc.id=(SELECT MAX(g2.id) FROM guardian_consents g2 "
                f"WHERE g2.student_id={alias}.id))")

    def scope_allowed(self, student_id, scope):
        """该学生是否获得某一项的授权；未开启强制拦截时一律返回 True。"""
        if not self.enforce:
            return True
        return scope in self.status(student_id)['scopes']

    def teacher_view_reason(self, student_id):
        """教师查看某学生对话是否被授权；返回 None 表示允许，否则返回提示语。"""
        if not self.enforce:
            return None
        st = self.status(student_id)
        if st['state'] != 'agreed':
            return '该学生尚未完成家长知情同意登记，或家长已撤回同意，无法查看其对话内容。'
        if '2' not in st['scopes']:
            return '家长未同意保存 AI 对话记录，该学生没有可查看的对话内容。'
        if '4' not in st['scopes']:
            return '家长未同意「教师查看与家校沟通」这一项，如需了解情况请联系家长本人或由班主任介入。'
        return None

    # ================= 内部方法 =================

    def _submit_message(self, scopes):
        if '2' not in scopes:
            return '已登记：家长未同意保存 AI 对话记录，该学生的 AI 伙伴功能已暂停，其它功能正常'
        if '5' not in scopes:
            return '已登记：家长同意保存对话并用于教学关怀，未授权研究用途'
        return '已登记：同意已保存，感谢您的配合'

    def _insert_record(self, student_id, guardian_name, relation, phone, scopes,
                       method, operator_id=None, under_14=False, note=None):
        sql = ('INSERT INTO guardian_consents(student_id,guardian_name,guardian_relation,guardian_phone,'
               'scopes,terms_version,status,method,under_14,note,operator_id) '
               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)')
        args = (student_id, guardian_name, relation, phone, ','.join(scopes), TERMS_VERSION,
                'agreed', method, 1 if under_14 else 0, note, operator_id)
        if self.execute_return_id:
            return self.execute_return_id(sql, args)
        self.execute(sql, args)
        return None

    def _resolve_student(self, raw_student_id):
        """把请求里的 studentId 解析成当前登录人有权操作的学生，返回 (id, 错误响应)。"""
        role = request.login_user['role']
        login_id = request.login_user['id']
        if role == 'student':
            if raw_student_id and int(raw_student_id) != int(login_id):
                return None, (jsonify({'success': False, 'message': '只能查看和登记自己的信息'}), 403)
            return int(login_id), None
        if not raw_student_id:
            return None, (jsonify({'success': False, 'message': '请指定学生 studentId'}), 400)
        student_id = int(raw_student_id)
        row = self.query('SELECT id, class_id FROM students WHERE id=%s', (student_id,), one=True)
        if not row:
            return None, (jsonify({'success': False, 'message': '学生不存在'}), 404)
        if role == 'teacher':
            cids = [int(c) for c in self.teacher_classes(login_id)]
            if not cids or int(row['class_id'] or 0) not in cids:
                return None, (jsonify({'success': False, 'message': '只能处理自己班级的学生'}), 403)
        elif role != 'admin':
            return None, (jsonify({'success': False, 'message': '无操作权限'}), 403)
        return student_id, None

    def _normalize_scopes(self, raw):
        if isinstance(raw, str):
            raw = [s for s in raw.split(',') if s]
        if not raw:
            return []
        return [str(s) for s in raw if str(s) in CONSENT_SCOPES]

    def _grade_of(self, student_id):
        row = self.query('SELECT c.grade FROM students s LEFT JOIN classes c ON c.id=s.class_id '
                         'WHERE s.id=%s', (student_id,), one=True)
        return (row['grade'] if row else '') or ''

    @staticmethod
    def _is_under_14(grade):
        """按年级从宽认定是否不满十四周岁：小学各年级与初一、初二都按不满14周岁处理。

        初一、初二学生约 12-14 周岁，处在十四周岁的临界线上，从严按不满十四周岁处理，
        以便统一执行「取得监护人同意 + 单独处理规则」的要求。
        """
        value = str(grade or '')
        for word in ('一', '二', '三', '四', '五', '六'):
            if value.startswith(word) and ('年级' in value or '小' in value):
                return True
        return value.startswith(('初一', '初二', '七年级', '八年级'))

    @staticmethod
    def _normalize_phone(value):
        return ''.join(ch for ch in str(value or '') if ch.isdigit())[:11]

    @staticmethod
    def _mask_phone(phone):
        phone = str(phone or '')
        if len(phone) == 11:
            return phone[:3] + '****' + phone[-4:]
        return phone or '—'

    @staticmethod
    def _empty_summary():
        return {'total': 0, 'agreed': 0, 'revoked': 0, 'none': 0, 'chatEnabled': 0}

    def _table_exists(self, table):
        row = self.query('SELECT COUNT(*) n FROM information_schema.TABLES '
                         'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s', (table,), one=True)
        return bool(row and row['n'])

    def _ensure_schema(self):
        """建表；使用 IF NOT EXISTS，可重复执行，不需要改动任何已有业务表。"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS guardian_consents (
              id INT AUTO_INCREMENT PRIMARY KEY,
              student_id INT NOT NULL COMMENT '学生ID',
              guardian_name VARCHAR(50) NOT NULL DEFAULT '' COMMENT '监护人姓名',
              guardian_relation VARCHAR(20) NOT NULL DEFAULT '监护人' COMMENT '与学生关系',
              guardian_phone VARCHAR(20) NOT NULL DEFAULT '' COMMENT '监护人手机号',
              scopes VARCHAR(100) NOT NULL DEFAULT '' COMMENT '同意项编号，逗号分隔，见 CONSENT_SCOPES',
              terms_version VARCHAR(20) NOT NULL DEFAULT '' COMMENT '同意的条款版本',
              status VARCHAR(10) NOT NULL DEFAULT 'agreed' COMMENT 'agreed/revoked',
              method VARCHAR(20) NOT NULL DEFAULT 'sms' COMMENT 'sms/paper_batch/legacy_import',
              under_14 TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否不满十四周岁',
              note VARCHAR(255) DEFAULT NULL,
              operator_id INT DEFAULT NULL COMMENT '代登记的老师或管理员ID',
              consented_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              revoked_at DATETIME DEFAULT NULL,
              KEY idx_student (student_id, id),
              KEY idx_state (status, consented_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            COMMENT='家长知情同意登记（每次同意或撤回都新增一条，以最新一条为准）'
        ''')
        self.execute('''
            CREATE TABLE IF NOT EXISTS guardian_consent_codes (
              id INT AUTO_INCREMENT PRIMARY KEY,
              student_id INT NOT NULL,
              guardian_phone VARCHAR(20) NOT NULL,
              code VARCHAR(10) NOT NULL,
              used TINYINT(1) NOT NULL DEFAULT 0,
              expires_at DATETIME NOT NULL,
              created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              KEY idx_student (student_id, created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监护人短信验证码'
        ''')

    def _backfill_legacy(self):
        """首次启用同意机制时，把存量学生按「历史存量」登记，避免老师端突然看不到对话。"""
        ids = self.query('SELECT id FROM students')
        for r in ids:
            self._insert_record(r['id'], '（历史存量）', '未采集', '', ['1', '2', '3', '4'],
                                'legacy_import', None, under_14=False,
                                note='启用同意机制前的存量学生，按学校统一告知处理，待补齐纸质《告家长书》')
        print(f'[consent] 已启用家长知情同意机制，存量学生 {len(ids)} 人登记为历史存量，'
              f'请尽快回收纸质《告家长书》后重新登记。')
