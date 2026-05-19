import React from 'react';
import styles from '../css/login-dark.scss';

type Props = {
    children: React.ReactNode;
    className?: string;
}

const LoginContainer = ({ children, className }: Props) => {
    return (
        <div className={`login-container ${className || ''}`}>
            <div className="background-elements">
                <div className="castle"></div>
            </div>
            {children}
        </div>
    )
}

export default LoginContainer;
export{};