import unittest
from unittest.mock import patch
import app
import llm_service


class TeacherIdentityTests(unittest.TestCase):
    def test_grade_identity_and_prompt(self):
        for grade, name in [('lower_primary', '小知老师'), ('upper_primary', '小知老师'),
                            ('middle_school', '知行老师'), ('high_school', '知行老师')]:
            self.assertEqual(llm_service.teacher_name(grade), name)
            with patch.object(llm_service, '_call_api', return_value='reply') as api:
                llm_service.chat('你好', grade, pet_name=name, scene='learning')
                self.assertIn(name, api.call_args.args[0][0]['content'])
                self.assertNotIn('宠物', api.call_args.args[0][0]['content'])
                llm_service.generate_course_guide('人工智能', grade)
                self.assertIn(name, api.call_args.args[0][0]['content'])

    def test_companion_retains_pet(self):
        with patch.object(llm_service, '_call_api', return_value='reply') as api:
            llm_service.chat('今天有点累', pet_name='毛球')
            prompt = api.call_args.args[0][0]['content']
            self.assertIn('宠物伙伴毛球', prompt)
            self.assertNotIn('小知老师', prompt)

    def test_clear_is_scoped(self):
        with patch.object(app, 'execute') as execute:
            client = app.app.test_client()
            for suffix, scene in [('?scene=learning', 'learning'), ('', 'companion')]:
                response = client.post('/api/student/chat/clear' + suffix,
                                       headers={'Authorization': 'Bearer test_student_7'})
                self.assertEqual(response.status_code, 200)
                self.assertIn('AND scene=%s', execute.call_args.args[0])
                self.assertEqual(execute.call_args.args[1], (7, scene))


if __name__ == '__main__':
    unittest.main()
