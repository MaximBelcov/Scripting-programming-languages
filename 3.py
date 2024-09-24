import requests
import json

post_id = 101
url = f'https://jsonplaceholder.typicode.com/posts/{post_id}'

updated_post = {
    'userId': 1,
    'title': 'Обновлённый пост',
    'body': 'Это обновленное содержимое тестового поста.'
}

requestsPut = requests.put(url, json=updated_post)

if requestsPut.status_code == 200:
    updated_post_response = requestsPut.json()
    print("Обновленный пост:")
    print(json.dumps(updated_post_response, indent=4, ensure_ascii=False))
else:
    print(f"Не удалось обновить пост. Статус код: {requestsPut.status_code}")