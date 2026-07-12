const BASE_URL = 'http://localhost:8000/api';

// Helper to make fetch requests with credentials (cookies)
async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  
  options.credentials = 'include';
  options.headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (options.body && typeof options.body === 'object') {
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, options);
  
  if (!response.ok) {
    let errMsg = `Request failed with status ${response.status}`;
    try {
      const errorData = await response.json();
      errMsg = errorData.error || errMsg;
    } catch (_) {}
    throw new Error(errMsg);
  }

  // Handle 201/204 empty responses safely
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  register: (username, password) => 
    request('/register', { method: 'POST', body: { username, password } }),
    
  login: (username, password) => 
    request('/login/', { method: 'POST', body: { username, password } }),
    
  searchUsers: (query) => 
    request(`/users/?search=${encodeURIComponent(query)}`),
    
  getConversations: () => 
    request('/conversations/'),
    
  createConversation: (recipientId) => 
    request('/conversations/', { method: 'POST', body: { recipient_id: recipientId } }),
    
  getMessages: (conversationId, afterId = null) => {
    const query = afterId ? `?after=${afterId}` : '';
    return request(`/conversation/${conversationId}/messages/${query}`);
  },
    
  sendMessage: (conversationId, type, content, clientTxId = null) => 
    request('/messages/', { 
      method: 'POST', 
      body: { conv_id: conversationId, message_type: type, content, client_tx_id: clientTxId } 
    }),
    
  getGames: () => 
    request('/games'),
};
