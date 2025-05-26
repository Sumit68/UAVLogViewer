/* eslint-disable */
import React, { useState } from 'react'

function ChatBot () {
    const [input, setInput] = useState('')
    const [chat, setChat] = useState([])

    const sendMessage = async () => {
        if (!input.trim()) return

        const userMessage = { sender: 'user', text: input }
        setChat([...chat, userMessage])

        const res = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input })
        })

        const data = await res.json()
        const botMessage = { sender: 'bot', text: data.response || 'Error fetching response' }
        setChat([...chat, userMessage, botMessage])
        setInput('')
    }

    return (
        <div style={{ padding: 16, border: '1px solid #ccc', width: 400 }}>
            <h3>Chat with UAV Assistant</h3>
            <div style={{ maxHeight: 200, overflowY: 'auto', marginBottom: 8 }}>
                {chat.map((msg, idx) => (
                    <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
                        <strong>{msg.sender === 'user' ? 'You' : 'Bot'}:</strong> {msg.text}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask me anything..."
                style={{ width: '100%', marginBottom: 8 }}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    )
}

export default ChatBot
