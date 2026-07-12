import { create } from 'zustand';
import { api } from '../utils/api';

export const useChatStore = create((set, get) => ({
  user: null,
  conversations: [],
  activeConversation: null,
  messages: [],
  games: [],
  loading: false,
  error: null,

  // Setters
  setError: (error) => set({ error }),
  setLoading: (loading) => set({ loading }),

  // Actions
  register: async (username, password) => {
    set({ loading: true, error: null });
    try {
      const data = await api.register(username, password);
      set({ loading: false });
      return data;
    } catch (err) {
      set({ error: err.message, loading: false });
      throw err;
    }
  },

  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      const user = await api.login(username, password);
      set({ user, loading: false });
      // Fetch initial data
      get().fetchConversations();
      get().fetchGames();
    } catch (err) {
      set({ error: err.message, loading: false });
      throw err;
    }
  },

  logout: () => {
    set({
      user: null,
      conversations: [],
      activeConversation: null,
      messages: [],
      error: null
    });
    // In session-based auth, we can also clear backend session if needed,
    // or just clear the frontend state.
  },

  fetchConversations: async () => {
    try {
      const conversations = await api.getConversations();
      set({ conversations });
    } catch (err) {
      set({ error: err.message });
    }
  },

  selectConversation: async (conv) => {
    set({ activeConversation: conv, messages: [], error: null });
    if (conv) {
      await get().fetchMessages(conv.id);
    }
  },

  startConversation: async (recipientId) => {
    set({ loading: true, error: null });
    try {
      const conv = await api.createConversation(recipientId);
      await get().fetchConversations();
      set({ activeConversation: conv, loading: false });
      await get().fetchMessages(conv.id);
      return conv;
    } catch (err) {
      set({ error: err.message, loading: false });
      throw err;
    }
  },

  fetchMessages: async (convId) => {
    try {
      const messages = await api.getMessages(convId);
      set({ messages });
    } catch (err) {
      set({ error: err.message });
    }
  },

  sendMessage: async (convId, type, content) => {
    const tempId = `temp-${Date.now()}`;
    const tempMsg = {
      id: tempId,
      conv_id: convId,
      sender_id: get().user.id,
      message_type: type,
      content: content,
      created_at: new Date().toISOString(),
      status: 'sending'
    };

    set((state) => ({
      messages: [...state.messages, tempMsg]
    }));

    try {
      const newMsg = await api.sendMessage(convId, type, content, tempId);
      set((state) => ({
        messages: state.messages.map((m) => m.id === tempId ? { ...newMsg, status: 'sent' } : m)
      }));
      get().fetchConversations();
    } catch (err) {
      set((state) => ({
        messages: state.messages.map((m) => m.id === tempId ? { ...m, status: 'failed' } : m)
      }));
      throw err;
    }
  },

  retryMessage: async (tempId, convId, type, content) => {
    set((state) => ({
      messages: state.messages.map((m) => m.id === tempId ? { ...m, status: 'sending' } : m)
    }));

    try {
      const newMsg = await api.sendMessage(convId, type, content, tempId);
      set((state) => ({
        messages: state.messages.map((m) => m.id === tempId ? { ...newMsg, status: 'sent' } : m)
      }));
      get().fetchConversations();
    } catch (err) {
      set((state) => ({
        messages: state.messages.map((m) => m.id === tempId ? { ...m, status: 'failed' } : m)
      }));
      throw err;
    }
  },

  fetchGames: async () => {
    try {
      const games = await api.getGames();
      set({ games });
    } catch (err) {
      set({ error: err.message });
    }
  }
}));
