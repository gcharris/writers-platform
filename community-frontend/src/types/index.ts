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
  username: string;
  email: string;
  password: string;
}

// Badge types
export interface Badge {
  id: string;
  work_id: string;
  badge_type: 'ai_analyzed' | 'human_verified' | 'human_self' | 'community_upload';
  verified: boolean;
  metadata_json: {
    score?: number;
    confidence?: number;
    models?: string[];
    analysis_date?: string;
  };
  created_at: string;
}

// Work types (published content)
export interface Work {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  genre: string | null;
  content: string;
  word_count: number;
  view_count: number;
  like_count: number;
  factory_project_id: string | null;
  factory_scores: {
    voice?: number;
    pacing?: number;
    character?: number;
    dialogue?: number;
    scene_effectiveness?: number;
    structure?: number;
    originality?: number;
  } | null;
  badges: Badge[];
  author: {
    username: string;
    id: string;
  };
  created_at: string;
  updated_at: string | null;
}

// Upload types
export interface WorkUpload {
  title: string;
  description?: string;
  genre?: string;
  content?: string;
  claim_human_authored: boolean;
}

// Comment types
export interface Comment {
  id: string;
  work_id: string;
  user_id: string;
  content: string;
  author: {
    username: string;
  };
  created_at: string;
}

// Browse filters
export interface BrowseFilters {
  genre?: string;
  badge_type?: string;
  search?: string;
  sort_by?: 'recent' | 'popular' | 'liked';
}
