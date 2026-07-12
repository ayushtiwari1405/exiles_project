import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from './store/useChatStore';
import { api } from './utils/api';
import { 
  MessageSquare, 
  Send, 
  Gamepad2, 
  Search, 
  LogOut, 
  UserPlus, 
  X, 
  Play, 
  User, 
  ArrowRight,
  Sparkles,
  Gamepad
} from 'lucide-react';

export default function App() {
  const {
    user,
    conversations,
    activeConversation,
    messages,
    games,
    loading,
    error,
    login,
    register,
    logout,
    fetchConversations,
    selectConversation,
    startConversation,
    sendMessage,
    retryMessage,
    fetchGames,
    setError
  } = useChatStore();

  // Auth local state
  const [isRegister, setIsRegister] = useState(false);
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  
  // Search users state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Message input state
  const [messageText, setMessageText] = useState('');

  // Active game iframe state
  const [activeGameUrl, setActiveGameUrl] = useState(null);
  const [activeGameTitle, setActiveGameTitle] = useState('');
  const [showGamesCatalog, setShowGamesCatalog] = useState(false);

  const messagesEndRef = useRef(null);

  // Poll for messages in the active conversation and update conversation list
  useEffect(() => {
    let interval;
    if (user && activeConversation) {
      interval = setInterval(() => {
        // Fetch new messages (cursor-based pagination is supported on backend,
        // but simple full fetch keeps states simple; we fetch latest messages).
        const lastMsgId = messages.length > 0 ? messages[messages.length - 1].id : null;
        
        // Fetch fresh message list
        useChatStore.getState().fetchMessages(activeConversation.id);
        // Refresh conversations list
        fetchConversations();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [user, activeConversation, messages.length]);

  // Scroll to bottom when messages load
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle User search
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchQuery.trim().length > 0) {
        setIsSearching(true);
        try {
          const res = await api.searchUsers(searchQuery);
          setSearchResults(res);
        } catch (err) {
          console.error(err);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    if (!usernameInput.trim() || !passwordInput.trim()) {
      setError('Please fill in all fields.');
      return;
    }
    try {
      if (isRegister) {
        await register(usernameInput, passwordInput);
        // Automatically login after successful registration
        await login(usernameInput, passwordInput);
      } else {
        await login(usernameInput, passwordInput);
      }
      setUsernameInput('');
      setPasswordInput('');
    } catch (err) {
      // Error is set in store
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim() || !activeConversation) return;
    try {
      await sendMessage(activeConversation.id, 'text', messageText);
      setMessageText('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendGameInvite = async (game) => {
    if (!activeConversation) return;
    try {
      // Send message with type 'games' and game details as JSON/URL
      const inviteContent = JSON.stringify({
        title: game.title,
        url: game.url,
        desc: game.desc
      });
      await sendMessage(activeConversation.id, 'games', inviteContent);
      setShowGamesCatalog(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenGameInvite = (contentStr) => {
    try {
      const gameInfo = JSON.parse(contentStr);
      setActiveGameUrl(gameInfo.url);
      setActiveGameTitle(gameInfo.title);
    } catch (e) {
      // Fallback if not JSON
      setActiveGameUrl(contentStr);
      setActiveGameTitle('Game');
    }
  };

  const handleSelectSearchResult = async (selectedUser) => {
    try {
      await startConversation(selectedUser.id);
      setSearchQuery('');
      setSearchResults([]);
    } catch (err) {
      console.error(err);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center px-4 relative overflow-hidden font-sans">
        {/* Decorative background gradients */}
        <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-violet-600/10 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none" />

        <div className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl relative z-10">
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-tr from-violet-500 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg shadow-violet-500/25 mb-4">
              <Gamepad2 className="w-8 h-8 text-white animate-pulse" />
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight text-center">
              AetherArcade
            </h1>
            <p className="text-slate-400 text-sm mt-1 text-center">
              Real-time messaging with interactive instant-play mini-games
            </p>
          </div>

          <form onSubmit={handleAuthSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Username
              </label>
              <input
                type="text"
                placeholder="Enter your username"
                value={usernameInput}
                onChange={(e) => setUsernameInput(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-violet-500 focus:ring-1 focus:ring-violet-500 rounded-xl px-4 py-3 text-white placeholder-slate-500 transition outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Password
              </label>
              <input
                type="password"
                placeholder="Enter your password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-violet-500 focus:ring-1 focus:ring-violet-500 rounded-xl px-4 py-3 text-white placeholder-slate-500 transition outline-none"
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-xs text-red-400 font-medium">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold rounded-xl py-3 shadow-lg shadow-violet-600/25 transition active:scale-[0.98] disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2"
            >
              {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError(null);
              }}
              className="text-xs text-violet-400 hover:text-violet-300 transition underline decoration-violet-500/50 underline-offset-4 cursor-pointer"
            >
              {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-slate-950 text-white flex overflow-hidden font-sans">
      {/* SIDEBAR: User search and active chats list */}
      <div className="w-80 border-r border-slate-900 flex flex-col bg-slate-950 z-20 shrink-0">
        {/* User Header */}
        <div className="p-4 border-b border-slate-900 flex items-center justify-between bg-slate-900/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
              <User className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-100">{user.username}</div>
              <div className="text-xxs text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
                Active Session
              </div>
            </div>
          </div>
          <button 
            onClick={logout}
            title="Log Out"
            className="p-2 hover:bg-red-500/10 hover:text-red-400 rounded-lg text-slate-400 transition cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>

        {/* User Search */}
        <div className="p-4 relative">
          <div className="relative">
            <input
              type="text"
              placeholder="Search users..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900/60 border border-slate-800 focus:border-violet-500 rounded-xl pl-10 pr-4 py-2 text-sm outline-none transition"
            />
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            {searchQuery && (
              <button 
                onClick={() => { setSearchQuery(''); setSearchResults([]); }}
                className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Search Dropdown Results */}
          {searchQuery && (
            <div className="absolute top-full left-4 right-4 bg-slate-900 border border-slate-800 rounded-xl shadow-xl mt-1 z-30 max-h-60 overflow-y-auto divide-y divide-slate-800">
              {isSearching ? (
                <div className="p-4 text-center text-xs text-slate-500">Searching...</div>
              ) : searchResults.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500">No users found</div>
              ) : (
                searchResults.map((u) => (
                  <button
                    key={u.id}
                    onClick={() => handleSelectSearchResult(u)}
                    className="w-full text-left px-4 py-3 hover:bg-violet-600/10 flex items-center justify-between text-sm transition cursor-pointer"
                  >
                    <span className="font-medium text-slate-200">{u.username}</span>
                    <span className="text-xxs text-violet-400 font-semibold uppercase tracking-wider bg-violet-600/10 px-2 py-0.5 rounded border border-violet-500/10 flex items-center gap-1">
                      <UserPlus className="w-3 h-3" />
                      Chat
                    </span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        {/* Chats History List */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          <div className="px-3 py-2 text-xxs font-bold text-slate-500 uppercase tracking-widest">
            Recent Conversations
          </div>
          {conversations.length === 0 ? (
            <div className="text-center text-slate-500 text-xs py-8 px-4">
              No active chats. Search above to start a conversation!
            </div>
          ) : (
            conversations.map((c) => {
              const isActive = activeConversation?.id === c.id;
              return (
                <button
                  key={c.id}
                  onClick={() => selectConversation(c)}
                  className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition cursor-pointer ${
                    isActive 
                      ? 'bg-gradient-to-r from-violet-600/20 to-indigo-600/20 border border-violet-500/20' 
                      : 'hover:bg-slate-900 border border-transparent'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    isActive 
                      ? 'bg-violet-600 text-white' 
                      : 'bg-slate-800 text-slate-300'
                  }`}>
                    {c.other_user.username[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline mb-0.5">
                      <div className={`text-sm font-semibold truncate ${
                        isActive ? 'text-violet-300' : 'text-slate-200'
                      }`}>
                        {c.other_user.username}
                      </div>
                      <span className="text-xxs text-slate-500 shrink-0">
                        {new Date(c.last_update).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 truncate">
                      Click to chat and play
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* CHAT AREA & GAME CONTAINER */}
      <div className="flex-1 flex bg-slate-950 relative overflow-hidden">
        {/* Chat Thread Panel */}
        <div className="flex-1 flex flex-col h-full bg-slate-950 border-r border-slate-900">
          {activeConversation ? (
            <>
              {/* Chat Header */}
              <div className="h-16 border-b border-slate-900 px-6 flex items-center justify-between bg-slate-900/10">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center text-indigo-400 font-bold text-sm border border-indigo-500/15">
                    {activeConversation.other_user.username[0].toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-slate-100">{activeConversation.other_user.username}</h2>
                    <p className="text-xxs text-slate-400">1:1 Conversation</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowGamesCatalog(true)}
                    className="bg-violet-600 hover:bg-violet-500 text-white text-xs font-semibold px-4 py-2 rounded-xl shadow-lg shadow-violet-600/15 transition active:scale-95 flex items-center gap-2 cursor-pointer"
                  >
                    <Gamepad2 className="w-4 h-4" />
                    Launch Game
                  </button>
                </div>
              </div>

              {/* Chat Thread Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col justify-center items-center text-slate-500 space-y-2">
                    <MessageSquare className="w-12 h-12 text-slate-700 stroke-[1.5]" />
                    <p className="text-sm">No messages yet. Send a message to start!</p>
                  </div>
                ) : (
                  messages.map((m) => {
                    const isSelf = m.sender_id === user.id;
                    const isGameType = m.message_type === 'games';
                    let gameInfo = null;

                    if (isGameType) {
                      try {
                        gameInfo = JSON.parse(m.content);
                      } catch (_) {
                        gameInfo = { title: 'Game Invite', url: m.content, desc: 'Shared mini-game' };
                      }
                    }

                      return (
                        <div 
                          key={m.id} 
                          className={`flex ${isSelf ? 'justify-end' : 'justify-start'}`}
                          role="log"
                          aria-label={`Message from ${isSelf ? 'you' : activeConversation.other_user.username} at ${new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
                        >
                          <div className={`max-w-[70%] rounded-2xl px-4 py-3 shadow-md ${
                            isGameType 
                              ? 'bg-gradient-to-br from-violet-900/60 to-indigo-900/60 border border-violet-500/30' 
                              : isSelf 
                                ? 'bg-violet-600 text-white rounded-br-none' 
                                : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-none'
                          }`}>
                          
                          {isGameType ? (
                            <div className="flex flex-col gap-2 font-sans">
                              <div className="flex items-center gap-2 pb-2 border-b border-violet-500/20">
                                <span className="bg-violet-500 text-white p-1.5 rounded-lg">
                                  <Gamepad className="w-4 h-4" />
                                </span>
                                <div>
                                  <div className="text-sm font-bold text-white tracking-wide">
                                    {gameInfo.title}
                                  </div>
                                  <div className="text-xxs text-violet-300">Game Invite</div>
                                </div>
                              </div>
                              <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                                {gameInfo.desc || 'Join me for a quick game!'}
                              </p>
                              <button
                                onClick={() => handleOpenGameInvite(m.content)}
                                className="w-full bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold py-2 rounded-xl shadow mt-2 transition flex items-center justify-center gap-1.5 cursor-pointer"
                              >
                                <Play className="w-3.5 h-3.5 fill-white" />
                                Launch & Play
                              </button>
                            </div>
                          ) : (
                            <p className="text-sm break-words whitespace-pre-wrap leading-relaxed">
                              {m.content}
                            </p>
                          )}
                          <div className={`text-xxs text-slate-400 mt-1.5 flex items-center justify-end gap-1.5 select-none ${
                            isSelf && !isGameType ? 'text-violet-200' : 'text-slate-400'
                          }`}>
                            <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            {m.status === 'sending' && (
                              <span className="text-xxs text-violet-300 italic animate-pulse">(Sending...)</span>
                            )}
                            {m.status === 'failed' && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  retryMessage(m.id, activeConversation.id, m.message_type, m.content);
                                }}
                                className="text-xxs text-red-400 underline cursor-pointer hover:text-red-300 transition flex items-center gap-1 font-semibold"
                              >
                                (Failed. Click to retry)
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input Area */}
              <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-900 bg-slate-900/10 flex gap-2">
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  className="flex-1 bg-slate-900/60 border border-slate-800 focus:border-violet-500 rounded-xl px-4 py-3 text-sm outline-none transition text-white placeholder-slate-500"
                />
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white p-3.5 rounded-xl shadow-lg shadow-indigo-600/15 transition active:scale-95 flex items-center justify-center cursor-pointer"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </>
          ) : (
            /* Welcome Dashboard when no conversation selected */
            <div className="flex-1 flex flex-col justify-center items-center p-8 relative overflow-hidden bg-slate-950 font-sans">
              <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] rounded-full bg-violet-600/5 blur-[100px] pointer-events-none" />
              <div className="absolute bottom-[20%] left-[10%] w-[30%] h-[30%] rounded-full bg-indigo-600/5 blur-[100px] pointer-events-none" />

              <div className="max-w-md text-center flex flex-col items-center relative z-10">
                <div className="w-20 h-20 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-violet-600/20 mb-6">
                  <Gamepad2 className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-extrabold text-white tracking-tight mb-3">
                  Welcome to AetherArcade!
                </h1>
                <p className="text-slate-400 text-sm leading-relaxed mb-6">
                  Select a contact on the left sidebar to start messaging. You can share interactive games like Chess, Tic-Tac-Toe, and Connect Four directly inside chat threads!
                </p>
                <div className="bg-slate-900/60 backdrop-blur border border-slate-800 rounded-2xl p-4 w-full text-left flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-violet-400 shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-1">Instant Game Invites</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      Just click the "Launch Game" button inside a conversation thread to send an invite. You and your friend can play concurrently in a side-by-side split pane.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* SIDE-BY-SIDE ACTIVE GAME IFRAME PANEL */}
        {activeGameUrl && (
          <div className="w-[500px] md:w-[600px] xl:w-[700px] border-l border-slate-900 bg-slate-900/30 flex flex-col h-full z-10 shrink-0 relative transition-all duration-300">
            <div className="h-16 border-b border-slate-900 px-6 flex items-center justify-between bg-slate-900/80 backdrop-blur">
              <div className="flex items-center gap-3">
                <span className="bg-emerald-500/20 text-emerald-400 p-1.5 rounded-lg border border-emerald-500/10">
                  <Gamepad className="w-4 h-4" />
                </span>
                <div>
                  <h2 className="text-sm font-bold text-slate-100">{activeGameTitle}</h2>
                  <p className="text-xxs text-emerald-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
                    Interactive Session Active
                  </p>
                </div>
              </div>
              <button 
                onClick={() => { setActiveGameUrl(null); setActiveGameTitle(''); }}
                className="p-2 hover:bg-red-500/10 hover:text-red-400 rounded-lg text-slate-400 transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            {/* Embedded Game Iframe container */}
            <div className="flex-1 bg-slate-950 p-2 relative">
              <iframe
                src={activeGameUrl}
                title={activeGameTitle}
                className="w-full h-full border-0 rounded-xl bg-slate-900"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          </div>
        )}

        {/* GAMES CATALOG MODAL */}
        {showGamesCatalog && (
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex justify-center items-center z-50 p-4">
            <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative">
              <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/40">
                <div className="flex items-center gap-2.5">
                  <span className="bg-violet-600/10 text-violet-400 p-1.5 rounded-xl border border-violet-500/10">
                    <Gamepad className="w-5 h-5" />
                  </span>
                  <div>
                    <h3 className="text-base font-bold text-white">Games Catalog</h3>
                    <p className="text-xxs text-slate-400">Select a game to invite {activeConversation?.other_user.username}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowGamesCatalog(false)}
                  className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-100 transition cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="p-6 max-h-[400px] overflow-y-auto space-y-4">
                {games.map((g) => (
                  <div 
                    key={g.id} 
                    className="p-4 bg-slate-950 border border-slate-800 hover:border-violet-500/40 rounded-2xl flex justify-between items-start gap-4 transition group"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-slate-100 group-hover:text-violet-400 transition">{g.title}</h4>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">{g.desc}</p>
                      <div className="text-xxs text-slate-500 mt-2 truncate bg-slate-900/50 px-2 py-0.5 rounded border border-slate-800 inline-block">
                        {g.url}
                      </div>
                    </div>
                    <button
                      onClick={() => handleSendGameInvite(g)}
                      className="bg-violet-600 hover:bg-violet-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition cursor-pointer shrink-0"
                    >
                      Invite
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
