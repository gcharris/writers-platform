/**
 * 3D Interactive Knowledge Graph Visualization
 * Uses React Force Graph 3D for interactive graph exploration
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { Entity, GraphVisualizationData, GraphNode as GraphNodeType, GraphEdge } from '../../types/knowledge-graph';

interface GraphVisualizationProps {
  projectId: string;
  onEntityClick?: (entityId: string) => void;
  highlightEntities?: string[];  // Entity IDs to highlight
  filterByType?: string[];  // Entity types to show
  height?: number;
}

interface GraphNode extends GraphNodeType {
  x?: number;
  y?: number;
  z?: number;
  color: string;
  size: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
  color: string;
  description: string;
}

const ENTITY_TYPE_COLORS: Record<string, string> = {
  character: '#FF6B6B',      // Red
  location: '#4ECDC4',        // Teal
  object: '#95E1D3',          // Light teal
  concept: '#FFE66D',         // Yellow
  event: '#FF8B94',           // Pink
  organization: '#C7CEEA',    // Light purple
  theme: '#FFDAC1',           // Peach
};

const RELATIONSHIP_TYPE_COLORS: Record<string, string> = {
  knows: '#95E1D3',
  conflicts_with: '#FF6B6B',
  located_in: '#4ECDC4',
  owns: '#FFE66D',
  member_of: '#C7CEEA',
  related_to: '#CCCCCC',
};

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  projectId,
  onEntityClick,
  highlightEntities = [],
  filterByType = [],
  height = 600,
}) => {
  const graphRef = useRef<any>(null);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);

  // Fetch graph data
  useEffect(() => {
    const fetchGraphData = async () => {
      setLoading(true);
      setError(null);

      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(
          `/api/knowledge-graph/projects/${projectId}/graph`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch graph: ${response.statusText}`);
        }

        const data: GraphVisualizationData = await response.json();

        // Convert to React Force Graph format
        const nodes: GraphNode[] = data.nodes.map(node => ({
          ...node,
          color: ENTITY_TYPE_COLORS[node.type] || '#999999',
          size: calculateNodeSize(node),
        }));

        const links: GraphLink[] = data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          type: edge.type,
          description: edge.description,
          color: RELATIONSHIP_TYPE_COLORS[edge.type] || '#CCCCCC',
        }));

        // Apply filters
        let filteredNodes = nodes;
        if (filterByType.length > 0) {
          filteredNodes = nodes.filter(node => filterByType.includes(node.type));

          // Only include links between visible nodes
          const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
          const filteredLinks = links.filter(
            link => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target)
          );

          setGraphData({ nodes: filteredNodes, links: filteredLinks });
        } else {
          setGraphData({ nodes, links });
        }

      } catch (err) {
        console.error('Error fetching graph data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchGraphData();
  }, [projectId, filterByType]);

  // Calculate node size based on entity properties
  const calculateNodeSize = (node: GraphNodeType): number => {
    const baseSize = 5;
    const mentionsMultiplier = Math.log10((node.mentions || 1) + 1);
    return baseSize * (1 + mentionsMultiplier);
  };

  // Handle node click
  const handleNodeClick = useCallback((node: GraphNode) => {
    if (onEntityClick) {
      onEntityClick(node.id);
    }

    // Center camera on clicked node
    if (graphRef.current) {
      const distance = 200;
      const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);

      graphRef.current.cameraPosition(
        {
          x: (node.x || 0) * distRatio,
          y: (node.y || 0) * distRatio,
          z: (node.z || 0) * distRatio,
        },
        node, // lookAt
        3000  // ms transition duration
      );
    }
  }, [onEntityClick]);

  // Custom node rendering
  const nodeThreeObject = useCallback((node: GraphNode) => {
    const isHighlighted = highlightEntities.includes(node.id);
    const isHovered = hoveredNode?.id === node.id;

    // Create sphere geometry
    const geometry = new THREE.SphereGeometry(node.size);
    const material = new THREE.MeshLambertMaterial({
      color: node.color,
      transparent: !isHighlighted && highlightEntities.length > 0,
      opacity: isHighlighted || highlightEntities.length === 0 ? 1 : 0.2,
    });

    const sphere = new THREE.Mesh(geometry, material);

    // Add outline if hovered or highlighted
    if (isHovered || isHighlighted) {
      const outlineGeometry = new THREE.SphereGeometry(node.size * 1.2);
      const outlineMaterial = new THREE.MeshBasicMaterial({
        color: isHighlighted ? '#FFFFFF' : '#FFFF00',
        side: THREE.BackSide,
      });
      const outline = new THREE.Mesh(outlineGeometry, outlineMaterial);
      sphere.add(outline);
    }

    return sphere;
  }, [highlightEntities, hoveredNode]);

  // Custom node label
  const nodeLabel = useCallback((node: GraphNode) => {
    return `
      <div style="
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        max-width: 200px;
      ">
        <div style="font-weight: bold; margin-bottom: 4px;">${node.label}</div>
        <div style="color: #CCCCCC; font-size: 10px;">
          Type: ${node.type}<br/>
          ${node.mentions ? `Mentions: ${node.mentions}` : ''}
        </div>
      </div>
    `;
  }, []);

  // Custom link rendering with labels
  const linkThreeObjectExtend = useCallback((link: GraphLink) => {
    // Add label to relationship
    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: new THREE.CanvasTexture(
          (() => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d')!;
            canvas.width = 256;
            canvas.height = 64;

            ctx.font = '20px Arial';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.textAlign = 'center';
            ctx.fillText(link.type.replace(/_/g, ' '), 128, 32);

            return canvas;
          })()
        ),
      })
    );

    sprite.scale.set(40, 10, 1);
    return sprite;
  }, []);

  if (loading) {
    return (
      <div style={{
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#1a1a1a',
        color: 'white',
      }}>
        <div>Loading knowledge graph...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#1a1a1a',
        color: '#FF6B6B',
      }}>
        <div>Error loading graph: {error}</div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', height }}>
      <ForceGraph3D
        ref={graphRef}
        graphData={graphData}
        nodeId="id"
        nodeLabel={nodeLabel}
        nodeThreeObject={nodeThreeObject}
        nodeAutoColorBy="type"
        linkSource="source"
        linkTarget="target"
        linkColor="color"
        linkWidth={2}
        linkThreeObjectExtend={linkThreeObjectExtend}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        onNodeClick={handleNodeClick}
        onNodeHover={setHoveredNode}
        backgroundColor="#0a0a0a"
        enableNodeDrag={true}
        enableNavigationControls={true}
        showNavInfo={false}
      />

      {/* Graph stats overlay */}
      <div style={{
        position: 'absolute',
        top: 10,
        left: 10,
        background: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        fontSize: '12px',
      }}>
        <div>{graphData.nodes.length} entities</div>
        <div>{graphData.links.length} relationships</div>
      </div>

      {/* Controls overlay */}
      <div style={{
        position: 'absolute',
        top: 10,
        right: 10,
        background: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        fontSize: '11px',
      }}>
        <div>Left click + drag: Rotate</div>
        <div>Right click + drag: Pan</div>
        <div>Scroll: Zoom</div>
        <div>Click node: Focus</div>
      </div>
    </div>
  );
};

export default GraphVisualization;
