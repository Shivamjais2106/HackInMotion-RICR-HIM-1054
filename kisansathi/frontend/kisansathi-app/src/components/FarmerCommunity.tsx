import React, { useState, useEffect, useRef } from 'react';
import { Send, Image, Smile, Users, Search, Phone, Video, MoreVertical, Plus, X, Settings, Trash2, UserPlus, Crown } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { useToast } from '@/components/ui/use-toast';
import { getAPIBaseURL } from '@/utils/api';
import {
  initializeSocket,
  getSocket,
  disconnectSocket,
  joinGroup,
  leaveGroup,
  sendMessage as emitSendMessage,
  emitTyping,
  emitStopTyping,
  subscribeNotifications,
  onNewMessage,
  onUserTyping,
  onUserStoppedTyping,
  onUserOnline,
  onUserOffline,
  onNotification,
  onUserJoinedGroup,
  onUserLeftGroup
} from '@/services/websocket';

interface Message {
  id: string;
  sender: {
    id: string;
    name: string;
    avatar: string;
  };
  text: string;
  image?: string;
  timestamp: string;
  reactions?: { emoji: string; count: number }[];
}

interface TypingUser {
  user_id: string;
  user_name: string;
}

interface OnlineUser {
  user_id: string;
  status: 'online' | 'offline';
}

interface Group {
  id: string;
  name: string;
  avatar: string;
  members: number;
  lastMessage: string;
  unread: number;
  description: string;
  created_by?: string;
  admins?: string[];
  member_ids?: string[];
}

interface GroupMember {
  id: string;
  name: string;
  mobile: string;
  isAdmin: boolean;
}

