import axios from 'axios';
import { message } from 'ant-design-vue';
import router from '../router';

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
            router.push('/');
        }
        return Promise.reject(error);
    }
);

// 用户管理API
export const userAPI = {
    // 新增用户（cjy新增）
    addUser: (data, token) => api.post('/users', data, { headers: { Authorization: `Bearer ${token}` } }),
    // 编辑用户（cjy新增）
    editUser: (userId, data, token) => api.put(`/users/${userId}`, data, { headers: { Authorization: `Bearer ${token}` } }),
};

// 管理后台API
export const adminAPI = {
    // 获取统计数据
    getStats: (token) => api.get('/admin/statistics', { params: { token } }),
    // 获取所有用户
    getUsers: (token, params = {}) => api.get('/admin/users', { params: { token, ...params } }),
    // 删除用户
    deleteUser: (id, token) => api.delete(`/admin/users/${id}`, { data: { token } }),
    // 获取所有演讲室
    getRooms: (token, params = {}) => api.get('/admin/speech-rooms/all', { params: { token, ...params } }),
    // 获取演讲室成员
    getRoomMembers: (roomId, token) => api.get(`/admin/speech-rooms/${roomId}/members`, { params: { token } }),
}

// 管理员API
export const adminAuthAPI = {
    // 管理员登录
    adminLogin: (data) => api.post('/admin/login', data),
};

// 工具函数
export const checkTokenExpired = () => {
    const token = localStorage.getItem('token');
    if (!token) {
        message.error('请先登录');
        router.push('/');
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