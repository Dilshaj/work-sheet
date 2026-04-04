import React from 'react';
import { Pencil, Trash2, UserPlus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const ProjectCard = ({ project, onEdit, onDelete, onBodyClick, onAddEmployee }) => {
    return (
        <div className="group relative overflow-hidden rounded-2xl border border-slate-200/60 dark:border-slate-800 bg-white dark:bg-slate-800/50 shadow-sm transition-all duration-300 hover:shadow-xl dark:hover:shadow-indigo-900/20 hover:-translate-y-1 cursor-pointer">
            <div className="aspect-video w-full overflow-hidden bg-slate-50/50 dark:bg-slate-900/30 flex items-center justify-center p-4 border-b border-slate-100 dark:border-slate-800" onClick={() => onBodyClick(project)}>
                <img src={project.image} alt={project.name} className="h-full w-full object-contain transition-transform group-hover:scale-110 drop-shadow-md" />
            </div>

            <div className="p-4" onClick={() => onBodyClick(project)}>
                <h3 className="font-semibold text-lg text-slate-800 dark:text-slate-100 line-clamp-1">{project.name}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Project ID: {project.id}</p>
            </div>

            <div className="absolute right-2 top-2 z-10 hidden flex-col gap-2 rounded-xl bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm p-1.5 shadow-lg group-hover:flex border border-slate-100 dark:border-slate-700">
                {onAddEmployee && (
                    <button
                        onClick={(e) => { e.stopPropagation(); onAddEmployee(project); }}
                        className="rounded-lg p-1.5 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-green-600 dark:hover:text-green-400 transition"
                        title="Add employee"
                    >
                        <UserPlus className="h-4 w-4" />
                    </button>
                )}
                <button
                    onClick={(e) => { e.stopPropagation(); onEdit(project); }}
                    className="rounded-lg p-1.5 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-blue-600 dark:hover:text-blue-400 transition"
                    title="Edit project"
                >
                    <Pencil className="h-4 w-4" />
                </button>
                <button
                    onClick={(e) => { e.stopPropagation(); onDelete(project.id); }}
                    className="rounded-lg p-1.5 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-red-600 dark:hover:text-red-400 transition"
                    title="Delete project"
                >
                    <Trash2 className="h-4 w-4" />
                </button>
            </div>
        </div>
    );
};

export default ProjectCard;
