// src/modules/auth/api/auth.api.ts
import api from "../../../app/api";

export interface User {
  id: string;
  email: string;
  full_name: string;
  picture_url?: string;
}

// 🔥 1. Ambil URL login Google dari backend
export async function getGoogleLoginUrl(): Promise<string> {
  const { data } = await api.get("/auth/google/login");

  const url = data?.data?.auth_url || data?.auth_url || data?.url;

  if (!url) {
    throw new Error("URL Google OAuth tidak ditemukan");
  }

  return url;
}

// 🔥 3. Ambil user yang sedang login
export async function getCurrentUser(): Promise<User> {
  const res = await api.get("/auth/me");

  const user = res.data?.data;

  if (!user) {
    throw new Error("User tidak ditemukan");
  }

  return user;
}

// 🔥 5. Logout
export async function logout() {
  try {
    await api.post("/auth/logout");
  } catch (err) {
    console.warn("Logout error:", err);
  }
}