const FarmerCommunity: React.FC = () => {
  const { t } = useLanguage();
  const { toast } = useToast();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageText, setMessageText] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDesc, setNewGroupDesc] = useState('');
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [groupMembers, setGroupMembers] = useState<GroupMember[]>([]);
  const [addMemberMobile, setAddMemberMobile] = useState('');
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [currentUserName, setCurrentUserName] = useState<string>('Farmer');
  const [isGroupAdmin, setIsGroupAdmin] = useState(false);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<Set<string>>(new Set());
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_BASE = getAPIBaseURL();

  // Get current user ID from localStorage
  useEffect(() => {
    const userId = localStorage.getItem('token');
    const userName = localStorage.getItem('user_name') || 'Farmer';
    if (userId) {
      setCurrentUserId(userId);
      setCurrentUserName(userName);
      // Initialize WebSocket connection
      initializeSocket(userId);
    }
    // Fetch groups on component mount
    fetchGroups();
  }, []);

  // Setup WebSocket listeners
  useEffect(() => {
    const socket = getSocket();
    if (!socket) return;

    // Listen for new messages
    onNewMessage((data) => {
      const newMessage: Message = {
        id: Date.now().toString(),
        sender: {
          id: data.user_id,
          name: data.user_name,
          avatar: '👤'
        },
        text: data.message,
        timestamp: new Date(data.timestamp).toLocaleTimeString()
      };
      setMessages(prev => [...prev, newMessage]);
    });

    // Listen for typing indicators
    onUserTyping((data) => {
      setTypingUsers(prev => {
        const exists = prev.find(u => u.user_id === data.user_id);
        if (!exists) {
          return [...prev, { user_id: data.user_id, user_name: data.user_name }];
        }
        return prev;
      });
    });

    // Listen for stop typing
    onUserStoppedTyping((data) => {
      setTypingUsers(prev => prev.filter(u => u.user_id !== data.user_id));
    });

    // Listen for online status
    onUserOnline((data) => {
      setOnlineUsers(prev => new Set([...prev, data.user_id]));
    });

    // Listen for offline status
    onUserOffline((data) => {
      setOnlineUsers(prev => {
        const newSet = new Set(prev);
        newSet.delete(data.user_id);
        return newSet;
      });
    });

    // Listen for user joined group
    onUserJoinedGroup((data) => {
      toast({
        title: 'User Joined',
        description: `A user joined the group`,
      });
    });

    // Listen for user left group
    onUserLeftGroup((data) => {
      toast({
        title: 'User Left',
        description: `A user left the group`,
      });
    });

    // Listen for notifications
    onNotification((data) => {
      toast({
        title: data.title,
        description: data.message,
      });
    });

    return () => {
      disconnectSocket();
    };
  }, [toast]);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/community/groups`);
      if (response.ok) {
        const data = await response.json();
        const groupsData = data.groups || [];
        setGroups(groupsData);
        
        // Auto-select first group if available
        if (groupsData.length > 0) {
          setSelectedGroup(groupsData[0]);
          fetchMessages(groupsData[0].id);
        }
      } else {
        console.error('Failed to fetch groups:', response.status);
        // Set empty groups array on error
        setGroups([]);
      }
    } catch (error) {
      console.error('Failed to fetch groups:', error);
      // Set empty groups array on error
      setGroups([]);
      toast({
        title: 'Connection Issue',
        description: 'Could not load community groups. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (groupId: string) => {
    try {
      const response = await fetch(`${API_BASE}/community/groups/${groupId}/messages`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const handleSelectGroup = (group: Group) => {
    setSelectedGroup(group);
    setMessages([]);
    setTypingUsers([]);
    fetchMessages(group.id);
    
    // Check if current user is admin
    if (currentUserId && group.admins) {
      setIsGroupAdmin(group.admins.includes(currentUserId));
    }
    
    // Join group via WebSocket
    if (currentUserId) {
      joinGroup(group.id, currentUserId);
    }
    
    // Auto-join group if logged in
    const token = localStorage.getItem('token');
    if (token) {
      joinGroup(group.id, token);
    }
  };

  const joinGroup = async (groupId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      await fetch(`${API_BASE}/community/groups/${groupId}/join`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      // Refresh groups to update member count
      fetchGroups();
    } catch (error) {
      console.error('Failed to join group:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSendMessage = async () => {
    if (!messageText.trim() && !selectedImage) return;
    if (!selectedGroup || !currentUserId) return;

    try {
      let token = localStorage.getItem('token');
      
      if (!token) {
        token = '1';
        console.log('Using default test user token:', token);
      }
      
      // Emit via WebSocket for real-time delivery
      emitSendMessage(selectedGroup.id, currentUserId, messageText, currentUserName);
      
      // Also send via REST API for persistence
      const messagePayload = {
        text: messageText,
        image: imagePreview,
        avatar: '👤',
      };

      const response = await fetch(`${API_BASE}/community/groups/${selectedGroup.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(messagePayload),
      });

      if (response.ok) {
        setMessageText('');
        setSelectedImage(null);
        setImagePreview(null);
        setIsTyping(false);
        
        // Emit stop typing
        emitStopTyping(selectedGroup.id, currentUserId);
        
        toast({
          title: 'Success',
          description: 'Message sent successfully',
        });
      } else {
        const errorData = await response.json();
        toast({
          title: 'Error',
          description: errorData.error || 'Failed to send message',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        variant: 'destructive',
      });
    }
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessageText(e.target.value);
    
    if (!selectedGroup || !currentUserId) return;
    
    // Emit typing indicator
    if (!isTyping) {
      setIsTyping(true);
      emitTyping(selectedGroup.id, currentUserId, currentUserName);
    }
    
    // Clear previous timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // Set new timeout to stop typing after 3 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      emitStopTyping(selectedGroup.id, currentUserId);
    }, 3000);
  };

  const handleAddEmoji = (emoji: string) => {
    setMessageText(messageText + emoji);
    setShowEmojiPicker(false);
  };

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) {
      toast({
        title: 'Error',
        description: 'Group name is required',
        variant: 'destructive',
      });
      return;
    }

    try {
      let token = localStorage.getItem('token');
      
      // If no token, use default test user token
      if (!token) {
        token = '1'; // Default test user ID
        console.log('Using default test user token for group creation:', token);
      }

      console.log('Creating group with:', { name: newGroupName, description: newGroupDesc });

      const response = await fetch(`${API_BASE}/community/groups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newGroupName,
          description: newGroupDesc,
          avatar: '🌾',
        }),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        setGroups([...groups, data.group]);
        setShowCreateGroup(false);
        setNewGroupName('');
        setNewGroupDesc('');
        toast({
          title: 'Success',
          description: 'Group created successfully',
        });
        // Refresh groups
        fetchGroups();
      } else {
        toast({
          title: 'Error',
          description: data.error || 'Failed to create group',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to create group:', error);
      toast({
        title: 'Error',
        description: 'Failed to create group: ' + (error instanceof Error ? error.message : 'Unknown error'),
        variant: 'destructive',
      });
    }
  };

  const handleDeleteMessage = async (messageId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: 'Error',
          description: 'Please login to delete messages',
          variant: 'destructive',
        });
        return;
      }

      const response = await fetch(`${API_BASE}/community/messages/${messageId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setMessages(messages.filter(m => m.id !== messageId));
        toast({
          title: 'Success',
          description: 'Message deleted successfully',
        });
      } else {
        const data = await response.json();
        toast({
          title: 'Error',
          description: data.error || 'Failed to delete message',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to delete message:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete message',
        variant: 'destructive',
      });
    }
  };

  const handleAddMember = async () => {
    if (!addMemberMobile.trim() || !selectedGroup) return;

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: 'Error',
          description: 'Please login to add members',
          variant: 'destructive',
        });
        return;
      }

      const response = await fetch(`${API_BASE}/community/groups/${selectedGroup.id}/add-member`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ mobile: addMemberMobile }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Success',
          description: data.message,
        });
        setAddMemberMobile('');
        fetchGroups();
      } else {
        const data = await response.json();
        toast({
          title: 'Error',
          description: data.error || 'Failed to add member',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to add member:', error);
      toast({
        title: 'Error',
        description: 'Failed to add member',
        variant: 'destructive',
      });
    }
  };

  const handleMakeAdmin = async (mobile: string) => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: 'Error',
          description: 'Please login',
          variant: 'destructive',
        });
        return;
      }

      const response = await fetch(`${API_BASE}/community/groups/${selectedGroup.id}/make-admin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ mobile }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Success',
          description: data.message,
        });
        fetchGroups();
      } else {
        const data = await response.json();
        toast({
          title: 'Error',
          description: data.error || 'Failed to make admin',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to make admin:', error);
      toast({
        title: 'Error',
        description: 'Failed to make admin',
        variant: 'destructive',
      });
    }
  };

  const handleRemoveMember = async (mobile: string) => {
    if (!selectedGroup) return;

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: 'Error',
          description: 'Please login',
          variant: 'destructive',
        });
        return;
      }

      const response = await fetch(`${API_BASE}/community/groups/${selectedGroup.id}/remove-member`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ mobile }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Success',
          description: data.message,
        });
        fetchGroups();
      } else {
        const data = await response.json();
        toast({
          title: 'Error',
          description: data.error || 'Failed to remove member',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to remove member:', error);
      toast({
        title: 'Error',
        description: 'Failed to remove member',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteGroup = async () => {
    if (!selectedGroup) return;

    if (!window.confirm('Are you sure you want to delete this group? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: 'Error',
          description: 'Please login',
          variant: 'destructive',
        });
        return;
      }

      const response = await fetch(`${API_BASE}/community/groups/${selectedGroup.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Group deleted successfully',
        });
        setShowAdminPanel(false);
        setSelectedGroup(null);
        fetchGroups();
      } else {
        const data = await response.json();
        toast({
          title: 'Error',
          description: data.error || 'Failed to delete group',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Failed to delete group:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete group',
        variant: 'destructive',
      });
    }
  };

  const filteredGroups = groups.filter(group =>
    group.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const emojis = ['😊', '😂', '❤️', '👍', '🙏', '😍', '🔥', '💯', '🌾', '🚜'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading community...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar - Groups List */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">👥 Farmer Community</h1>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search groups..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          {/* Create Group Button */}
          <button
            onClick={() => setShowCreateGroup(true)}
            className="w-full mt-3 flex items-center justify-center gap-2 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
          >
            <Plus className="w-5 h-5" />
            Create Group
          </button>
        </div>

        {/* Groups List */}
        <div className="flex-1 overflow-y-auto">
          {filteredGroups.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              <p>No groups yet</p>
              <p className="text-sm mt-2">Create your first group!</p>
            </div>
          ) : (
            filteredGroups.map((group) => (
              <div
                key={group.id}
                onClick={() => handleSelectGroup(group)}
                className={`p-4 border-b border-gray-100 cursor-pointer transition ${
                  selectedGroup?.id === group.id
                    ? 'bg-green-50 border-l-4 border-l-green-600'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="text-3xl">{group.avatar}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-800 truncate">{group.name}</h3>
                      {group.unread > 0 && (
                        <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                          {group.unread}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 truncate">{group.lastMessage}</p>
                    <p className="text-xs text-gray-400 mt-1">👥 {group.members} members</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      {selectedGroup && (
        <div className="flex-1 flex flex-col bg-white">
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-3xl">{selectedGroup.avatar}</div>
              <div>
                <h2 className="text-xl font-bold">{selectedGroup.name}</h2>
                <p className="text-green-100 text-sm">👥 {selectedGroup.members} members</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="p-2 hover:bg-green-500 rounded-lg transition">
                <Phone className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-green-500 rounded-lg transition">
                <Video className="w-5 h-5" />
              </button>
              {isGroupAdmin && (
                <button 
                  onClick={() => setShowAdminPanel(true)}
                  className="p-2 hover:bg-green-500 rounded-lg transition"
                  title="Group Settings"
                >
                  <Settings className="w-5 h-5" />
                </button>
              )}
              <button className="p-2 hover:bg-green-500 rounded-lg transition">
                <MoreVertical className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <p className="text-gray-500">No messages yet. Start the conversation!</p>
              </div>
            ) : (
              messages.map((message) => (
                <div key={message.id} className="flex gap-3 group">
                  <div className="text-2xl">{message.sender.avatar}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-gray-800">{message.sender.name}</span>
                      <span className="text-xs text-gray-500">{message.timestamp}</span>
                      {onlineUsers.has(message.sender.id) && (
                        <span className="w-2 h-2 bg-green-500 rounded-full" title="Online"></span>
                      )}
                      <button
                        onClick={() => handleDeleteMessage(message.id)}
                        className="ml-auto opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50 transition"
                      >
                        Delete
                      </button>
                    </div>
                    
                    {/* Message Bubble */}
                    <div className="bg-white rounded-lg p-3 shadow-sm max-w-md">
                      {message.image && (
                        <img
                          src={message.image}
                          alt="Message"
                          className="rounded-lg mb-2 max-w-full h-auto"
                        />
                      )}
                      {message.text && (
                        <p className="text-gray-800">{message.text}</p>
                      )}
                    </div>

                    {/* Reactions */}
                    {message.reactions && message.reactions.length > 0 && (
                      <div className="flex gap-2 mt-2">
                        {message.reactions.map((reaction, idx) => (
                          <button
                            key={idx}
                            className="bg-white rounded-full px-2 py-1 text-sm border border-gray-200 hover:border-gray-400 transition"
                          >
                            {reaction.emoji} {reaction.count}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {/* Typing Indicators */}
            {typingUsers.length > 0 && (
              <div className="flex gap-3">
                <div className="text-2xl">⌨️</div>
                <div className="flex-1">
                  <div className="text-sm text-gray-600">
                    {typingUsers.map(u => u.user_name).join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
                  </div>
                  <div className="flex gap-1 mt-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Image Preview */}
          {imagePreview && (
            <div className="px-6 py-3 bg-gray-100 border-t border-gray-200">
              <div className="relative inline-block">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="h-24 rounded-lg"
                />
                <button
                  onClick={() => {
                    setImagePreview(null);
                    setSelectedImage(null);
                  }}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Emoji Picker */}
          {showEmojiPicker && (
            <div className="px-6 py-3 bg-gray-100 border-t border-gray-200 flex gap-2 flex-wrap">
              {emojis.map((emoji) => (
                <button
                  key={emoji}
                  onClick={() => handleAddEmoji(emoji)}
                  className="text-2xl hover:scale-125 transition"
                >
                  {emoji}
                </button>
              ))}
            </div>
          )}

          {/* Input Area */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex items-end gap-3">
              {/* Image Upload */}
              <label className="cursor-pointer p-2 hover:bg-gray-100 rounded-lg transition">
                <Image className="w-6 h-6 text-gray-600" />
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                />
              </label>

              {/* Emoji Picker */}
              <button
                onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <Smile className="w-6 h-6 text-gray-600" />
              </button>

              {/* Message Input */}
              <input
                type="text"
                value={messageText}
                onChange={handleMessageChange}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type a message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />

              {/* Send Button */}
              <button
                onClick={handleSendMessage}
                disabled={!messageText.trim() && !selectedImage}
                className="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Group Modal */}
      {showCreateGroup && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Create New Group</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Group Name</label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  placeholder="e.g., Tomato Farmers"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={newGroupDesc}
                  onChange={(e) => setNewGroupDesc(e.target.value)}
                  placeholder="What is this group about?"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowCreateGroup(false);
                    setNewGroupName('');
                    setNewGroupDesc('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateGroup}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Admin Panel Modal */}
      {showAdminPanel && selectedGroup && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <Settings className="w-6 h-6" />
                Group Settings
              </h2>
              <button
                onClick={() => setShowAdminPanel(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Add Member Section */}
              <div className="border-b pb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <UserPlus className="w-5 h-5" />
                  Add Member
                </h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={addMemberMobile}
                    onChange={(e) => setAddMemberMobile(e.target.value)}
                    placeholder="Enter mobile number"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <button
                    onClick={handleAddMember}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Delete Group Section */}
              <div className="border-b pb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Trash2 className="w-5 h-5 text-red-600" />
                  Delete Group
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  This will permanently delete the group and all its messages.
                </p>
                <button
                  onClick={handleDeleteGroup}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                >
                  Delete Group
                </button>
              </div>

              {/* Close Button */}
              <button
                onClick={() => setShowAdminPanel(false)}
                className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FarmerCommunity;
