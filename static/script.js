// Initialize Socket.IO connection
const socket = io();

// Default room is the global group chat
let currentRoom = "global";

// When a user selects a room (global or DM)
function selectRoom(room) {
  currentRoom = room;
  document.getElementById("chat-box").innerHTML = ""; // clear chat box on room switch
  socket.emit("join", { room: currentRoom, username: window.currentUsername });
}

// Send a message using Socket.IO
function sendMessage() {
  const messageInput = document.getElementById("message");
  const message = messageInput.value;
  if (message.trim() === "") return;
  socket.emit("message", { room: currentRoom, username: window.currentUsername, message: message });
  messageInput.value = "";
}

// Listen for incoming messages
socket.on("message", function(data) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message");
  if (data.username === window.currentUsername) {
    msgDiv.classList.add("sent");
  } else {
    msgDiv.classList.add("received");
  }
  msgDiv.innerHTML = `<strong>${data.username}:</strong> ${data.message} <span style="font-size:10px;">${data.timestamp}</span>`;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
});

// Theme switcher function
function toggleTheme() {
  document.body.classList.toggle("dark-mode");
}
