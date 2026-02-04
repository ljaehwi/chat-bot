// services/socket.js

let socket = null;

const connectWebSocket = (onMessageCallback) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    console.log("WebSocket is already connected.");
    return;
  }

  const wsUrl = `ws://localhost:8000/ws/chat`;
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("WebSocket connection established.");
    onMessageCallback({ type: 'connection_status', status: 'connected' });
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessageCallback(data);
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected.");
    onMessageCallback({ type: 'connection_status', status: 'disconnected' });
    socket = null;
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    onMessageCallback({ type: 'error', content: 'WebSocket connection failed.' });
    onMessageCallback({ type: 'connection_status', status: 'disconnected' });
    socket = null;
  };
};

const sendMessage = (payload) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not connected. Cannot send message.");
        return;
    }
    socket.send(JSON.stringify(payload));
}

const disconnectWebSocket = () => {
  if (socket) {
    socket.close();
  }
};

// It's better to export functions that interact with the service
// rather than the socket instance itself.
export { connectWebSocket, sendMessage, disconnectWebSocket };