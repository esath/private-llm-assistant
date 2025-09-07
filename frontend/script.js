document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');

    // --- CONFIGURATION ---
    // In a real K8s deployment, this URL should point to the backend service.
    // If you are running locally, it's 'http://localhost:5000/api/chat'.
    // The '/api/chat' is a placeholder that will be proxied by Nginx in the Docker container.
    // Allow overriding API URL (e.g., window.API_URL = 'http://localhost:5000/api/chat')
    const resolveApiUrl = () => {
        if (window.API_URL && typeof window.API_URL === 'string') return window.API_URL;
        const host = window.location.hostname;
        const isLocalHost =
            host === 'localhost' ||
            host === '127.0.0.1' ||
            host === '::1';
        return isLocalHost ? 'http://localhost:5000/api/chat' : '/api/chat';
    };
    const API_URL = resolveApiUrl();
    const HEALTH_URL = API_URL.replace(/\/chat$/, '/health');
    console.debug('[frontend] Using API_URL =', API_URL);

    const showSystemMessage = (text) => {
        const msg = document.createElement('div');
        msg.classList.add('message', 'system');
        const p = document.createElement('p');
        p.textContent = text;
        msg.appendChild(p);
        chatMessages.appendChild(msg);
    };

    const fetchWithTimeout = (url, opts = {}, ms = 5000) => {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), ms);
        const merged = { ...opts, signal: controller.signal };
        return fetch(url, merged).finally(() => clearTimeout(id));
    };

    // Probe backend on load and surface actionable hint if unreachable.
    fetchWithTimeout(HEALTH_URL, { method: 'GET' }, 4000)
        .then((r) => {
            if (!r.ok) throw new Error(`Health check failed: ${r.status}`);
        })
        .catch(() => {
            showSystemMessage(
                `Backend not reachable at ${HEALTH_URL}. Ensure the backend runs on port 5000 (python app.py), or set window.API_URL in index.html to a reachable URL.`
            );
        });

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
                const details = await response.text().catch(() => '');
                throw new Error(`API Error ${response.status}: ${details || response.statusText}`);
            }
            
            // Handle the streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedResponse = '';
            const renderMarkdown = (text) => {
                if (window.marked && typeof window.marked.parse === 'function') {
                    return window.marked.parse(text);
                }
                // Fallback: plain text if marked is unavailable
                return null;
            };

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                accumulatedResponse += decoder.decode(value, { stream: true });
                const html = renderMarkdown(accumulatedResponse);
                if (html !== null) {
                    botParagraph.innerHTML = html;
                } else {
                    botParagraph.textContent = accumulatedResponse;
                }
                scrollToBottom();
            }

        } catch (error) {
            console.error('Error fetching chat response:', error);
            const networkHint = error.name === 'TypeError'
                ? `Cannot reach ${API_URL}. Check backend is running and CORS/URL are correct.`
                : '';
            botParagraph.textContent = `Sorry, something went wrong. ${error.message || ''} ${networkHint}`;
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
