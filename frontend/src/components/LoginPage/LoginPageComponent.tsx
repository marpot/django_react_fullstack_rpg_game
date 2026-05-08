import React from 'react';
import LoginContainer from "./LoginContainer";
import LoginSection from "./LoginSection";
import { handleSubmit } from './SubmitHandler';
import MedievalBackground from './MedievalBackground';

const LoginPageComponent = () => {
    return (
        <LoginContainer>
            <MedievalBackground />
            <div className="title has-text-centered mb-4">
                <h1>Witaj w Średniowiecznym RPG</h1>
                <p className="subtitle">Zaloguj się, aby rozpocząć przygodę</p>
            </div>
            <LoginSection errorMessage='' onSubmit={handleSubmit} />
        </LoginContainer>
    );
};

export default LoginPageComponent;
export{};
