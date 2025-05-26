<template>
  <div style="border: 1px solid #ccc; padding: 10px; width: 400px; background: white;">
    <h5>UAV Assistant</h5>

    <div style="max-height: 300px; overflow-y: auto; margin-bottom: 10px;">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :style="{ textAlign: msg.sender === 'user' ? 'right' : 'left' }"
      >
        <strong>{{ msg.sender === 'user' ? 'You' : 'Bot' }}:</strong> {{ msg.text }}
      </div>
    </div>

    <div style="display: flex; gap: 5px; align-items: center;">
      <label style="cursor: pointer;">
        📎
        <input
          type="file"
          accept=".bin"
          style="display: none;"
          @change="handleFileUpload"
        />
      </label>

      <input
        v-model="input"
        @keyup.enter="sendMessage"
        placeholder="Ask something..."
        style="flex: 1; padding: 4px;"
        ref="inputField"
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  data() {
    return {
      input: '',
      messages: [],
      sessionId: null
    }
  },
  methods: {
    async sendMessage() {
      if (!this.input.trim()) return

      this.messages.push({ sender: 'user', text: this.input })
      const messageToSend = this.input
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
  const file = event.target.files[0]
  if (!file) return

  this.messages.push({ sender: 'bot', text: '⏳ Loading telemetry data from file...' })

  const formData = new FormData()
  formData.append('file', file)
  if (this.sessionId) {
    formData.append('session_id', this.sessionId)
  }

  try {
    const res = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()

    if (!data.success) {
      alert(`❌ ${data.message || 'Upload failed.'}`)
      this.messages.push({ sender: 'bot', text: '❌ Failed to load telemetry data.' })
      return
    }

    this.sessionId = data.session_id
    this.messages.push({
      sender: 'bot',
      text: data.message || '✅ Telemetry data successfully loaded. You may now ask flight questions.'
    })
  } catch (err) {
    console.error('Upload error:', err)
    alert(`❌ Upload error: ${err.message}`)
    this.messages.push({ sender: 'bot', text: '❌ Upload or parsing failed.' })
  }
}

  }
}
</script>
