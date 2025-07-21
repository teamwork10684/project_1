import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Auth from '../views/auth/Auth.vue'
import Profile from '../views/Profile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
    },
    {
      path: '/auth',
      name: 'Auth',
      component: Auth,
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile,
    },
  ],
})

// 路由守卫：未登录强制跳转到登录页，已登录访问登录页自动跳转首页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (!token && to.path !== '/auth') {
    next('/auth');
  } else if (token && to.path === '/auth') {
    next('/');
  } else {
    next();
  }
});

export default router
