import apiClient from './client';

export const getBooksApi = (params) => 
  apiClient.get('/books', { params });

export const getBookApi = (id) => 
  apiClient.get(`/books/${id}`);

export const addBookApi = (data) => 
  apiClient.post('/books', data);

export const getBookReviewsApi = (bookId, params) => 
  apiClient.get(`/books/${bookId}/reviews`, { params });

export const submitReviewApi = (bookId, data) => 
  apiClient.post(`/books/${bookId}/reviews`, data);
