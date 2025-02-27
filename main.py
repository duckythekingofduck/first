from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, join_room, leave_room, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, datetime

# Configuration
IP = "37.60.242.197"
PORT = 8000
SECRET_KEY = "rachat_spicy"
# Use your MongoDB Atlas connection; here we use database "rachat"
MONGO_URI = "mongodb+srv://killer:killer1699@killer.ofoul.mongodb.net/rachat?retryWrites=true&w=majority"

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["MONGO_URI"] = MONGO_URI
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")

mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Helper function: Generate default avatar URL using first 3 letters of username
def get_default_avatar(username):
    initials = username[:3].upper()
    # Using a placeholder service
    return f"https://via.placeholder.com/100?text={initials}"

# --------------------------
# Routes
# --------------------------
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("chat"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if mongo.db.users.find_one({"username": username}):
            return "Username already taken!", 400
        hashed_pw = generate_password_hash(password)
        avatar = get_default_avatar(username)
        mongo.db.users.insert_one({
            "username": username,
            "password": hashed_pw,
            "avatar": avatar
        })
        session["user"] = username
        return redirect(url_for("chat"))
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = mongo.db.users.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        session["user"] = username
        return redirect(url_for("chat"))
    return "Invalid login!", 401

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect(url_for("index"))
    current_user = mongo.db.users.find_one({"username": session["user"]})
    avatar = current_user.get("avatar", get_default_avatar(session["user"]))
    # Retrieve all other users for the DM list
    users = list(mongo.db.users.find({"username": {"$ne": session["user"]}}, {"_id": 0, "username": 1, "avatar": 1}))
    return render_template("chat.html", username=session["user"], avatar=avatar, users=users)

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("index"))
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    # Update user avatar to the uploaded image (using relative path)
    mongo.db.users.update_one({"username": session["user"]}, {"$set": {"avatar": "/" + filepath}})
    return redirect(url_for("chat"))

# --------------------------
# Socket.IO Events
# --------------------------
@socketio.on("join")
def handle_join(data):
    room = data["room"]
    username = data["username"]
    join_room(room)
    emit("status", {"msg": f"{username} has joined {room}."}, room=room)

@socketio.on("message")
def handle_message(data):
    room = data["room"]
    msg = data["message"]
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    # Save message with room info (group chat vs DM)
    mongo.db.messages.insert_one({
        "room": room,
        "sender": data["username"],
        "message": msg,
        "timestamp": timestamp
    })
    emit("message", {"username": data["username"], "message": msg, "timestamp": timestamp}, room=room)

@socketio.on("leave")
def handle_leave(data):
    room = data["room"]
    username = data["username"]
    leave_room(room)
    emit("status", {"msg": f"{username} has left {room}."}, room=room)

# --------------------------
# Run the App
# --------------------------
if __name__ == "__main__":
    socketio.run(app, host=IP, port=PORT, debug=True)
