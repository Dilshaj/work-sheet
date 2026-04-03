import React, { createContext, useState, useEffect, useContext } from 'react';
import { getAttendanceLogs, checkIn, checkOut } from '../services/attendanceService';
import { useAuth } from './AuthContext';
import { useProjectFilter } from './ProjectFilterContext';

const AttendanceContext = createContext();

export const useAttendance = () => useContext(AttendanceContext);

export const AttendanceProvider = ({ children }) => {
    const { user } = useAuth();
    const { selectedProjectId } = useProjectFilter();
    const [logs, setLogs] = useState([]);
    const [activeLog, setActiveLog] = useState(null);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                // For admin, pass selectedProjectId to filter. For employees, fetch all (their own context).
                const isAdmin = user?.role === 'admin';
                const projId = isAdmin ? selectedProjectId : null;
                const data = await getAttendanceLogs(projId);
                setLogs(data);

                if (user) {
                    const today = new Date().toISOString().split('T')[0];
                    const empId = user.employee_id || user.employeeId;
                    const active = data.find(l => l.employeeId === empId && l.date === today && l.status === 'Checked In');
                    setActiveLog(active || null);
                }
            } catch (error) {
                console.error("Error fetching attendance logs:", error);
            }
        };

        fetchLogs();

        // Polling every 10 seconds for real-time updates on admin dashboard
        const intervalId = setInterval(fetchLogs, 10000);

        return () => clearInterval(intervalId);
    }, [user, selectedProjectId]);

    const handleCheckIn = async () => {
        if (!user) return;
        const empId = user.employee_id || user.employeeId;

        // Capture GPS location if available
        let latitude = null;
        let longitude = null;
        let locationName = null;

        const getPosition = () => {
            return new Promise((resolve) => {
                if (!navigator.geolocation) {
                    resolve(null);
                } else {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
                        () => resolve(null),
                        { timeout: 5000 }
                    );
                }
            });
        };

        const coords = await getPosition();
        if (coords) {
            latitude = coords.lat;
            longitude = coords.lng;

            // Reverse Geocoding via Nominatim
            try {
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`);
                const data = await response.json();
                const address = data.address;
                locationName = address.suburb || address.neighbourhood || address.city_district || address.town || address.city || address.village || "Unknown Area";
                const city = address.city || address.town || address.state || "";
                locationName = locationName !== city ? `${city}, ${locationName}` : city;
            } catch (err) {
                console.error("Geocoding failed", err);
            }
        }

        try {
            const newLog = await checkIn({
                userId: user.id,
                employeeId: empId,
                userName: user.name,
                projectId: selectedProjectId,
                latitude,
                longitude,
                location_name: locationName
            });
            setLogs(prev => [newLog, ...prev]);
            setActiveLog(newLog);
        } catch (error) {
            alert(error.message);
        }
    };

    const handleCheckOut = async () => {
        if (!user) return;
        const empId = user.employee_id || user.employeeId;
        try {
            const updatedLog = await checkOut(user.id, empId);
            if (updatedLog) {
                setLogs(prev => prev.map(l => l.id === updatedLog.id ? updatedLog : l));
                setActiveLog(null);
            }
        } catch (error) {
            alert(error.message);
        }
    };

    const value = {
        logs,
        activeLog,
        handleCheckIn,
        handleCheckOut
    };

    return (
        <AttendanceContext.Provider value={value}>
            {children}
        </AttendanceContext.Provider>
    );
};
