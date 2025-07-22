import axios from 'axios';
import { message } from 'ant-design-vue';
import router from '../router';

// ����axiosʵ��
const api = axios.create({
    baseURL: 'http://localhost:5000/popquiz',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ���������� - ���token
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

// ��Ӧ������ - ����token����
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response?.status === 401) {
            // token���ڻ���Ч
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            message.error('��¼�ѹ��ڣ������µ�¼');
            router.push('/auth');
        }
        return Promise.reject(error);
    }
);

// �û�����API
export const userAPI = {
    // �û�ע��
    register: (data) => api.post('/register', data),

    // �û���¼
    login: (data) => api.post('/login', data),

    // �û��˳���¼
    logout: (data) => api.post('/logout', data),

    // ��ȡ�û�����������ݽ���
    getUserSpeechRooms: (token) => api.get(`/user/speech-rooms?token=${token}`),

    // ��ȡ�û����б������¼
    getUserInvitations: (token) => api.get(`/user/invitations?token=${token}`),

    // ��ȡ�û������������ݽ���
    getUserCreatedRooms: (token, params = {}) => {
        const queryParams = new URLSearchParams({ token, ...params });
        return api.get(`/user/created-rooms?${queryParams}`);
    },
    // �����û���cjy������
    addUser: (data) => api.post('/users', data),
    // �༭�û���cjy������
    editUser: (userId, data) => api.put(`/users/${userId}`, data),
};

// �ݽ��ҹ���API
export const speechRoomAPI = {
    // �����ݽ���
    createSpeechRoom: (data) => api.post('/speech-rooms', data),

    // �����ݽ���
    joinRoom: (data) => api.post('/join-room', data),

    // ���뷿���ȡ������Ϣ�ͽ�ɫ��Ϣ
    enterRoom: (roomId, token) => api.get(`/speech-rooms/${roomId}/enter?token=${token}`),

    // ��ʼ�ݽ�
    startSpeech: (roomId, token) => api.post(`/speech-rooms/${roomId}/start`, { token }),

    // �����ݽ�
    endSpeech: (roomId, token) => api.post(`/speech-rooms/${roomId}/end`, { token }),

    // ��ȡ�ݽ��Ҳ���������
    getRoomParticipantsCount: (roomId, token) => api.get(`/speech-rooms/${roomId}/participants/count?token=${token}`),

    // ��ȡ�ݽ���������Ա�б�
    getRoomOnlineParticipants: (roomId, token) => api.get(`/speech-rooms/${roomId}/online-participants?token=${token}`),

    // ��ȡָ���ݽ��ҵ�������Ŀ
    getRoomQuestions: (roomId, token) => api.get(`/speech-rooms/${roomId}/questions?token=${token}`),
};

// �������API
export const invitationAPI = {
    // ��������
    inviteUser: (data) => api.post('/invitations', data),

    // ��������
    acceptInvitation: (data) => api.post('/invitations/accept', data),

    // �ܾ�����
    rejectInvitation: (data) => api.post('/invitations/reject', data),
};

// ����API
export const answerAPI = {
    // ���ڴ���
    answerQuestion: (roomId, data) => api.post(`/speech-rooms/${roomId}/answer-question`, data),
};

// ��Ŀ����API
export const questionAPI = {
    // �����ı����봴����Ŀ
    requestQuestionsByText: (data) => api.post('/request-questions-by-text', data),

    // ������Ŀ
    publishQuestion: (roomId, data) => api.post(`/speech-rooms/${roomId}/publish-question`, data),

    // ��ȡ�������·�����δ��������Ŀ���ݽ��ߺ���֯�ߣ�
    getCurrentQuestionForSpeakerAndOrganizer: (roomId, token) => api.get(`/speech-rooms/${roomId}/current-question-for-speaker-and-organizer?token=${token}`),

    // ��ȡ�������·�����δ��������Ŀ�����ڣ�
    getCurrentQuestionForAudience: (roomId, token) => api.get(`/speech-rooms/${roomId}/current-question-for-audience?token=${token}`),

    // ��ȡ��Ŀ�������ͳ�ƣ��ݽ��ߺ���֯�ߣ�
    getQuestionStatisticsForSpeakerAndOrganizer: (publishedQuestionId, token) => api.get(`/published-questions/${publishedQuestionId}/statistics-for-speaker-and-organizer?token=${token}`),

    // ��ȡ��Ŀ�������ͳ�ƣ����ڣ�
    getQuestionStatisticsForAudience: (publishedQuestionId, token) => api.get(`/published-questions/${publishedQuestionId}/statistics-for-audience?token=${token}`),
};

// ���۹���API
export const discussionAPI = {
    // ��������
    createDiscussion: (data) => api.post('/discussions', data),

    // ��ȡ�����б�
    getDiscussions: (roomId, token) => api.get(`/discussions?room_id=${roomId}&token=${token}`),

    // ��ȡָ����Ŀ����������
    getQuestionDiscussions: (questionId, token) => api.get(`/questions/${questionId}/discussions?token=${token}`),
};

// �����̨API
export const adminAPI = {
    // ��ȡͳ������
    getStats: (token) => api.get('/admin/statistics', { params: { token } }),
    // ��ȡ�����û�
    getUsers: (token) => api.get('/admin/users', { params: { token } }),
    // ɾ���û�
    deleteUser: (id, token) => api.delete(`/admin/users/${id}`, { data: { token } }),
    // ��ȡ�����ݽ���
    getRooms: (token) => api.get('/admin/speech-rooms/all', { params: { token } }),
    // ��ȡ�ݽ��ҳ�Ա
    getRoomMembers: (roomId, token) => api.get(`/admin/speech-rooms/${roomId}/members`, { params: { token } }),
}

// ���ߺ���
export const checkTokenExpired = () => {
    const token = localStorage.getItem('token');
    if (!token) {
        message.error('���ȵ�¼');
        router.push('/auth');
        return true;
    }
    return false;
};

// ��ȡ���ش洢��token
export const getToken = () => {
    return localStorage.getItem('token');
};

// ��ȡ���ش洢���û���
export const getUsername = () => {
    return localStorage.getItem('username');
};

export default api; 