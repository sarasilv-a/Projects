import { createRouter, createWebHistory } from "vue-router";
import { useSessionStore } from "@/stores/session";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
    },
    {
      path: "/recover-password",
      name: "recover-password",
      component: () => import("@/views/RecoverPasswordView.vue"),
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
    },
    {
      path: "/access-denied",
      name: "AccessDenied",
      component: () => import("@/views/AccessDeniedView.vue"),
    },

    // Aluno
    {
      path: "/student/schedule",
      name: "student-schedule",
      component: () => import("@/views/student/ScheduleView.vue"),
      meta: { requiresAuth: true, role: "student" },
    },
    {
      path: "/student/profile",
      name: "student-profile",
      component: () => import("@/views/student/ProfileView.vue"),
      meta: { requiresAuth: true, role: "student" },
    },

    // Diretor
    {
      path: "/director/schedule",
      name: "director-schedule",
      component: () => import("@/views/director/ScheduleView.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
    {
      path: "/director/shifts",
      name: "shifts",
      component: () => import("@/views/director/ShiftsView.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
    {
      path: "/director/students",
      name: "students",
      component: () => import("@/views/director/StudentsView.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
    {
      path: "/director/profile",
      name: "director-profile",
      component: () => import("@/views/director/ProfileView.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
    {
      path: "/director/dashboard",
      name: "director-dashboard",
      component: () => import("@/views/director/DashboardView.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
    {
      path: "/director/notifications",
      name: "director-notifications",
      component: () => import("@/views/director/NotificationsView.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
    {
      path: "/director/manualAlloc",
      name: "director-manualAlloc",
      component: () => import("@/views/director/ManualAlloc.vue"),
      meta: { requiresAuth: true, role: "director" },
    },
  ],
});

router.beforeEach((to, from, next) => {
  const session = useSessionStore();

  // Se não requer autenticação, segue
  if (!to.meta.requiresAuth) {
    return next();
  }

  // Se não está autenticado, redireciona para login
  if (!session.isLoggedIn) {
    return next("/login");
  }

  // Se a rota requer um papel específico (student/director), valida
  const role = to.meta.role;
  if (role && session.type !== role) {
    return next("/access-denied");
  }

  next();
});

export default router;
