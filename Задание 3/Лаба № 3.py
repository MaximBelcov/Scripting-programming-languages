import sqlite3
import requests

# 1
def create_database():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        body TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# 2
def fetch_posts():
    url = 'https://jsonplaceholder.typicode.com/posts'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Ошибка при получении данных:", response.status_code)
        return []

# 3
def save_posts_to_db(posts):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts')
    for post in posts:

        cursor.execute('''
        INSERT INTO posts (id, user_id, title, body)
        VALUES (?, ?, ?, ?)
        ''', (post['id'], post['userId'], post['title'], post['body']))
    
    conn.commit()
    conn.close()

# 4
def get_posts_by_user(user_id):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
    posts = cursor.fetchall()
    conn.close()
    
    return posts

if __name__ == "__main__":
    create_database()
    posts = fetch_posts()
    save_posts_to_db(posts)
    
    user_id = 1
    user_posts = get_posts_by_user(user_id)
    for post in user_posts:
        print(post)