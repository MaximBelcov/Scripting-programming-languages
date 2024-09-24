import requests
import json

url = 'https://jsonplaceholder.typicode.com/posts'

new_post = {
    'UserId': 1,
    'title': 'Тестовый пост',
    'body': 'Это содержимое тестового поста. Здесь может быть любой текст.'
}

requestsPost = requests.post(url, json=new_post)

if requestsPost.status_code == 201:
    created_post = requestsPost.json()
    print("Новый пост:")
    print(json.dumps(created_post, indent=4, ensure_ascii=False))
else:
    print(f"Не удалось создать пост. Статус код: {requestsPost.status_code}")
