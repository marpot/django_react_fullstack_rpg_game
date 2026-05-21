export const authStorage = {
  getAccess: (): string | null => {
    return localStorage.getItem("access_token");
  },

  getRefresh: (): string | null => {
    return localStorage.getItem("refresh_token");
  },

  setTokens: (access: string, refresh: string): void => {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  },

  clear: (): void => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};