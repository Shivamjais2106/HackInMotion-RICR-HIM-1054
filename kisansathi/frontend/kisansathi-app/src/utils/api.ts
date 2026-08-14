/**
 * API Utility Functions
 * Handles all API calls with JWT authentication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

/**
 * Get JWT token from localStorage
 */
export const getToken = (): string | null => {
  return localStorage.getItem("access_token") || localStorage.getItem("token");
};

/**
 * Get authorization headers with JWT token
 */
export const getAuthHeaders = (): HeadersInit => {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

/**
 * Generic API call function
 */
export const apiCall = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      // Handle specific error cases
      if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem("access_token");
        localStorage.removeItem("token");
        window.location.href = "/auth";
        throw new Error("Session expired. Please login again.");
      }
      
      if (response.status === 429) {
        throw new Error("Too many requests. Please try again later.");
      }

      throw new Error(data.error || `API Error: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
};

/**
 * Get API base URL (for direct fetch calls)
 */
export const getAPIBaseURL = (): string => {
  return API_BASE_URL;
};

/**
 * Authentication APIs
 */
export const authAPI = {
  register: (userData: any) =>
    apiCall("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    }),

  login: (mobile: string, password: string) =>
    apiCall("/auth/login", {
      method: "POST",
      body: JSON.stringify({ mobile, password }),
    }),

  getProfile: () =>
    apiCall("/auth/profile", {
      method: "GET",
    }),
};

/**
 * Community APIs
 */
export const communityAPI = {
  getGroups: () =>
    apiCall("/community/groups", {
      method: "GET",
    }),

  createGroup: (groupData: any) =>
    apiCall("/community/groups", {
      method: "POST",
      body: JSON.stringify(groupData),
    }),

  getMessages: (groupId: string) =>
    apiCall(`/community/groups/${groupId}/messages`, {
      method: "GET",
    }),

  sendMessage: (groupId: string, messageData: any) =>
    apiCall(`/community/groups/${groupId}/messages`, {
      method: "POST",
      body: JSON.stringify(messageData),
    }),

  deleteMessage: (messageId: string) =>
    apiCall(`/community/messages/${messageId}`, {
      method: "DELETE",
    }),

  addMember: (groupId: string, mobile: string) =>
    apiCall(`/community/groups/${groupId}/add-member`, {
      method: "POST",
      body: JSON.stringify({ mobile }),
    }),

  makeAdmin: (groupId: string, mobile: string) =>
    apiCall(`/community/groups/${groupId}/make-admin`, {
      method: "POST",
      body: JSON.stringify({ mobile }),
    }),

  removeMember: (groupId: string, mobile: string) =>
    apiCall(`/community/groups/${groupId}/remove-member`, {
      method: "POST",
      body: JSON.stringify({ mobile }),
    }),

  deleteGroup: (groupId: string) =>
    apiCall(`/community/groups/${groupId}`, {
      method: "DELETE",
    }),
};

/**
 * Recommendation APIs
 */
export const recommendationAPI = {
  getCropRecommendation: (cropData: any) =>
    apiCall("/recommendations/crop", {
      method: "POST",
      body: JSON.stringify(cropData),
    }),
};

/**
 * Chatbot APIs
 */
export const chatbotAPI = {
  sendMessage: (message: string, conversationHistory: any[] = []) =>
    apiCall("/chatbot/message", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      }),
    }),

  generateVoice: (text: string, language: string = "hi") =>
    apiCall("/chatbot/voice", {
      method: "POST",
      body: JSON.stringify({ text, language }),
    }),
};

/**
 * Livestock APIs
 */
export const livestockAPI = {
  predictDisease: (formData: FormData) =>
    fetch(`${API_BASE_URL}/livestock-disease-predict`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      body: formData,
    }).then((res) => res.json()),

  getDiseases: (animalType: string) =>
    apiCall(`/livestock-diseases/${animalType}`, {
      method: "GET",
    }),
};

/**
 * Health APIs
 */
export const healthAPI = {
  health: () =>
    apiCall("/health", {
      method: "GET",
    }),

  status: () =>
    apiCall("/status", {
      method: "GET",
    }),
};

export default {
  authAPI,
  communityAPI,
  recommendationAPI,
  chatbotAPI,
  livestockAPI,
  healthAPI,
  getToken,
  getAuthHeaders,
  apiCall,
  getAPIBaseURL,
};
