import apiClient from './client';

export const submitCommentApi = (data) => 
  apiClient.post('/comments', data);

export const getCommentsApi = (params) => 
  apiClient.get('/comments', { params });

export const getCommentApi = (id) => 
  apiClient.get(`/comments/${id}`);

export const updateCommentApi = (id, data) => 
  apiClient.patch(`/comments/${id}`, data);

export const deleteCommentApi = (id) => 
  apiClient.delete(`/comments/${id}`);
