document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');

    // --- CONFIGURATION ---
    // In a real K8s deployment, this URL should point to the backend service.
    // If you are running locally, it's 'http://localhost:5000/api/chat'.
    // The '/api/chat' is a placeholder that will be proxied by Nginx in the Docker container.
    const API_URL = '/api/chat';

    const sendMessage = async () => {
        const question = chatInput.value.trim();
        if (!question) return;

        // Disable input and show loading indicator
        chatInput.value = '';
        chatInput.disabled = true;
        sendButton.disabled = true;
        loadingIndicator.classList.remove('hidden');

        // Add user message to chat window
        appendMessage(question, 'user');

        // Create a container for the bot's response
        const botMessageContainer = appendMessage('', 'bot');
        const botParagraph = botMessageContainer.querySelector('p');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }
            
            // Handle the streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedResponse = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                accumulatedResponse += decoder.decode(value, { stream: true });
                // Use marked.js to render Markdown in real-time
                botParagraph.innerHTML = marked.parse(accumulatedResponse);
                scrollToBottom();
            }

        } catch (error) {
            console.error('Error fetching chat response:', error);
            botParagraph.innerHTML = 'Sorry, something went wrong. Please check the console for details.';
        } finally {
            // Re-enable input and hide loading indicator
            chatInput.disabled = false;
            sendButton.disabled = false;
            loadingIndicator.classList.add('hidden');
            chatInput.focus();
            scrollToBottom();
        }
    };

    const appendMessage = (text, sender) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message', sender);
        
        const messageParagraph = document.createElement('p');
        messageParagraph.textContent = text;
        
        messageWrapper.appendChild(messageParagraph);
        chatMessages.appendChild(messageWrapper);
        scrollToBottom();
        return messageWrapper;
    };

    const scrollToBottom = () => {
        const chatWindow = document.getElementById('chat-window');
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };
    
    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    });

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
