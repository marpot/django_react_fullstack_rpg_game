import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
// import * as serviceWorkerRegistration from './serviceWorkerRegistration';
import './styles/main.scss';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  // <React.StrictMode>
    <App />
  // </React.StrictMode>
);

// ❌ DISABLED (DEV FIX - prevents cache / routing issues)
// serviceWorkerRegistration.register({
//   onSuccess: () => {
//     console.log('Service Worker zarejestrowany pomyślnie!');
//   },
//   onError: (error: Error) => {
//     console.error('Błąd rejestracji Service Workera:', error);
//   }
// });