import api from './api';
const API_URL = 'attendance';

export const getAttendanceLogs = async (projectId = null) => {
    try {
        const params = {};
        if (projectId) params.project_id = projectId;
        const response = await api.get(`${API_URL}/`, { params });
        return response.data;
    } catch (error) {
        console.error('Failed to fetch attendance logs:', error);
        return [];
    }
};

export const getEmployeeAttendance = async (employeeId) => {
    try {
        const response = await api.get(`${API_URL}/${employeeId}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch attendance for ${employeeId}:`, error);
        return [];
    }
};

export const checkIn = async ({ userId, employeeId, userName, projectId = null, latitude = null, longitude = null, location_name = null }) => {
    try {
        const response = await api.post(`${API_URL}/check-in`, {
            employee_id: employeeId,
            latitude,
            longitude,
            location_name
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Failed to check in');
    }
};

export const checkOut = async (userId, employeeId) => {
    try {
        const response = await api.post(`${API_URL}/employee/check-out`, {
            userId,
            employee_id: employeeId
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Failed to check out');
    }
};

export const exportAttendanceToExcel = async () => {
    try {
        const response = await api.get(`${API_URL}/admin/export`, {
            responseType: 'blob',
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'attendance_report.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Export failed:', error);
        throw new Error(error.response?.data?.detail || 'Failed to export attendance data');
    }
};
