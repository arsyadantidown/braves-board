import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import LoginView from "../modules/auth/views/LoginView.vue";
import DashboardView from "../modules/dashboard/views/DashboardView.vue";
import BoardsView from "../modules/board/views/BoardsView.vue";
import BoardsListView from "../modules/board/views/BoardsListView.vue";
import TimeTrackerView from "../modules/timer/views/TimeTrackerView.vue";
import ReportsView from "../modules/reports/views/ReportsView.vue";
import ProjectsView from "../modules/board/views/ProjectsView.vue";
import TeamView from "../modules/team/views/TeamView.vue";
import { useAuthStore } from "../modules/auth/store/auth.store";

const routes: RouteRecordRaw[] = [
  { path: "/", component: LoginView, meta: { public: true } },
  { path: "/dashboard", component: DashboardView },
  { path: "/boards", component: BoardsListView },
  { path: "/boards/:boardId", component: BoardsView },
  { path: "/tracker", component: TimeTrackerView },
  { path: "/reports", component: ReportsView },
  { path: "/projects", component: ProjectsView },
  { path: "/team", component: TeamView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  // Saat browser reload, Pinia kosong. Refresh cookie akan dipakai
  // untuk memperoleh access token baru secara transparan.
  await auth.initialize();

  const isPublic = to.meta.public === true;

  if (!isPublic && !auth.isAuthenticated) {
    return {
      path: "/",
      query: { redirect: to.fullPath },
    };
  }

  if (isPublic && auth.isAuthenticated && to.path === "/") {
    return "/dashboard";
  }

  return true;
});

export default router;
