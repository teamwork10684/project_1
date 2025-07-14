import axios from 'axios';
import { message } from 'ant-design-vue';
import router from '../router';

//计划6天之内初步完成

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/popquiz',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // token过期或无效
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      message.error('登录已过期，请重新登录');
      router.push('/auth');
    }
    return Promise.reject(error);
  }
);

// 用户管理API
export const userAPI = {
  // 用户注册
  register: (data) => api.post('/register', data),
  
  // 用户登录
  login: (data) => api.post('/login', data),
  
  // 用户退出登录
  logout: (data) => api.post('/logout', data),
  
  // 获取用户参与的所有演讲室
  getUserSpeechRooms: (token) => api.get(`/user/speech-rooms?token=${token}`),
  
  // 获取用户所有被邀请记录
  getUserInvitations: (token) => api.get(`/user/invitations?token=${token}`),
  
  // 获取用户创建的所有演讲室
  getUserCreatedRooms: (token, params = {}) => {
    const queryParams = new URLSearchParams({ token, ...params });
    return api.get(`/user/created-rooms?${queryParams}`);
  },
};

// 演讲室管理API
export const speechRoomAPI = {
  // 创建演讲室
  createSpeechRoom: (data) => api.post('/speech-rooms', data),
  
  // 加入演讲室
  joinRoom: (data) => api.post('/join-room', data),
  
  // 进入房间获取房间信息和角色信息
  enterRoom: (roomId, token) => api.get(`/speech-rooms/${roomId}/enter?token=${token}`),
  
  // 开始演讲
  startSpeech: (roomId, token) => api.post(`/speech-rooms/${roomId}/start`, { token }),
  
  // 结束演讲
  endSpeech: (roomId, token) => api.post(`/speech-rooms/${roomId}/end`, { token }),
  
  // 获取演讲室参与总人数
  getRoomParticipantsCount: (roomId, token) => api.get(`/speech-rooms/${roomId}/participants/count?token=${token}`),
  
  // 获取演讲室在线人员列表
  getRoomOnlineParticipants: (roomId, token) => api.get(`/speech-rooms/${roomId}/online-participants?token=${token}`),
  
  // 获取指定演讲室的所有题目
  getRoomQuestions: (roomId, token) => api.get(`/speech-rooms/${roomId}/questions?token=${token}`),
};

// 邀请管理API
export const invitationAPI = {
  // 发起邀请
  inviteUser: (data) => api.post('/invitations', data),
  
  // 接受邀请
  acceptInvitation: (data) => api.post('/invitations/accept', data),
  
  // 拒绝邀请
  rejectInvitation: (data) => api.post('/invitations/reject', data),
};

// 答题API
export const answerAPI = {
  // 听众答题
  answerQuestion: (roomId, data) => api.post(`/speech-rooms/${roomId}/answer-question`, data),
};

// 题目管理API
export const questionAPI = {
  // 根据文本申请创建题目
  requestQuestionsByText: (data) => api.post('/request-questions-by-text', data),
  
  // 发布题目
  publishQuestion: (roomId, data) => api.post(`/speech-rooms/${roomId}/publish-question`, data),
  
  // 获取房间最新发布还未结束的题目（演讲者和组织者）
  getCurrentQuestionForSpeakerAndOrganizer: (roomId, token) => api.get(`/speech-rooms/${roomId}/current-question-for-speaker-and-organizer?token=${token}`),
  
  // 获取房间最新发布还未结束的题目（听众）
  getCurrentQuestionForAudience: (roomId, token) => api.get(`/speech-rooms/${roomId}/current-question-for-audience?token=${token}`),
  
  // 获取题目答题情况统计（演讲者和组织者）
  getQuestionStatisticsForSpeakerAndOrganizer: (publishedQuestionId, token) => api.get(`/published-questions/${publishedQuestionId}/statistics-for-speaker-and-organizer?token=${token}`),
  
  // 获取题目答题情况统计（听众）
  getQuestionStatisticsForAudience: (publishedQuestionId, token) => api.get(`/published-questions/${publishedQuestionId}/statistics-for-audience?token=${token}`),
};

// 讨论管理API
export const discussionAPI = {
  // 发表讨论
  createDiscussion: (data) => api.post('/discussions', data),
  
  // 获取讨论列表
  getDiscussions: (roomId, token) => api.get(`/discussions?room_id=${roomId}&token=${token}`),
  
  // 获取指定题目的所有讨论
  getQuestionDiscussions: (questionId, token) => api.get(`/questions/${questionId}/discussions?token=${token}`),
};

// 工具函数
export const checkTokenExpired = () => {
  const token = localStorage.getItem('token');
  if (!token) {
    message.error('请先登录');
    router.push('/auth');
    return true;
  }
  return false;
};

// 获取本地存储的token
export const getToken = () => {
  return localStorage.getItem('token');
};

// 获取本地存储的用户名
export const getUsername = () => {
  return localStorage.getItem('username');
};

export default api; 