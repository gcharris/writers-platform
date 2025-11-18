// User types
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username?: string;
  email: string;
  password: string;
}

// Project types
export interface Project {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  genre: string | null;
  status: 'draft' | 'analyzing' | 'analyzed' | 'published';
  word_count: number;
  scene_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface ProjectCreate {
  title: string;
  description?: string;
  genre?: string;
}

export interface ProjectUpdate {
  title?: string;
  description?: string;
  genre?: string;
  status?: string;
}

// Scene types
export interface Scene {
  id: string;
  project_id: string;
  content: string;
  title: string | null;
  chapter_number: number | null;
  scene_number: number | null;
  sequence: number;
  word_count: number;
  created_at: string;
}

export interface SceneCreate {
  content: string;
  title?: string;
  chapter_number?: number;
  scene_number?: number;
}

// Analysis types
export interface AnalysisRequest {
  scene_outline: string;
  chapter?: string;
  context_requirements?: string[];
  agents?: string[];
  synthesize?: boolean;
}

export interface AnalysisStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  scene_outline: string;
  chapter: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface AnalysisResult {
  id: string;
  status: string;
  scene_outline: string;
  chapter: string | null;
  started_at: string | null;
  completed_at: string | null;
  summary: {
    best_agent: string;
    best_score: number;
    hybrid_score: number | null;
    total_cost: number;
    total_tokens: number;
  } | null;
  full_results: any;
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
  cost_per_1k_tokens: number;
}
