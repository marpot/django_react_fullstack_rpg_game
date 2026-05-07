import React from 'react';

const SubmitButton: React.FC<{ loading: boolean; }> = ({ loading }) => (
  <div className="field">
    <div className="control">
      <button type="submit" className={`button is-primary ${loading ? 'is-loading' : ''}`} disabled={loading}>
        Utwórz pokój
      </button>
    </div>
  </div>
);

export default SubmitButton; 