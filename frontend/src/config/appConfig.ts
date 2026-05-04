type Config = {
  API_URL: string;
  WS_URL: string;
};

const getBaseUrl = () => {
  const host = window.location.hostname;

  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }

  if (host === "localhost" || host === "127.0.0.1") {
    return "http://localhost:8001";
  }

  return "http://backend:8000";
};

export const config: Config = {
  API_URL: getBaseUrl(),
  WS_URL:
    process.env.REACT_APP_WS_URL ||
    (window.location.hostname === "localhost"
      ? "ws://localhost:8001"
      : "ws://backend:8000")
};