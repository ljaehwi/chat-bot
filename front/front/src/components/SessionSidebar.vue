<template>
  <div class="session-sidebar">
    <div class="glass-card">
      <div class="card-header">
        <i class="pi pi-database header-icon"></i>
        <span class="header-title">SESSION</span>
      </div>

      <div class="card-content">
        <div class="section-label">Connection Status</div>
        <div class="thread-box">
          <span class="connection-status">{{ connectionText }}</span>
          <div class="status-dot" :class="{ active: isConnected }"></div>
        </div>

        <div class="divider"></div>

        <div class="section-label">History Archive</div>
        <div class="past-sessions-container">
          <div class="empty-state">
            <i class="pi pi-history"></i>
            <p>No past sessions recorded</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAgentStore } from '../stores/agent';

const store = useAgentStore();

// Bind to the new isConnected state property
const isConnected = computed(() => store.isConnected);

// Display text based on the connection status
const connectionText = computed(() => isConnected.value ? 'CONNECTED' : 'DISCONNECTED');
</script>

<style scoped>
.session-sidebar {
  padding: 1rem;
  height: 100%;
  font-family: 'Pretendard', sans-serif;
}

/* Glassmorphism Container */
.glass-card {
  background: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Header Style */
.card-header {
  padding: 1rem 1.2rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.header-icon {
  color: #4facfe;
  font-size: 1rem;
}

.header-title {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: #aaa;
  text-transform: uppercase;
}

/* Content Layout */
.card-content {
  padding: 1.5rem 1.2rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.section-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #666;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

/* Thread ID Box (Code Style) */
.thread-box {
  display: flex;
  align-items: center;
  background: #151515;
  border: 1px solid #333;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
}

.thread-box:hover {
  border-color: #4facfe;
  box-shadow: 0 0 15px rgba(79, 172, 254, 0.1);
}

.key-icon {
  color: #555;
  font-size: 0.9rem;
  margin-right: 0.8rem;
}

.thread-id {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  color: #00f2fe;
  font-size: 0.85rem;
  letter-spacing: -0.5px;
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Status Dot */
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #333;
  margin-left: 10px;
}

.status-dot.active {
  background-color: #00f2fe;
  box-shadow: 0 0 6px #00f2fe;
}

/* Divider */
.divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 0%, transparent 100%);
  margin-bottom: 1.5rem;
}

/* Empty State Styling */
.past-sessions-container {
  flex-grow: 1;
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  text-align: center;
  color: #555;
}

.empty-state i {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 0.8rem;
  margin: 0;
}
</style>