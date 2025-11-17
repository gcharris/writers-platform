import { apiClient } from './client';
import type {
  LoginCredentials,
  RegisterData,
  User,
  Project,
  ProjectCreate,
  ProjectUpdate,
  Scene,
  SceneCreate,
  AnalysisRequest,
  AnalysisStatus,
  AnalysisResult,
  AIModel,
} from '../types';

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await apiClient.post('/auth/login', credentials);
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

// Projects API
export const projectsApi = {
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post('/projects/', data);
    return response.data;
  },

  upload: async (file: File, title?: string, description?: string, genre?: string): Promise<Project> => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);
    if (genre) formData.append('genre', genre);

    const response = await apiClient.post('/projects/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (): Promise<Project[]> => {
    const response = await apiClient.get('/projects/');
    return response.data;
  },

  get: async (id: string): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },

  update: async (id: string, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.put(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },

  getScenes: async (projectId: string): Promise<Scene[]> => {
    const response = await apiClient.get(`/projects/${projectId}/scenes`);
    return response.data;
  },

  addScene: async (projectId: string, scene: SceneCreate): Promise<Scene> => {
    const response = await apiClient.post(`/projects/${projectId}/scenes`, scene);
    return response.data;
  },
};

// Analysis API
export const analysisApi = {
  run: async (projectId: string, request: AnalysisRequest) => {
    const response = await apiClient.post(`/analysis/run?project_id=${projectId}`, request);
    return response.data;
  },

  getStatus: async (jobId: string): Promise<AnalysisStatus> => {
    const response = await apiClient.get(`/analysis/${jobId}/status`);
    return response.data;
  },

  getResults: async (jobId: string): Promise<AnalysisResult> => {
    const response = await apiClient.get(`/analysis/${jobId}/results`);
    return response.data;
  },

  listProjectAnalyses: async (projectId: string) => {
    const response = await apiClient.get(`/analysis/project/${projectId}/analyses`);
    return response.data;
  },

  getModels: async (): Promise<{ models: AIModel[]; default: string[] }> => {
    const response = await apiClient.get('/analysis/models');
    return response.data;
  },
};
