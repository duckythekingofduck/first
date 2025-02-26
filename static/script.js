var socket = io.connect("http://37.60.242.197:8000");

socket.on("message", function(msg) {
    var chatBox = document.getElementById("chat-box");
    var newMessage = document.createElement("p");
    newMessage.innerText = msg;
    chatBox.appendChild(newMessage);
});

function sendMessage() {
    var messageInput = document.getElementById("message");
    socket.emit("message", { message: messageInput.value });
    messageInput.value = "";
}
