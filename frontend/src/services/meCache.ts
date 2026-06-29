import { api } from "@/api/client";

let mePromise: Promise<any> | null = null;

export const getMe = async () => {
  if (!mePromise) {
    mePromise = api.get("/accounts/me/").then((r) => r.data);
  }

  return mePromise;
};