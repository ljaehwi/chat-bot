<template>
  <div class="chat-input">
    <div class="input-wrapper">
      <Textarea
        v-model="newMessage"
        class="modern-input"
        placeholder="질문을 작성해주세요.."
        @keyup.enter="handleSendMessage"
        :disabled="isLoading"
        :autoResize="true"
        rows="1"
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
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAgentStore } from '../stores/agent';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';

const store = useAgentStore();
const newMessage = ref('');

const isLoading = computed(() => store.status !== 'finished' && store.status !== 'waiting' && store.status !== 'error');

const handleSendMessage = () => {
  if (newMessage.value.trim() !== '') {
    store.sendMessage(1, newMessage.value);
    newMessage.value = '';
  }
};
</script>

<style scoped>
.chat-input {
  padding: 1.5rem;
  background: linear-gradient(to top, #121212 80%, transparent);
  border-top: 1px solid #1f1f1f;
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
  box-shadow: none !important;
  resize: none; /* Disable manual resize handle */
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
</style>

