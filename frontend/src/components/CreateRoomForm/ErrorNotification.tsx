import React from "react";
import "../ui/notifications.scss";

interface ErrorNotificationProps {
  error: string | null;
}

const ErrorNotification: React.FC<ErrorNotificationProps> = ({ error }) => {
  if (!error) return null;

  return (
    <div className="error-notification">
      {error}
    </div>
  );
};

export default ErrorNotification;