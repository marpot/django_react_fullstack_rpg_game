import React from 'react';
import Button from '../ui/Button';

const SubmitButton: React.FC<{ loading: boolean; }> = ({ loading }) => (
  <div className="field">
    <div className="control">
      <Button type="submit" variant="primary" fullWidth disabled={loading}>
        Utwórz pokój
      </Button>
    </div>
  </div>
);

export default SubmitButton; 