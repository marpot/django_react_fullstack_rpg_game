import React from "react";
import { Link } from "react-router-dom";
import "./back-to-adventures-button.scss";

const BackToAdventuresButton: React.FC = () => (
  <Link className="back-to-adventures-button" to="/dashboard">
    Wróć do Sali Przygód
  </Link>
);

export default BackToAdventuresButton;
