import React from "react";
import "./button.scss";

type ButtonVariant = "primary" | "danger" | "secondary";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  fullWidth = false,
  className = "",
  ...props
}) => {
  return (
    <button
      className={`btn btn-${variant} ${fullWidth ? "btn-full" : ""} ${className}`}
      {...props}
    />
  );
};

export default Button;