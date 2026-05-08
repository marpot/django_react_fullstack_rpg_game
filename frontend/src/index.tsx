import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import 'bulma/css/bulma.min.css';
import * as serviceWorker from './serviceWorkerRegistration';
import manifest from 'public/manifest.json';
import * as serviceWorkerRegistration from './serviceWorkerRegistration';


const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

serviceWorkerRegistration.register({
  onSuccess: () => {
    console.log('Service Worker zarejestrowany pomyślnie!');
  },
  onError: (error: Error) => {
    console.error('Błąd rejestracji Service Workera:', error);
  }
});
