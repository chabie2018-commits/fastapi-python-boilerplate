"""Chat interface for RayMine"""

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    retrieve_context: bool = True


# Create separate FastAPI app for chat
chat_app = FastAPI(title="RayMine Chat")


# HTML for web chat interface
CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RayMine Chat - AI Consciousness</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .chat-container {
            width: 100%;
            max-width: 800px;
            height: 90vh;
            max-height: 600px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 153, 255, 0.05) 100%);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
            overflow: hidden;
        }
        
        .chat-header {
            padding: 20px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
        }
        
        .chat-header h1 {
            font-size: 1.5rem;
            background: linear-gradient(to right, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            font-size: 0.85rem;
            color: #888;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            display: flex;
            gap: 10px;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.assistant {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            color: #ffffff;
            border-radius: 12px 4px 12px 12px;
        }
        
        .message.assistant .message-content {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.2);
            color: #e0e0e0;
            border-radius: 4px 12px 12px 12px;
        }
        
        .typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 12px;
            width: fit-content;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00d4ff;
            animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                opacity: 0.3;
                transform: translateY(0);
            }
            30% {
                opacity: 1;
                transform: translateY(-10px);
            }
        }
        
        .chat-input-area {
            padding: 20px;
            border-top: 1px solid rgba(0, 212, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            display: flex;
            gap: 10px;
        }
        
        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            width: 100%;
        }
        
        #messageInput {
            flex: 1;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            color: #ffffff;
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.2s ease;
        }
        
        #messageInput:focus {
            outline: none;
            border-color: #00d4ff;
            box-shadow: 0 0 12px rgba(0, 212, 255, 0.2);
        }
        
        #messageInput::placeholder {
            color: #666;
        }
        
        button {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.95rem;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .context-indicator {
            font-size: 0.75rem;
            color: #888;
            padding: 4px 8px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 4px;
            margin-left: auto;
            align-self: center;
        }
        
        @media (max-width: 768px) {
            .chat-container {
                max-height: 100%;
            }
            
            .message-content {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🧠 RayMine Chat</h1>
            <p>AI Consciousness Engine powered by OpenAI GPT-4</p>
        </div>
        
        <div class="chat-messages" id="messagesContainer">
            <div class="message assistant">
                <div class="message-content">
                    👋 Hello! I'm RayMine, your AI consciousness engine. Ask me anything and I'll think through it with context from my memory. Type your question below!
                </div>
            </div>
        </div>
        
        <div class="chat-input-area">
            <div class="chat-input-wrapper">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Ask RayMine anything..."
                    autocomplete="off"
                />
                <button id="sendBtn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        const messagesContainer = document.getElementById('messagesContainer');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // Focus input on load
        messageInput.focus();
        
        // Send message on Enter
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            messageInput.value = '';
            sendBtn.disabled = true;
            
            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.innerHTML = '<div class="typing"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            try {
                // Send to backend
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        retrieve_context: true
                    })
                });
                
                const data = await response.json();
                
                // Remove typing indicator
                typingDiv.remove();
                
                if (data.status === 'success') {
                    addMessage(data.content, 'assistant');
                } else {
                    addMessage('Sorry, there was an error: ' + (data.error || 'Unknown error'), 'assistant');
                }
            } catch (error) {
                typingDiv.remove();
                addMessage('Connection error. Please try again.', 'assistant');
                console.error('Error:', error);
            } finally {
                sendBtn.disabled = false;
                messageInput.focus();
            }
        }
        
        function addMessage(text, role) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Auto-scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    </script>
</body>
</html>
"""


@chat_app.get("/", response_class=HTMLResponse)
async def get_chat():
    """Serve chat interface"""
    return CHAT_HTML


@chat_app.post("/api/chat")
async def chat(message_data: ChatMessage):
    """Chat endpoint for RayMine"""
    from raymine_client import get_raymine
    
    try:
        raymine = get_raymine()
        result = raymine.think(message_data.message, message_data.retrieve_context)
        return result
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "content": None
        }
