from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, join_room, leave_room, send
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://killer:killer1699@killer.ofoul.mongodb.net/?retryWrites=true&w=majority"
app.config["SECRET_KEY"] = "rachat_spicy"
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # Store user sessions

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({"username": username})
        if user:
            return "User already exists!"
        mongo.db.users.insert_one({"username": username, "password": password})
        return redirect(url_for('index'))
    return render_template("register.html")

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template("chat.html", username=session['username'])

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    send(f"{username} has joined the chat.", room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    send(message, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)
    send(f"{username} has left the chat.", room=room)

if __name__ == '__main__':
    socketio.run(app, host="37.60.242.197", port=8000, debug=True)
