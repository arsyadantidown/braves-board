import axios, { AxiosError, AxiosHeaders } from "axios";
import type { InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../modules/auth/store/auth.store";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const BASE_URL = `${API_BASE_URL}/api/v1`;

const NON_IDEMPOTENT_METHODS = ["post", "put", "patch", "delete"];
const REFRESH_PATH = "/auth/refresh";

type RetriableRequest = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const auth = useAuthStore();
  const token = auth.accessToken;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (
    config.method &&
    NON_IDEMPOTENT_METHODS.includes(config.method.toLowerCase())
  ) {
    config.headers["X-Request-Nonce"] = crypto.randomUUID();
  }

  return config;
});

function handleAuthFailure() {
  const auth = useAuthStore();
  auth.clearSession();

  if (window.location.pathname !== "/") {
    window.location.assign("/");
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequest | undefined;

    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    // Request refresh tidak boleh di-refresh lagi.
    if (originalRequest.url?.includes(REFRESH_PATH)) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    // Satu request hanya boleh dicoba ulang satu kali.
    if (originalRequest._retry) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    const auth = useAuthStore();
    const token = await auth.refreshAccessToken();

    if (!token) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    originalRequest.headers = AxiosHeaders.from(originalRequest.headers);
    originalRequest.headers.set("Authorization", `Bearer ${token}`);

    return api(originalRequest);
  },
);

export default api;
