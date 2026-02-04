<template>
  <div class="system-health">
    <div 
      v-for="(service, name) in health" 
      :key="name" 
      :class="['service-status', getStatusClass(service.status)]"
      v-tooltip.top="service.message || 'No details available'"
    >
      <div class="info-group">
        <span class="service-name">{{ name.replace('_', ' ') }}</span>
        <span class="status-indicator">
          <span :class="['status-light', getStatusClass(service.status)]"></span>
          <span class="status-ping"></span>
        </span>
      </div>
      
      <div class="status-text-wrapper">
        <span class="status-text">{{ service.status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAgentStore } from '../stores/agent';
import Tooltip from 'primevue/tooltip'; // Tooltip directive 사용을 위해 import 유지

const store = useAgentStore();
const health = ref({});

onMounted(async () => {
    health.value = await store.fetchSystemHealth();
    console.log("System Health Loaded:", health.value);
});

const getStatusClass = (status) => {
  return status === 'ok' ? 'ok' : 'error';
};
</script>

<style scoped>
/* 전체 그리드 레이아웃 */
.system-health {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
}

/* 카드 스타일 (Glassmorphism & Border) */
.service-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 30, 30, 0.6); /* 반투명 배경 */
  backdrop-filter: blur(10px);
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: help;
}

/* Hover 효과 */
.service-status:hover {
  background: rgba(40, 40, 40, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

/* 상태별 테두리 포인트 컬러 */
.service-status.ok {
  border-left: 3px solid #00f2fe; /* Cyan */
}
.service-status.error {
  border-left: 3px solid #ff0055; /* Neon Red */
}

/* 서비스 이름 텍스트 */
.service-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #a0a0a0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-right: 8px;
}

/* 상태 텍스트 (우측) */
.status-text {
  font-family: 'JetBrains Mono', monospace; /* 고정폭 폰트 추천 */
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
}

.service-status.ok .status-text {
  color: #00f2fe;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
}

.service-status.error .status-text {
  color: #ff0055;
  text-shadow: 0 0 10px rgba(255, 0, 85, 0.3);
}

/* --- 상태 표시등 (Pulse Animation) --- */
.info-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 12px;
  height: 12px;
}

/* 실제 점 */
.status-light {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  z-index: 2;
}

.status-light.ok {
  background-color: #00f2fe;
  box-shadow: 0 0 8px #00f2fe;
}

.status-light.error {
  background-color: #ff0055;
  box-shadow: 0 0 8px #ff0055;
}

/* 퍼지는 애니메이션 (Ping) */
.status-ping {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  opacity: 0.6;
  z-index: 1;
}

.service-status.ok .status-ping {
  background-color: #00f2fe;
  animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.service-status.error .status-ping {
  background-color: #ff0055;
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}
</style>