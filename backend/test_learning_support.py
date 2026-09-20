"""Run with: python -B -m unittest discover -s backend -p test_learning_support.py"""
import datetime
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, request
import app as server
from learning_support import LearningSupport


class SupportTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.query = MagicMock()
        self.execute = MagicMock()
        self.conn = MagicMock()
        self.cursor = self.conn.cursor.return_value.__enter__.return_value
        self.cursor.fetchone.return_value = {'student_id': 7, 'class_id': 2}

        def login(fn):
            def wrapped(*args, **kwargs):
                request.login_user = {'id': 7, 'role': request.headers.get('Role', 'student')}
                return fn(*args, **kwargs)
            wrapped.__name__ = fn.__name__
            return wrapped

        self.support = LearningSupport(self.app, lambda: self.conn, self.query,
                                       self.execute, login, lambda _: [2])
        self.client = self.app.test_client()

    def test_help_is_saved_and_invalid_kind_rejected(self):
        self.assertEqual(self.client.post('/api/student/learning-support/help', json={'kind': 'study'}).status_code, 200)
        self.assertEqual(self.execute.call_args.args[1][1], 'study')
        self.assertEqual(self.client.post('/api/student/learning-support/help', json={'kind': 'other'}).status_code, 400)

    def test_roles_cannot_cross(self):
        self.assertEqual(self.client.get('/api/teacher/learning-support').status_code, 403)
        self.assertEqual(self.client.post('/api/teacher/learning-support/1', json={'action': 'easy'}).status_code, 403)
        self.assertEqual(self.client.post('/api/student/learning-support/help', headers={'Role': 'teacher'}).status_code, 403)
        self.execute.assert_not_called()

    def test_unassigned_class_cannot_be_changed(self):
        self.cursor.fetchone.return_value = {'student_id': 7, 'class_id': 99}
        response = self.client.post('/api/teacher/learning-support/1', json={'action': 'easy'}, headers={'Role': 'teacher'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.conn.commit.assert_not_called()

    def test_adjust_restore_and_observe(self):
        for action in ('easy', 'normal', 'observe'):
            self.cursor.execute.reset_mock()
            response = self.client.post('/api/teacher/learning-support/1', json={'action': action, 'note': '关心学生'}, headers={'Role': 'teacher'})
            self.assertEqual(response.status_code, 200)
            sql = [call.args for call in self.cursor.execute.call_args_list]
            profile = [entry for entry in sql if 'INSERT INTO student_learning_support' in entry[0]]
            self.assertEqual(len(profile), 0 if action == 'observe' else 1)
            if profile:
                self.assertEqual(profile[0][1], (7, action, 7))
            self.assertTrue(any('INSERT INTO learning_support_actions' in entry[0] for entry in sql))

    def test_failed_audit_rolls_back_difficulty(self):
        self.cursor.execute.side_effect = [None, None, None, RuntimeError('write failed')]
        with self.assertRaises(RuntimeError):
            self.client.post('/api/teacher/learning-support/1', json={'action': 'easy'}, headers={'Role': 'teacher'})
        self.conn.rollback.assert_called_once()
        self.conn.commit.assert_not_called()

    def test_emotion_validates_and_signals_only_sad(self):
        with self.app.test_request_context():
            self.support.record_emotion(7, {'mood': '/images/Mood_Diary/happy.jpg'})
            self.assertEqual(self.execute.call_count, 1)
            self.execute.reset_mock()
            self.support.record_emotion(7, {'mood': '/images/Mood_Diary/sad.jpg'})
            self.assertEqual(self.execute.call_count, 2)
            self.assertEqual(self.execute.call_args.args[1][1], 'mood')
            response = self.support.record_emotion(7, {'mood': '/images/Mood_Diary/sad.jpg', 'date': 'not-a-date'})
            self.assertEqual(response[1], 400)

    def test_alert_upsert_preserves_teacher_handling(self):
        self.support.signal(7, 'score', '低分')
        sql = self.execute.call_args.args[0]
        self.assertIn('ON DUPLICATE KEY UPDATE', sql)
        self.assertNotIn('status=', sql)


class QuizIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()
        self.headers = {'Authorization': 'Bearer test_student_7'}
        self.questions = [{'question': '基础概念', 'options': ['A', 'B', 'C', 'D'], 'answer': 0, 'explanation': '说明'}]

    def test_easy_bypasses_shared_cache_and_keeps_grade(self):
        with patch.object(server.learning_support, 'difficulty', return_value='easy'), \
             patch.object(server, 'query', return_value={'grade_level': 'middle_school'}) as query, \
             patch.object(server.llm_service, 'generate_quiz', return_value=self.questions) as generate, \
             patch.object(server, 'execute') as execute:
            response = self.client.post('/api/student/ai/quiz/generate', json={'topic': 'AI', 'courseId': 1}, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['difficulty'], 'easy')
            generate.assert_called_once_with('AI', 'middle_school', 3, difficulty='easy')
            self.assertEqual(query.call_count, 1)
            execute.assert_not_called()

    def test_normal_uses_course_cache(self):
        import json
        with patch.object(server.learning_support, 'difficulty', return_value='normal'), \
             patch.object(server, 'query', side_effect=[{'grade_level': 'middle_school'}, {'quiz_content': json.dumps([self.questions])}]), \
             patch.object(server.llm_service, 'generate_quiz') as generate:
            response = self.client.post('/api/student/ai/quiz/generate', json={'topic': 'AI', 'courseId': 1}, headers=self.headers)
            self.assertTrue(response.json['fromCache'])
            generate.assert_not_called()

    def test_low_score_alert_and_passing_score(self):
        with patch.object(server, 'execute'), patch.object(server.learning_support, 'signal') as signal:
            for answer in (1, 0):
                response = self.client.post('/api/student/ai/quiz/grade', json={'questions': self.questions, 'answers': [answer]}, headers=self.headers)
                self.assertEqual(response.status_code, 200)
            signal.assert_called_once()
            self.assertEqual(signal.call_args.args[1], 'score')

    def test_empty_quiz_does_not_raise_alert(self):
        with patch.object(server, 'execute') as execute, patch.object(server.learning_support, 'signal') as signal:
            response = self.client.post('/api/student/ai/quiz/grade', json={'questions': [], 'answers': []}, headers=self.headers)
            self.assertEqual(response.status_code, 400)
            execute.assert_not_called()
            signal.assert_not_called()

    def test_easy_generation_failure_does_not_fall_back_to_harder_cache(self):
        with patch.object(server.learning_support, 'difficulty', return_value='easy'), \
             patch.object(server, 'query', return_value={'grade_level': 'middle_school'}), \
             patch.object(server.llm_service, 'generate_quiz', return_value=[{'question': '题目生成失败，请重试'}]):
            response = self.client.post('/api/student/ai/quiz/generate', json={'topic': 'AI'}, headers=self.headers)
            self.assertEqual(response.status_code, 503)


if __name__ == '__main__':
    unittest.main()
