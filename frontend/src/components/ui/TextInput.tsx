import React from 'react';

type Props = {
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  name?: string;
  required?: boolean;
};

const TextInput: React.FC<Props> = ({
  type = 'text',
  value,
  onChange,
  placeholder,
  name,
  required = false,
}) => {
  return (
    <input
      className="app-input"
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      name={name}
      required={required}
    />
  );
};

export default TextInput;