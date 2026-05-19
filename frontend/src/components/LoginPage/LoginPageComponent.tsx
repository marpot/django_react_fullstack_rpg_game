import React from 'react';
import LoginContainer from "./LoginContainer";
import LoginSection from "./LoginSection";
import { handleSubmit } from './SubmitHandler';
import "./LoginPage.scss";

const LoginPageComponent = () => {
    return (
        <div className="login-page">
            <LoginContainer className="login-panel">
                <div className="login-title">
                    <h1>Witaj w Średniowiecznym RPG</h1>
                    <p className="subtitle">
                        Zaloguj się, 
                    </p>
                </div>

                <LoginSection errorMessage="" onSubmit={handleSubmit} />
            </LoginContainer>
        </div>
    );
};

export default LoginPageComponent;