import { createRouter, createWebHistory } from 'vue-router';
import AdminMain from '../views/AdminMain.vue';

const routes = [
    {
        path: '/',
        name: 'AdminMain',
        component: AdminMain,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router; 