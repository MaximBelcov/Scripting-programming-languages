import requests

url = 'https://jsonplaceholder.typicode.com/posts'

requestsGet = requests.get(url)

if requestsGet.status_code == 200:
    posts = requestsGet.json()
    even_user_posts = [post for post in posts if post['userId'] % 2 == 0]

    for post in even_user_posts:
        print(f"UserId: {post['userId']},\nPostId: {post['id']},\nTitle: {post['title']},\nBody: {post['body']}\n")
else:
    print(f"Не удалось получить данные. Статус код: {requestsGet.status_code}")