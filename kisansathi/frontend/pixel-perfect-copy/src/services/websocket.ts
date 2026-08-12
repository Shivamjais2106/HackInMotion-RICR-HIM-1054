import io, { Socket } from 'socket.io-client';

let socket: Socket | null = null;

const getSocketURL = (): string => {
  return import.meta.env.VITE_API_URL 
    ? import.meta.env.VITE_API_URL
    : 'http://localhost:5000';
};

export const initializeSocket = (userId: string): Socket => {
  if (socket && socket.connected) {
    return socket;
  }

  socket = io(getSocketURL(), {
    query: {
      user_id: userId
    },
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5
  });

  socket.on('connect', () => {
    console.log('✅ Connected to WebSocket');
  });

  socket.on('disconnect', () => {
    console.log('❌ Disconnected from WebSocket');
  });

  socket.on('connect_error', (error) => {
    console.error('❌ Connection error:', error);
  });

  return socket;
};

export const getSocket = (): Socket | null => {
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

// Chat events
export const joinGroup = (groupId: string, userId: string) => {
  if (socket) {
    socket.emit('join_group', { group_id: groupId, user_id: userId });
  }
};

export const leaveGroup = (groupId: string, userId: string) => {
  if (socket) {
    socket.emit('leave_group', { group_id: groupId, user_id: userId });
  }
};

export const sendMessage = (groupId: string, userId: string, message: string, userName: string) => {
  if (socket) {
    socket.emit('send_message', {
      group_id: groupId,
      user_id: userId,
      message,
      user_name: userName
    });
  }
};

export const emitTyping = (groupId: string, userId: string, userName: string) => {
  if (socket) {
    socket.emit('typing', {
      group_id: groupId,
      user_id: userId,
      user_name: userName
    });
  }
};

export const emitStopTyping = (groupId: string, userId: string) => {
  if (socket) {
    socket.emit('stop_typing', {
      group_id: groupId,
      user_id: userId
    });
  }
};

// Notification events
export const subscribeNotifications = (userId: string) => {
  if (socket) {
    socket.emit('subscribe_notifications', { user_id: userId });
  }
};

export const unsubscribeNotifications = (userId: string) => {
  if (socket) {
    socket.emit('unsubscribe_notifications', { user_id: userId });
  }
};

// Monitoring events
export const subscribeMonitoring = (userId: string) => {
  if (socket) {
    socket.emit('subscribe_monitoring', { user_id: userId });
  }
};

export const unsubscribeMonitoring = (userId: string) => {
  if (socket) {
    socket.emit('unsubscribe_monitoring', { user_id: userId });
  }
};

// Event listeners
export const onNewMessage = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('new_message', callback);
  }
};

export const onUserTyping = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('user_typing', callback);
  }
};

export const onUserStoppedTyping = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('user_stopped_typing', callback);
  }
};

export const onUserOnline = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('user_online', callback);
  }
};

export const onUserOffline = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('user_offline', callback);
  }
};

export const onNotification = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('notification', callback);
  }
};

export const onMonitoringUpdate = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('monitoring_update', callback);
  }
};

export const onUserJoinedGroup = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('user_joined_group', callback);
  }
};

export const onUserLeftGroup = (callback: (data: any) => void) => {
  if (socket) {
    socket.on('user_left_group', callback);
  }
};

export default socket;
