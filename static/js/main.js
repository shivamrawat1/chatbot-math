document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');

    // Handle Send Button Click
    sendButton.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (message) {
            appendMessage('You', message, 'user-message');
            userInput.value = '';
            getResponse(message);
        }
    });

    // Handle Enter Key Press
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });

    // Speech Recognition
    micButton.addEventListener('click', () => {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'en-US';
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                sendButton.click();
            };
            recognition.start();
        } else {
            alert('Speech recognition not supported in this browser.');
        }
    });

    // Append Message to Chat Box
    function appendMessage(sender, message, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Get Response from Server
    function getResponse(message) {
        fetch('/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'message': message })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage('Assistant', data.message, 'assistant-message');
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('Assistant', 'Sorry, an error occurred.', 'assistant-message');
        });
    }
});
