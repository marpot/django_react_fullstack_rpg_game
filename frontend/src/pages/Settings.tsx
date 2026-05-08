import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface SettingsProps {
  // Add any props you want to pass to the component here
}

const Settings: React.FC<SettingsProps> = () => {
  const [setting, setSetting] = useState<string>('default value');

  useEffect(() => {
    console.log('Component mounted!');
  }, []);

  const navigate = useNavigate();

  return (
    <div>
      <p>Setting: {setting}</p>
      <button onClick={() => setSetting('new value')}>Update Setting</button>
      <button onClick={() => navigate('/dashboard')}>Go to dashboard</button>
    </div>
  );
};

export default Settings;