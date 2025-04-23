from requests import get, post, delete

print(post('http://localhost:5000/api/v2/work',
           json={'title': 'test', 'content': 'test', 'experience': 'test', 'colab': "test", 'is_private': 1,
                 'user_id': 1}).json())

print(post('http://localhost:5000/api/v2/work',
           json={'title': 'ete', 'content': 'ete', 'experience': '', 'colab': "", 'is_private': 1,
                 'user_id': 1, 'takogo nety': "a?"}).json())

print(post('http://localhost:5000/api/v2/work', json={}).json())

print(get('http://localhost:5000/api/v2/work').json())

print(get('http://localhost:5000/api/v2/work/2').json())

print(get('http://localhost:5000/api/v2/work/999').json())

print(get('http://localhost:5000/api/v2/work/q').json())

print(delete('http://localhost:5000/api/v2/work/999').json())

print(delete('http://localhost:5000/api/v2/work/qqq').json())

print(delete('http://localhost:5000/api/v2/work/12').json())
