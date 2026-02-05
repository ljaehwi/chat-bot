<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer" @scroll="handleScroll">
      <div v-for="msg in messages" :key="msg.id" :class="['message-row', msg.role]">
        <div v-if="msg.role === 'assistant'" class="avatar assistant-avatar">
          <i class="pi pi-sparkles"></i>
        </div>
        
        <div class="message-bubble">
          <div class="content" v-html="renderMarkdown(msg.content)"></div>
          <div v-if="msg.role === 'assistant' && msg.tool_results && msg.tool_results.length" class="tool-results">
            <div class="tool-results-title">사용한 도구</div>
            <div v-for="(tool, idx) in msg.tool_results" :key="`${msg.id}-${idx}`" class="tool-result">
              <div class="tool-result-header">
                <div class="tool-name">{{ tool.tool_name || 'unknown_tool' }}</div>
                <button
                  class="tool-toggle"
                  type="button"
                  @click="toggleTool(`${msg.id}-${idx}`)"
                >
                  {{ isToolOpen(`${msg.id}-${idx}`) ? '접기' : '자세히보기' }}
                </button>
              </div>
              <pre v-if="isToolOpen(`${msg.id}-${idx}`)" class="tool-output" v-text="tool.output"></pre>
            </div>
          </div>
        </div>

        <div v-if="msg.role === 'user'" class="avatar user-avatar">
          <i class="pi pi-user"></i>
        </div>
      </div>
    </div>

    <button
      v-if="showJumpToBottom"
      class="jump-to-bottom"
      type="button"
      @click="jumpToBottom"
    >
      새 메시지 {{ unreadCount }}개
    </button>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue';
import { useAgentStore } from '../stores/agent';
import { marked } from 'marked';

const store = useAgentStore();
const messagesContainer = ref(null);
const isUserScrolledUp = ref(false);
const SCROLL_THRESHOLD = 32;
const unreadCount = ref(0);
const expandedTools = ref({});

const messages = computed(() => store.messages);
const showJumpToBottom = computed(() => isUserScrolledUp.value && unreadCount.value > 0);

const renderMarkdown = (content) => {
  return marked(content);
};

watch(messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      if (!isUserScrolledUp.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        unreadCount.value = 0;
      } else {
        unreadCount.value += 1;
      }
    }
  });
}, { deep: true });

const handleScroll = () => {
  const container = messagesContainer.value;
  if (!container) return;
  const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
  isUserScrolledUp.value = distanceFromBottom > SCROLL_THRESHOLD;
  if (!isUserScrolledUp.value) {
    unreadCount.value = 0;
  }
};

const jumpToBottom = () => {
  const container = messagesContainer.value;
  if (!container) return;
  container.scrollTop = container.scrollHeight;
  unreadCount.value = 0;
  isUserScrolledUp.value = false;
};

const toggleTool = (key) => {
  expandedTools.value[key] = !expandedTools.value[key];
};

const isToolOpen = (key) => {
  return !!expandedTools.value[key];
};
</script>

<style scoped>
/* Overall layout & background */
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #121212;
  font-family: 'Pretendard', sans-serif;
  color: #e0e0e0;
  min-height: 0;
  position: relative;
}

/* Message area */
.messages {
  flex: 1 1 auto;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 0;
}

/* Scrollbar */
.messages::-webkit-scrollbar {
  width: 6px;
}
.messages::-webkit-scrollbar-thumb {
  background-color: #333;
  border-radius: 3px;
}

/* Message rows */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  max-width: 80%;
  animation: fadeIn 0.3s ease-out;
}

.message-row.user {
  align-self: flex-end;
  flex-direction: row;
}

.message-row.assistant {
  align-self: flex-start;
}

/* Avatars */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
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

/* Bubbles */
.message-bubble {
  padding: 12px 18px;
  border-radius: 18px;
  line-height: 1.6;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  position: relative;
}

.message-row.user .message-bubble {
  background-color: #2b5cff;
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.message-row.assistant .message-bubble {
  background-color: #2a2a2a;
  color: #e0e0e0;
  border-bottom-left-radius: 4px;
  border: 1px solid #3a3a3a;
}

/* Markdown styling */
.content :deep(p) {
  margin: 0;
}
.content :deep(code) {
  background: rgba(0,0,0,0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.tool-results {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-results-title {
  font-size: 0.8rem;
  color: #9aa0a6;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tool-result {
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 8px 10px;
}

.tool-result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.tool-name {
  font-size: 0.85rem;
  color: #dfe4ea;
  font-weight: 600;
}

.tool-toggle {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: #cfd8dc;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.75rem;
  cursor: pointer;
}

.tool-toggle:hover {
  border-color: #4facfe;
  color: #ffffff;
}

.tool-output {
  margin-top: 8px;
  background: rgba(0,0,0,0.45);
  border-radius: 8px;
  padding: 10px;
  color: #e0e0e0;
  font-size: 0.8rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.jump-to-bottom {
  position: absolute;
  right: 24px;
  bottom: 24px;
  background: #2b5cff;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.85rem;
  box-shadow: 0 6px 18px rgba(0,0,0,0.35);
  cursor: pointer;
}

.jump-to-bottom:hover {
  background: #1a45d6;
}

.jump-to-bottom:active {
  transform: translateY(1px);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
