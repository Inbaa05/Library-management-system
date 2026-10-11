import apiClient from './client';

export const loginApi = (email, password) => 
  apiClient.post('/auth/login', { email, password });

export const registerApi = (name, email, password) => 
  apiClient.post('/auth/register', { name, email, password });

export const logoutApi = () => 
  apiClient.post('/auth/logout');

export const getMeApi = () => 
  apiClient.get('/auth/me');

export const changePasswordApi = (oldPassword, newPassword) => 
  apiClient.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword });
