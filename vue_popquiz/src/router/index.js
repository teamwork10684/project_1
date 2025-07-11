import { createRouter, createWebHistory } from 'vue-router'
import Auth from '../views/auth/Auth.vue'
import Main from '../views/main/Main.vue'
import Demo from '../views/main/Demo.vue'
import Home from '../views/main/Home.vue'
import Room from '../views/main/Room.vue'
import Speakerroom from '../views/main/Speakerroom.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Auth',
      component: Auth,
    },
    {
      path: '/auth',
      name: 'AuthPage',
      component: Auth,
    },
    {
      path: '/main',
      name: 'Main',
      component: Main,
      children: [
        {
          path: '',
          name: 'MainHome',
          component: Home,
        },
        {
          path: 'demo',
          name: 'Demo',
          component: Demo,
        },
        {
          path: 'room',
          name: 'Room',
          component: Room,
        },
        {
          path: 'speakerroom',
          name: 'Speakerroom',
          component: Speakerroom,
        }
      ]
    }
  ],
})

export default router
