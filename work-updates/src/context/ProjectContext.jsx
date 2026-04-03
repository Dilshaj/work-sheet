import React, { createContext, useState, useContext, useEffect } from 'react';
import { getProjects, addProject as apiAddProject, updateProject as apiUpdateProject, deleteProject as apiDeleteProject } from '../services/projectService';

const ProjectContext = createContext();

export const ProjectProvider = ({ children }) => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getProjects().then(data => {
            setProjects(data);
            setLoading(false);
        });
    }, []);

    const addProject = async (projectObj) => {
        const newProj = await apiAddProject(projectObj);
        setProjects(prev => [...prev, newProj]);
    };

    const editProject = async (id, data) => {
        const updated = await apiUpdateProject(id, data);
        setProjects(prev => prev.map(p => p.id === id ? updated : p));
    };

    const removeProject = async (id) => {
        await apiDeleteProject(id);
        setProjects(prev => prev.filter(p => p.id !== id));
    };

    return (
        <ProjectContext.Provider value={{ projects, loading, addProject, editProject, removeProject }}>
            {children}
        </ProjectContext.Provider>
    );
};

export const useProjects = () => useContext(ProjectContext);
