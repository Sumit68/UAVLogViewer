<template>
  <div class="chat-container">
    <div class="chat-header">🛩 UAV Assistant</div>

    <div class="chat-messages" ref="chatBox" :style="{ maxHeight: messages.length ? '400px' : 'auto' }">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="msg.sender"
      >
        <div class="bubble">
          <strong>{{ msg.sender === 'user' ? 'You' : 'Bot' }}:</strong> {{ msg.text }}
        </div>
      </div>
    </div>

    <div class="chat-input">
      <label class="upload-icon">
        📎
        <input
          type="file"
          accept=".bin"
          @change="handleFileUpload"
          style="display: none"
        />
      </label>

      <input
        v-model="input"
        @keyup.enter="sendMessage"
        placeholder="Ask something..."
        class="input-box"
      />
      <button @click="sendMessage" class="send-btn">Send</button>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  data () {
    return {
      input: '',
      messages: [],
      sessionId: null
    }
  },
  methods: {
    async sendMessage () {
      if (!this.input.trim()) return

      const messageToSend = this.input
      this.messages.push({ sender: 'user', text: messageToSend })
      this.input = ''

      try {
        const res = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: messageToSend, session_id: this.sessionId })
        })
        const data = await res.json()
        this.sessionId = data.session_id
        this.messages.push({ sender: 'bot', text: data.response || 'Error' })
      } catch (err) {
        this.messages.push({ sender: 'bot', text: 'Failed to reach server' })
      }
    },
    async handleFileUpload(event) {
  const fileInput = event.target;
  const file = fileInput.files[0];
  if (!file) return;

  this.messages.push({ sender: 'bot', text: '⏳ Loading telemetry data from file...' });

  const formData = new FormData();
  formData.append('file', file);
  if (this.sessionId) formData.append('session_id', this.sessionId);

  try {
    const res = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    this.sessionId = data.session_id;
    this.messages.push({ sender: 'bot', text: data.message });
    
  } catch (err) {
    console.error('Upload error:', err);
    this.messages.push({ sender: 'bot', text: 'Upload or parsing failed.' });
  } finally {
    // ✅ Reset input so selecting the same file again triggers change
    fileInput.value = '';
  }
}
  },
  updated () {
    this.$nextTick(() => {
      const box = this.$refs.chatBox
      box.scrollTop = box.scrollHeight
    })
  }
}
</script>

<style scoped>
.chat-container {
  width: 400px;
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  font-family: 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
  position: fixed;
  bottom: 20px;
  right: 20px;
}

.chat-header {
  background: #2d2d2d;
  color: #fff;
  padding: 12px 16px;
  font-weight: bold;
  font-size: 16px;
}

.chat-messages {
  flex-grow: 1;
  min-height: 50px;
  max-height: 400px;
  overflow-y: auto;
  padding: 12px;
  background: #282828;
  color: #e5e5e5;
  transition: max-height 0.2s ease-in-out;
}

.user {
  text-align: right;
}

.bot {
  text-align: left;
}

.bubble {
  display: inline-block;
  padding: 8px 12px;
  margin: 6px 0;
  border-radius: 12px;
  background: #3a3a3a;
  color: #fff;
  max-width: 80%;
  word-wrap: break-word;
}

.chat-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #1e1e1e;
}

.input-box {
  flex: 1;
  padding: 6px 10px;
  border-radius: 8px;
  border: none;
  outline: none;
  font-size: 14px;
}

.send-btn {
  background: #ff6f3c;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-weight: bold;
}

.send-btn:hover {
  background: #ff874d;
}

.upload-icon {
  font-size: 20px;
  cursor: pointer;
  color: #aaa;
}
</style>
