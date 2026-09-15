import sys, json, ast
sys.dont_write_bytecode = True
sys.path.insert(0, r'D:\GITHUB\aupet-new\backend')
import app
client = app.app.test_client()
assert client.post('/api/student/ai/programming-tutor',json={'question':'test'}).status_code == 401
headers={'Authorization':'Bearer test_student_1'}
assert client.post('/api/student/ai/programming-tutor',json={},headers=headers).status_code == 400
assert client.get('/api/student/ai/programming-tutor',headers=headers).status_code == 200
captured=[]
app.llm_service._call_api=lambda messages, **kwargs: captured.append(messages) or '先考虑中间两项的下标。'
response=client.post('/api/student/ai/programming-tutor',headers=headers,json={'question':'中位数怎么求？','course':'Python数据分析','language':'Python','task':{'title':'寻找中位数'},'code':'values = [1, 2]','history':[{'role':'user','content':'怎么开始？'}]})
assert response.status_code == 200
assert response.json['answer']=='先考虑中间两项的下标。'
assert 'Python数据分析' in captured[0][1]['content']
assert any(message.get('content')=='怎么开始？' for message in captured[0])
print('Authenticated tutor API and course context checks passed')
