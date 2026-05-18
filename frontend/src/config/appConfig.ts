type Config = {
  API_URL: string;
  WS_URL: string;
};

const isLocal =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

const getApiUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }

  return isLocal ? "http://localhost:8001" : window.location.origin;
};

const getWsUrl = () => {
  if (process.env.REACT_APP_WS_URL) {
    return process.env.REACT_APP_WS_URL;
  }

  return isLocal ? "ws://localhost:8001" : `ws://${window.location.host}`;
};

export const config: Config = {
  API_URL: getApiUrl(),
  WS_URL: getWsUrl(),
};