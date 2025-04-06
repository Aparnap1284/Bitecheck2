// This script loads the chatbot and manages its functionality
(function() {
    // Create the chatbot elements
    function createChatbot() {
        // Create main container
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'bitecheck-chatbot';

        // Create chat icon (we'll use the existing one)
        const chatIcon = document.getElementById('chatbot-avatar');
        chatIcon.id = 'bitecheck-chat-icon';

        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'bitecheck-chat-window';

        // Create chat header
        const chatHeader = document.createElement('div');
        chatHeader.id = 'bitecheck-chat-header';
        chatHeader.textContent = 'Chat with BiteCheck';

        // Create messages container
        const chatMessages = document.createElement('div');
        chatMessages.id = 'bitecheck-chat-messages';

        // Create input container
        const chatInputContainer = document.createElement('div');
        chatInputContainer.id = 'bitecheck-chat-input-container';

        // Create text input
        const chatInput = document.createElement('input');
        chatInput.type = 'text';
        chatInput.id = 'bitecheck-chat-input';
        chatInput.placeholder = 'Type your question...';

        // Create send button
        const chatSend = document.createElement('button');
        chatSend.id = 'bitecheck-chat-send';
        
        // Create send icon
        const sendIcon = document.createElement('i');
        sendIcon.className = 'fas fa-paper-plane';
        chatSend.appendChild(sendIcon);

        // Assemble the elements
        chatInputContainer.appendChild(chatInput);
        chatInputContainer.appendChild(chatSend);
        
        chatWindow.appendChild(chatHeader);
        chatWindow.appendChild(chatMessages);
        chatWindow.appendChild(chatInputContainer);
        
        document.body.appendChild(chatWindow);

        // Add styles
        addChatbotStyles();
        
        return {
            chatIcon,
            chatWindow,
            chatMessages,
            chatInput,
            chatSend
        };
    }

    // Add the necessary styles
    function addChatbotStyles() {
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            /* Chatbot styling */
            #bitecheck-chat-icon {
                width: 60px;
                height: 60px;
                background-color: #ff6b6b;
                border-radius: 50%;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 30px;
                cursor: pointer;
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            #bitecheck-chat-window {
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 320px;
                height: 400px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                display: none;
                flex-direction: column;
                overflow: hidden;
                z-index: 1000;
            }
            
            #bitecheck-chat-header {
                background-color: #ff6b6b;
                color: white;
                padding: 12px 15px;
                font-size: 16px;
                font-weight: bold;
            }
            
            #bitecheck-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .bitecheck-message {
                padding: 10px 15px;
                border-radius: 18px;
                max-width: 75%;
                word-wrap: break-word;
            }
            
            .bitecheck-user-message {
                align-self: flex-end;
                background-color: #E3F2FD;
            }
            
            .bitecheck-bot-message {
                align-self: flex-start;
                background-color: #F1F1F1;
            }
            
            #bitecheck-chat-input-container {
                display: flex;
                padding: 10px 15px;
                border-top: 1px solid #E0E0E0;
            }
            
            #bitecheck-chat-input {
                flex: 1;
                padding: 10px 15px;
                border: 1px solid #BDBDBD;
                border-radius: 20px;
                outline: none;
                font-size: 14px;
            }
            
            #bitecheck-chat-send {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                margin-left: 10px;
                cursor: pointer;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            #bitecheck-chat-send i {
                font-size: 16px;
            }
        `;
        document.head.appendChild(styleElement);
    }

    // Initialize the chatbot
    function initChatbot() {
        const elements = createChatbot();
        const {chatIcon, chatWindow, chatMessages, chatInput, chatSend} = elements;
        
        // Toggle chat window
        chatIcon.addEventListener('click', function() {
            const isVisible = chatWindow.style.display === 'flex';
            chatWindow.style.display = isVisible ? 'none' : 'flex';
            
            // Show welcome message when opening for the first time
            if (!isVisible && chatMessages.children.length === 0) {
                addMessage("Hi there! I'm your BiteCheck assistant. How can I help you with your food questions today?", 'bot');
            }
            
            // Focus input when opened
            if (!isVisible) {
                setTimeout(() => chatInput.focus(), 100);
            }
        });
        
        // Send message on button click
        chatSend.addEventListener('click', sendMessage);
        
        // Send message on Enter key
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Send message function
        function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Display user message
            addMessage(message, 'user');
            
            // Clear input
            chatInput.value = '';
            
            // Call API
            fetch('https://bitecheck2.onrender.com/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Display bot response
                if (data && data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage("I'm sorry, I couldn't process your request.", 'bot');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage("Sorry, there was an error connecting to the service. Please try again later.", 'bot');
            });
        }
        
        // Add message to chat
        function addMessage(text, sender) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('bitecheck-message');
            messageElement.classList.add(sender === 'user' ? 'bitecheck-user-message' : 'bitecheck-bot-message');
            messageElement.textContent = text;
            
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Run when the page loads
    document.addEventListener('DOMContentLoaded', initChatbot);
})();