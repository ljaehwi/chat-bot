<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer">
      <div v-for="msg in messages" :key="msg.id" :class="['message-row', msg.role]">
        <div v-if="msg.role === 'assistant'" class="avatar assistant-avatar">
          <i class="pi pi-sparkles"></i>
        </div>
        
        <div class="message-bubble">
           <div class="content" v-html="renderMarkdown(msg.content)"></div>
        </div>

        <div v-if="msg.role === 'user'" class="avatar user-avatar">
          <i class="pi pi-user"></i>
        </div>
      </div>
    </div>

    <div class="input-container">
      <div class="input-wrapper">
        <InputText 
          type="text" 
          v-model="newMessage" 
          class="modern-input"
          placeholder="부장님, 지시사항을 입력해주세요..." 
          @keyup.enter="handleSendMessage" 
          :disabled="isLoading" 
        />
        <Button 
          icon="pi pi-arrow-up" 
          class="send-btn" 
          rounded 
          text
          @click="handleSendMessage" 
          :disabled="isLoading || !newMessage.trim()" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue';
import { useAgentStore } from '../stores/agent';
import { marked } from 'marked';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

const store = useAgentStore();
const newMessage = ref('');
const messagesContainer = ref(null);

const messages = computed(() => store.messages);
const isLoading = computed(() => store.status !== 'finished' && store.status !== 'waiting' && store.status !== 'error');

const handleSendMessage = () => {
  if (newMessage.value.trim() !== '') {
    store.sendMessage(1, newMessage.value); // Send user_id as an integer
    newMessage.value = '';
  }
};

const renderMarkdown = (content) => {
  return marked(content);
};

watch(messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}, { deep: true });
</script>

<style scoped>
/* 전체 레이아웃 & 배경 */
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #121212; /* Deep Dark Background */
  font-family: 'Pretendard', sans-serif; /* Modern Font recommendation */
  color: #e0e0e0;
}

/* 메시지 영역 */
.messages {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 스크롤바 커스텀 */
.messages::-webkit-scrollbar {
  width: 6px;
}
.messages::-webkit-scrollbar-thumb {
  background-color: #333;
  border-radius: 3px;
}

/* 메시지 행 (배치) */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  max-width: 80%;
  animation: fadeIn 0.3s ease-out;
}

.message-row.user {
  align-self: flex-end; /* 오른쪽 정렬 */
  flex-direction: row; /* 아바타 우측 배치 */
}

.message-row.assistant {
  align-self: flex-start; /* 왼쪽 정렬 */
}

/* 아바타 스타일 */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px; /* Soft square */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  flex-shrink: 0;
}

.assistant-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #000;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

/* 말풍선 스타일 */
.message-bubble {
  padding: 12px 18px;
  border-radius: 18px;
  line-height: 1.6;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  position: relative;
}

/* User Bubble: 강조색 */
.message-row.user .message-bubble {
  background-color: #2b5cff;
  color: #ffffff;
  border-bottom-right-radius: 4px; /* 말꼬리 효과 */
}

/* Assistant Bubble: 다크 그레이 */
.message-row.assistant .message-bubble {
  background-color: #2a2a2a;
  color: #e0e0e0;
  border-bottom-left-radius: 4px; /* 말꼬리 효과 */
  border: 1px solid #3a3a3a;
}

/* Markdown Content 내부 스타일링 */
.content :deep(p) {
  margin: 0;
}
.content :deep(code) {
  background: rgba(0,0,0,0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

/* 입력 영역 (Floating Style) */
.input-container {
  padding: 1.5rem;
  background: linear-gradient(to top, #121212 80%, transparent); /* Fade out top */
}

.input-wrapper {
  display: flex;
  align-items: center;
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 30px;
  padding: 6px 6px 6px 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  transition: border-color 0.3s;
}

.input-wrapper:focus-within {
  border-color: #4facfe;
}

.modern-input {
  flex-grow: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1rem;
  padding: 8px 0;
  outline: none;
  box-shadow: none !important; /* PrimeVue default override */
}

.modern-input::placeholder {
  color: #666;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #2b5cff !important;
  color: white !important;
  margin-left: 8px;
  transition: transform 0.2s, background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.send-btn:hover:not(:disabled) {
  background-color: #1a45d6 !important;
  transform: scale(1.05);
}

.send-btn:disabled {
  background-color: #333 !important;
  color: #666 !important;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>