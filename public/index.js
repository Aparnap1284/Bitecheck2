// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Animate feature cards when scrolled into view
    const featureCards = document.querySelectorAll('.feature-card');
    const stepCards = document.querySelectorAll('.step-card');
    const testimonials = document.querySelectorAll('.testimonial');
    const faqItems = document.querySelectorAll('.faq-item');
    
    // Initialize Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });
    
    // Add appear-on-scroll class and observe all elements that should animate
    function setupAnimatedElements(elements, delay = 0) {
        elements.forEach((el, index) => {
            el.classList.add('appear-on-scroll');
            el.style.transitionDelay = `${delay + (index * 0.15)}s`;
            observer.observe(el);
        });
    }
    
    setupAnimatedElements(featureCards);
    setupAnimatedElements(stepCards, 0.2);
    setupAnimatedElements(testimonials, 0.3);
    setupAnimatedElements(faqItems, 0.1);
    
    // Animate food items randomly
    const foodItems = document.querySelectorAll('.food-item');
    foodItems.forEach(item => {
        // Random float animation timing
        const randomDuration = 2 + Math.random() * 2;
        const randomDelay = Math.random() * 1;
        item.style.animationDuration = `${randomDuration}s, ${randomDuration}s`;
        item.style.animationDelay = `${randomDelay}s, ${randomDelay}s`;
    });
    
    // Add confetti effect when CTA button is clicked
    const ctaButton = document.querySelector('.cta-btn');
    if (ctaButton) {
        ctaButton.addEventListener('click', function() {
            createConfetti();
        });
    }
    
    // Chat bot animation and functionality
    const chatbot = document.getElementById('chatbot');
    if (chatbot) {
        // Animate chatbot entrance
        setTimeout(() => {
            chatbot.style.animation = 'bounceIn 0.8s forwards';
        }, 2000);
        
        // Create chat window element
        const chatWindow = document.createElement('div');
        chatWindow.classList.add('chat-window');
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-title">BiteCheck Assistant</div>
                <div class="chat-close">×</div>
            </div>
            <div class="chat-messages">
                <div class="message bot">
                    <div class="message-avatar">🤖</div>
                    <div class="message-bubble">
                        Hello! I'm your BiteCheck assistant. How can I help you with your food journey today?
                    </div>
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" placeholder="Type your message...">
                <button class="chat-send">➡️</button>
            </div>
        `;
        chatWindow.style.display = 'none';
        document.body.appendChild(chatWindow);
        
        // Add chat functionality
        chatbot.addEventListener('click', function() {
            if (chatWindow.style.display === 'none') {
                chatWindow.style.display = 'flex';
                chatWindow.style.animation = 'slideInUp 0.5s forwards';
                chatbot.style.animation = 'pulse 1s infinite';
            } else {
                chatWindow.style.animation = 'slideOutDown 0.5s forwards';
                setTimeout(() => {
                    chatWindow.style.display = 'none';
                }, 500);
                chatbot.style.animation = '';
            }
        });
        
        // Close button functionality
        const chatClose = chatWindow.querySelector('.chat-close');
        chatClose.addEventListener('click', function(e) {
            e.stopPropagation();
            chatWindow.style.animation = 'slideOutDown 0.5s forwards';
            setTimeout(() => {
                chatWindow.style.display = 'none';
            }, 500);
            chatbot.style.animation = '';
        });
        
        // Send message functionality
        const chatInput = chatWindow.querySelector('.chat-input');
        const chatSend = chatWindow.querySelector('.chat-send');
        const chatMessages = chatWindow.querySelector('.chat-messages');
        
        function sendMessage() {
            const message = chatInput.value.trim();
            if (message !== '') {
                // Add user message
                const userMessage = document.createElement('div');
                userMessage.classList.add('message', 'user');
                userMessage.innerHTML = `
                    <div class="message-bubble">
                        ${message}
                    </div>
                `;
                chatMessages.appendChild(userMessage);
                chatInput.value = '';
                
                // Auto scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Simulate typing indicator
                const typingIndicator = document.createElement('div');
                typingIndicator.classList.add('message', 'bot', 'typing');
                typingIndicator.innerHTML = `
                    <div class="message-avatar">🤖</div>
                    <div class="message-bubble">
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                `;
                chatMessages.appendChild(typingIndicator);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Simulate response after delay
                setTimeout(() => {
                    chatMessages.removeChild(typingIndicator);
                    
                    // Sample responses based on keyword matching
                    let botResponse = "I'm sorry, I don't understand that question. Can you ask about our food tracking or scanning features?";
                    
                    const lowerMessage = message.toLowerCase();
                    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
                        botResponse = "Hello there! How can I help you with your food journey today?";
                    } else if (lowerMessage.includes('allerg')) {
                        botResponse = "BiteCheck can detect common allergens like nuts, dairy, gluten, and more! Just scan the label and we'll alert you to potential risks.";
                    } else if (lowerMessage.includes('scan') || lowerMessage.includes('how')) {
                        botResponse = "Simply take a picture of any food label using our app and our AI will analyze it instantly! Want to try our demo?";
                    } else if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('free')) {
                        botResponse = "BiteCheck offers a free basic plan with 10 scans per month. Our premium plan is just $4.99/month for unlimited scans and personalized recommendations!";
                    }
                    
                    const botMessageEl = document.createElement('div');
                    botMessageEl.classList.add('message', 'bot');
                    botMessageEl.innerHTML = `
                        <div class="message-avatar">🤖</div>
                        <div class="message-bubble">
                            ${botResponse}
                        </div>
                    `;
                    chatMessages.appendChild(botMessageEl);
                    
                    // Add cute food emoji animation to response
                    const foodEmoji = document.createElement('div');
                    foodEmoji.classList.add('food-emoji-animation');
                    const emojis = ['🍎', '🥕', '🥑', '🥦', '🍇', '🥗'];
                    foodEmoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                    botMessageEl.appendChild(foodEmoji);
                    
                    // Auto scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 1500);
            }
        }
        
        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Add "wiggle" animation to CTA buttons on hover
    const allCTAButtons = document.querySelectorAll('.cta-button, .cta-btn');
    allCTAButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.animation = 'wiggle 0.5s ease';
        });
        
        button.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });
    
    // Add parallax effect to hero section
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.pageYOffset;
            const heroItems = heroSection.querySelectorAll('.food-item');
            
            heroItems.forEach((item, index) => {
                const speed = 0.05 + (index * 0.01);
                const yPos = -scrollPosition * speed;
                item.style.transform = `translateY(${yPos}px)`;
            });
        });
    }
});

// Create confetti effect
function createConfetti() {
    const confettiContainer = document.createElement('div');
    confettiContainer.classList.add('confetti-container');
    document.body.appendChild(confettiContainer);
    
    const colors = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#ff8c8c', '#6bffd3'];
    
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.classList.add('confetti');
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDuration = `${Math.random() * 2 + 2}s`;
        confetti.style.animationDelay = `${Math.random() * 0.5}s`;
        confettiContainer.appendChild(confetti);
    }
    
    setTimeout(() => {
        document.body.removeChild(confettiContainer);
    }, 4000);
}

// Add these CSS styles dynamically for new animations
const newStyles = document.createElement('style');
newStyles.textContent = `
    @keyframes bounceIn {
        0% { transform: scale(0); opacity: 0; }
        60% { transform: scale(1.2); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes slideInUp {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideOutDown {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(50px); opacity: 0; }
    }
    
    @keyframes wiggle {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(3deg); }
        50% { transform: rotate(0deg); }
        75% { transform: rotate(-3deg); }
        100% { transform: rotate(0deg); }
    }
    
    .chat-window {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 320px;
        height: 400px;
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 5px 30px rgba(0, 0, 0, 0.2);
        z-index: 999;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-header {
        background-color: var(--primary);
        color: white;
        padding: 12px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
    }
    
    .chat-close {
        cursor: pointer;
        font-size: 24px;
    }
    
    .chat-messages {
        flex: 1;
        padding: 15px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    .message {
        display: flex;
        align-items: flex-start;
        max-width: 80%;
    }
    
    .message.bot {
        align-self: flex-start;
    }
    
    .message.user {
        align-self: flex-end;
        justify-content: flex-end;
    }
    
    .message-avatar {
        background-color: var(--primary);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 8px;
    }
    
    .message-bubble {
        background-color: #f0f0f0;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-left-radius: 0;
        font-size: 14px;
    }
    
    .message.user .message-bubble {
        background-color: var(--primary);
        color: white;
        border-radius: 15px;
        border-bottom-right-radius: 0;
    }
    
    .chat-input-area {
        display: flex;
        padding: 10px;
        border-top: 1px solid #e0e0e0;
    }
    
    .chat-input {
        flex: 1;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        outline: none;
    }
    
    .chat-send {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        margin-left: 10px;
        cursor: pointer;
    }
    
    .typing-indicator {
        display: flex;
        padding: 5px 0;
    }
    
    .typing-indicator span {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #888;
        border-radius: 50%;
        margin-right: 5px;
        animation: typingAnimation 1s infinite ease-in-out;
    }
    
    .typing-indicator span:nth-child(1) {
        animation-delay: 0s;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
        margin-right: 0;
    }
    
    @keyframes typingAnimation {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .confetti-container {
        position: fixed;
        top: -20px;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
    }
    
    .confetti {
        position: absolute;
        width: 10px;
        height: 10px;
        opacity: 0.8;
        animation: confettiFall linear forwards;
    }
    
    @keyframes confettiFall {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
    }
    
    .food-emoji-animation {
        position: absolute;
        right: -15px;
        top: -15px;
        animation: foodEmojiFloat 2s ease-out forwards;
        font-size: 20px;
    }
    
    @keyframes foodEmojiFloat {
        0% { transform: translateY(0) scale(0); opacity: 0; }
        50% { transform: translateY(-20px) scale(1.2); opacity: 1; }
        100% { transform: translateY(-40px) scale(1); opacity: 0; }
    }
`;
document.head.appendChild(newStyles);