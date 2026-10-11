import apiClient from './client';

export const getDashboardSummaryApi = () => 
  apiClient.get('/dashboard/summary');

export const getDashboardTrendsApi = (days = 30) => 
  apiClient.get('/dashboard/trends', { params: { days } });

export const getDashboardCategoriesApi = () => 
  apiClient.get('/dashboard/categories');

export const getDashboardInsightsApi = () => 
  apiClient.get('/dashboard/insights');

export const getReportsApi = (params) => 
  apiClient.get('/reports/comments', { params });

export const exportReportCsvApi = (params) => 
  apiClient.get('/reports/export.csv', { params, responseType: 'blob' });
