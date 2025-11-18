import { apiClient } from './client';
import type {
  LoginCredentials,
  RegisterData,
  User,
  Work,
  WorkUpload,
  Comment,
  BrowseFilters,
  EntitySearchParams,
} from '../types';

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await apiClient.post('/auth/login/json', credentials);
    return response.data;
  },

  register: async (data: RegisterData) => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// Works API
export const worksApi = {
  browse: async (filters?: BrowseFilters): Promise<Work[]> => {
    const response = await apiClient.get('/works/', { params: filters });
    return response.data;
  },

  browseByEntity: async (params: EntitySearchParams): Promise<Work[]> => {
    const response = await apiClient.get('/browse/by-entity', { params });
    return response.data.works || response.data;
  },

  get: async (id: string): Promise<Work> => {
    const response = await apiClient.get(`/works/${id}`);
    return response.data;
  },

  like: async (id: string): Promise<void> => {
    await apiClient.post(`/works/${id}/like`);
  },

  unlike: async (id: string): Promise<void> => {
    await apiClient.delete(`/works/${id}/like`);
  },

  upload: async (file: File, data: WorkUpload): Promise<Work> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', data.title);
    if (data.description) formData.append('description', data.description);
    if (data.genre) formData.append('genre', data.genre);
    formData.append('claim_human_authored', data.claim_human_authored.toString());

    const response = await apiClient.post('/community/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  create: async (data: WorkUpload): Promise<Work> => {
    const response = await apiClient.post('/works/', {
      title: data.title,
      description: data.description,
      genre: data.genre,
      content: data.content,
      claim_human_authored: data.claim_human_authored,
    });
    return response.data;
  },
};

// Comments API
export const commentsApi = {
  list: async (workId: string): Promise<Comment[]> => {
    const response = await apiClient.get(`/works/${workId}/comments`);
    return response.data;
  },

  create: async (workId: string, content: string): Promise<Comment> => {
    const response = await apiClient.post(`/works/${workId}/comments`, { content });
    return response.data;
  },

  delete: async (commentId: string): Promise<void> => {
    await apiClient.delete(`/comments/${commentId}`);
  },
};
