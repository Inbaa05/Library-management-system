import apiClient from './client';

export const getModerationQueueApi = (params) => 
  apiClient.get('/moderation/queue', { params });

export const approveCommentApi = (id, note) => 
  apiClient.post(`/moderation/${id}/approve`, { note, confirm: true });

export const flagCommentApi = (id, reason) => 
  apiClient.post(`/moderation/${id}/flag`, { reason, confirm: true });

export const archiveCommentApi = (id, reason) => 
  apiClient.post(`/moderation/${id}/archive`, { reason, confirm: true });

export const restoreCommentApi = (id) => 
  apiClient.post(`/moderation/${id}/restore`, { confirm: true });

export const getModerationHistoryApi = (id) => 
  apiClient.get(`/moderation/${id}/history`);
