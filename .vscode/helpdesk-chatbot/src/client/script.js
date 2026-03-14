// This file contains the client-side JavaScript code that handles user interactions with the chatbot, sends messages to the server, and updates the UI with responses.

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const userMessage = chatInput.value.trim();
        if (userMessage) {
            appendMessage('You', userMessage);
            chatInput.value = '';

            const response = await sendMessageToServer(userMessage);
            appendMessage('Bot', response);
        }
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
    }

    async function sendMessageToServer(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
            const data = await response.json();
            return data.reply || 'Sorry, I did not understand that.';
        } catch (error) {
            console.error('Error sending message:', error);
            return 'Error communicating with the server.';
        }
    }
});