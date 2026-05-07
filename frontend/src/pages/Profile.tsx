import React, { useState, useEffect, ProfilerProps } from 'react';
import { useNavigate } from 'react-router-dom';

interface ProfileProps {} {

}

const Profile: React.FC<ProfilerProps> = () => {
    const navigate = useNavigate();

    return (
        // TODO: implement profile logic
        <div>Profile content</div>
    );
};

export default Profile;