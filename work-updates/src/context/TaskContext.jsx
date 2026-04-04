import React, { createContext, useState, useContext, useEffect, useCallback, useMemo } from 'react';
import { getTasks, getEmployees, addTask as apiAddTask, updateTaskStatus as apiUpdateStatus, updateEmployeeProgress as apiUpdateProgress, addEmployee as apiAddEmployee, deleteEmployee as apiDeleteEmployee } from '../services/taskService';
import { useProjectFilter } from './ProjectFilterContext';

const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
    const [tasks, setTasks] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const { selectedProjectId } = useProjectFilter();

    const fetchAll = useCallback((silent = false) => {
        if (!silent) setLoading(true);
        Promise.all([getTasks(), getEmployees(selectedProjectId)]).then(([tasksData, empData]) => {
            const normalized = empData.map(emp => {
                let avatar = emp.avatar;
                if (avatar && !avatar.includes('http') && avatar.startsWith('/')) {
                    avatar = `${window.location.host.includes('localhost') ? 'http://localhost:5000' : ''}${avatar}`;
                }
                return { ...emp, avatar };
            });
            setTasks(tasksData);
            setEmployees(normalized);
            setLoading(false);
        });
    }, [selectedProjectId]);

    useEffect(() => {
        fetchAll();
        const intervalId = setInterval(() => fetchAll(true), 15000); // 15s silent polling
        return () => clearInterval(intervalId);
    }, [fetchAll]);

    const fetchTasks = useCallback(async () => {
        const data = await getTasks();
        setTasks(data);
    }, []);

    const assignTask = async (taskObj) => {
        const newTask = await apiAddTask(taskObj);
        setTasks(prev => [...prev, newTask]);
    };

    const changeTaskStatus = async (id, status) => {
        const updated = await apiUpdateStatus(id, status);
        setTasks(prev => prev.map(t => t.id === id ? updated : t));
    };

    const updateProgress = async (empId, newStats) => {
        const updated = await apiUpdateProgress(empId, newStats);
        setEmployees(prev => prev.map(e => e.id === empId ? updated : e));
    };

    const fetchEmployees = async () => {
        const fresh = await getEmployees(selectedProjectId);
        const bustedEmployees = fresh.map(emp => {
            let avatar = emp.avatar;
            if (avatar && !avatar.includes('http') && avatar.startsWith('/')) {
                avatar = `${window.location.origin}${avatar}`;
            }
            if (avatar && !avatar.includes('ui-avatars.com')) {
                avatar = `${avatar.split('?')[0]}?t=${Date.now()}`;
            }
            return { ...emp, avatar };
        });
        setEmployees(bustedEmployees);
    };

    const addNewEmployee = async (employeeData) => {
        const newEmployee = await apiAddEmployee(employeeData);
        // Immediately show the new employee in the list (optimistic update)
        setEmployees(prev => [...prev, newEmployee]);
        // Then re-fetch from server to ensure correct ordering and project filtering
        const fresh = await getEmployees(selectedProjectId);
        setEmployees(fresh);
        return newEmployee;
    };

    const removeEmployee = async (employeeId) => {
        // Optimistic update - remove from UI instantly as requested
        setEmployees(prev => prev.filter(emp => emp.employeeId !== employeeId));

        try {
            await apiDeleteEmployee(employeeId);
        } catch (error) {
            // Revert on failure
            const fresh = await getEmployees(selectedProjectId);
            setEmployees(fresh);
            throw error;
        }
    };

    const value = useMemo(() => ({
        tasks,
        employees,
        loading,
        fetchTasks,
        fetchEmployees,
        assignTask,
        changeTaskStatus,
        updateProgress,
        addEmployee: addNewEmployee,
        removeEmployee,
        refreshEmployees: fetchEmployees
    }), [tasks, employees, loading, fetchTasks, fetchEmployees, assignTask, changeTaskStatus, updateProgress, addNewEmployee, removeEmployee]);

    return (
        <TaskContext.Provider value={value}>
            {children}
        </TaskContext.Provider>
    );
};

export const useTasks = () => useContext(TaskContext);
