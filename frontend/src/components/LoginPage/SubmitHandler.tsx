import { api } from '../../api/client';

export const handleSubmit = async (data: { username: string; password: string }) => {
  try {
    const response = await api.post('/accounts/login/', data);   
     console.log('✅ Zalogowano', response.data);
  } catch (error) {
    console.error('❌ Błąd logowania:', error);
  }
};
