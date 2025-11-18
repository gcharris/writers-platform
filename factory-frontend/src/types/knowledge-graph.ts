/**
 * Knowledge Graph TypeScript types
 * Matches backend data models
 */

export type EntityType =
  | 'character'
  | 'location'
  | 'object'
  | 'concept'
  | 'event'
  | 'organization'
  | 'theme';

export type RelationType =
  // Character relationships
  | 'knows'
  | 'related_to'
  | 'conflicts_with'
  | 'loves'
  | 'fears'
  | 'works_with'
  | 'leads'
  | 'follows'
  // Spatial relationships
  | 'located_in'
  | 'travels_to'
  | 'owns'
  | 'resides_in'
  // Temporal relationships
  | 'occurs_before'
  | 'occurs_during'
  | 'occurs_after'
  | 'causes'
  | 'results_in'
  // Conceptual relationships
  | 'represents'
  | 'symbolizes'
  | 'relates_to'
  | 'opposes'
  | 'supports'
  // Event relationships
  | 'participates_in'
  | 'witnesses'
  | 'triggers'
  // Organizational
  | 'member_of'
  | 'founded_by'
  | 'controls';

export interface Entity {
  id: string;
  name: string;
  type: EntityType;
  description: string;
  aliases: string[];
  attributes: Record<string, any>;
  first_appearance?: string;
  appearances: string[];
  mentions: number;
  created_at: string;
  updated_at: string;
  confidence: number;
  verified: boolean;
}

export interface Relationship {
  source: string;
  target: string;
  relation: RelationType;
  description: string;
  context: string[];
  scenes: string[];
  strength: number;
  valence: number;
  attributes: Record<string, any>;
  start_scene?: string;
  end_scene?: string;
  created_at: string;
  updated_at: string;
  confidence: number;
  verified: boolean;
}

export interface GraphNode {
  id: string;
  label: string;
  type: EntityType;
  description: string;
  mentions: number;
  verified: boolean;
  group: string;
  [key: string]: any;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  type: RelationType;
  description: string;
  strength: number;
  valence: number;
}

export interface GraphVisualizationData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: {
    project_id: string;
    entity_count: number;
    relationship_count: number;
    last_updated?: string;
  };
}

export interface GraphStats {
  entity_count: number;
  relationship_count: number;
  scene_count: number;
  extraction_stats: {
    total: number;
    successful: number;
    failed: number;
    success_rate: number;
  };
  central_entities: Array<{
    entity_id: string;
    name: string;
    centrality: number;
  }>;
}

export interface ExtractionJob {
  job_id: string;
  project_id: string;
  scene_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  extractor_type: 'llm' | 'ner' | 'hybrid';
  model_name?: string;
  entities_extracted: number;
  relationships_extracted: number;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  error_message?: string;
  tokens_used?: number;
  cost?: number;
  created_at: string;
}

export interface ExtractRequest {
  scene_id: string;
  extractor_type: 'llm' | 'ner' | 'hybrid';
  model_name?: string;
}

export interface PathQueryResult {
  found: boolean;
  path?: string[];
  entities?: Entity[];
  length?: number;
  message?: string;
}
