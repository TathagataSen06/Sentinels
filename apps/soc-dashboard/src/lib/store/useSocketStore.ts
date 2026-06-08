import { create } from 'zustand';

export interface FeedEvent {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  sensor?: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
}

interface SocketState {
  isConnected: boolean;
  events: FeedEvent[];
  connect: () => void;
  disconnect: () => void;
  addEvent: (event: Omit<FeedEvent, 'id' | 'timestamp'>) => void;
}

export const useSocketStore = create<SocketState>((set) => ({
  isConnected: false,
  events: [],
  connect: () => {
    set({ isConnected: true });
    // In a real implementation, this would establish the WebSocket connection
    // and bind onmessage handlers to addEvent.
  },
  disconnect: () => set({ isConnected: false }),
  addEvent: (event) => set((state) => {
    const newEvent: FeedEvent = {
      ...event,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString()
    };
    return {
      events: [newEvent, ...state.events].slice(0, 100) // Keep last 100 events
    };
  }),
}));
