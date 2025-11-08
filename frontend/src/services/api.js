import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Categories
export const getCategories = () => api.get('/categories');
export const createCategory = (data) => api.post('/categories', data);
export const updateCategory = (id, data) => api.put(`/categories/${id}`, data);
export const deleteCategory = (id) => api.delete(`/categories/${id}`);

// Subcategories
export const createSubcategory = (data) => api.post('/categories/subcategories', data);
export const updateSubcategory = (id, data) => api.put(`/categories/subcategories/${id}`, data);
export const deleteSubcategory = (id) => api.delete(`/categories/subcategories/${id}`);

// Items
export const getItems = (params) => api.get('/items', { params });
export const getItem = (id) => api.get(`/items/${id}`);
export const createItem = (data) => api.post('/items', data);
export const updateItem = (id, data) => api.put(`/items/${id}`, data);
export const deleteItem = (id) => api.delete(`/items/${id}`);

// Bills
export const getBills = (params) => api.get('/bills', { params });
export const getBill = (id) => api.get(`/bills/${id}`);
export const createBill = (data) => api.post('/bills', data);
export const updateBill = (id, data) => api.put(`/bills/${id}`, data);
export const deleteBill = (id) => api.delete(`/bills/${id}`);
export const getSpendingSummary = (params) => api.get('/bills/stats/summary', { params });
export const getStoreSummary = (params) => api.get('/bills/stats/by-store', { params });

// OCR
export const scanBill = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/ocr/scan', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const scanAndSaveBill = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/ocr/scan-and-save', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export default api;
