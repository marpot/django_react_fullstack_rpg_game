import { api } from "../../../api/client";

export const fetchMe = async () => {
  const response = await api.get("/accounts/me/");
  return response.data;
};