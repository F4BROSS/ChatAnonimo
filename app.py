from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = 'seu_segredo_aqui'

# Simulação de banco de dados em memória
users = {}  # {"username": "ip_address"}
online_users = {}  # {"username": last_activity_time}
chat_messages = {}  # {"user1_user2": [{"sender": "user1", "message": "msg", "seen": False}]}

def is_termux():
    return os.environ.get('TERMUX') is not None

def update_user_status(username):
    online_users[username] = datetime.now()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username in users:
            if users[username] == request.remote_addr:
                session['username'] = username
                update_user_status(username)
                return redirect(url_for('home'))
            else:
                return "Nome de usuário já está em uso por outra pessoa!", 400
        else:
            users[username] = request.remote_addr
            session['username'] = username
            update_user_status(username)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        search_user = request.form['search_user']
        if search_user in users and search_user != session['username']:
            session['chat_with'] = search_user
            update_user_status(session['username'])
            return redirect(url_for('chat'))
        else:
            return "Usuário não encontrado ou não pode conversar consigo mesmo!", 400

    return render_template('home.html', username=session['username'])

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session or 'chat_with' not in session:
        return redirect(url_for('home'))

    user1 = session['username']
    user2 = session['chat_with']
    chat_id = "_".join(sorted([user1, user2]))

    if request.method == 'POST':
        message = request.form['message']
        if chat_id not in chat_messages:
            chat_messages[chat_id] = []
        chat_messages[chat_id].append({"sender": user1, "message": message, "seen": False})
    
    for msg in chat_messages.get(chat_id, []):
        if msg['sender'] != user1:
            msg['seen'] = True

    chat_history = chat_messages.get(chat_id, [])
    update_user_status(user1)

    return render_template('chat.html', chat_with=user2, chat_history=chat_history, online_users=online_users)

@app.route('/delete_user')
def delete_user():
    username = session.pop('username', None)
    if username in users:
        del users[username]
        online_users.pop(username, None)
    return redirect(url_for('login'))

@app.route('/leave_chat')
def leave_chat():
    session.pop('chat_with', None)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('chat_with', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = random.randint(8000, 9000)  # Gera uma porta aleatória entre 8000 e 9000
    if is_termux():
        app.run(host="0.0.0.0", port=port)
    else:
        app.run(host="127.0.0.1", port=port, debug=True)