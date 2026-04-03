import React, { createContext, useState, useContext, useEffect } from 'react';
import { getTasks, getEmployees, addTask as apiAddTask, updateTaskStatus as apiUpdateStatus, updateEmployeeProgress as apiUpdateProgress, addEmployee as apiAddEmployee, deleteEmployee as apiDeleteEmployee } from '../services/taskService';
import { useProjectFilter } from './ProjectFilterContext';

const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
    const [tasks, setTasks] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const { selectedProjectId } = useProjectFilter();

    useEffect(() => {
        const fetchAll = () => {
            setLoading(true);
            Promise.all([getTasks(), getEmployees(selectedProjectId)]).then(([tasksData, empData]) => {
                setTasks(tasksData);
                setEmployees(empData);
                setLoading(false);
            });
        };

        fetchAll();
        const intervalId = setInterval(fetchAll, 10000); // 10s polling for real-time visibility
        return () => clearInterval(intervalId);
    }, [selectedProjectId]);

    const fetchTasks = async () => {
        const data = await getTasks();
        setTasks(data);
    };

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
        setEmployees(fresh);
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

    return (
        <TaskContext.Provider value={{ tasks, employees, loading, fetchTasks, fetchEmployees, assignTask, changeTaskStatus, updateProgress, addEmployee: addNewEmployee, removeEmployee, refreshEmployees: fetchEmployees }}>
            {children}
        </TaskContext.Provider>
    );
};

export const useTasks = () => useContext(TaskContext);
