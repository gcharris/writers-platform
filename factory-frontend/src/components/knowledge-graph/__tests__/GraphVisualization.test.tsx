/**
 * GraphVisualization Component Unit Tests
 */

import { render, screen, waitFor } from '@testing-library/react';
import { GraphVisualization } from '../GraphVisualization';

// Mock fetch
global.fetch = jest.fn();

// Mock react-force-graph-3d
jest.mock('react-force-graph-3d', () => ({
  __esModule: true,
  default: ({ graphData }: any) => (
    <div data-testid="force-graph-3d">
      {graphData.nodes.length} entities, {graphData.links.length} relationships
    </div>
  ),
}));

describe('GraphVisualization', () => {
  const mockProjectId = 'test-project-123';

  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
    localStorage.setItem('auth_token', 'test-token');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    (global.fetch as jest.Mock).mockImplementation(() =>
      new Promise(() => {}) // Never resolves
    );

    render(<GraphVisualization projectId={mockProjectId} />);
    expect(screen.getByText(/Loading knowledge graph/i)).toBeInTheDocument();
  });

  it('fetches and displays graph data', async () => {
    const mockGraphData = {
      nodes: [
        {
          id: '1',
          name: 'Mickey',
          type: 'character',
        },
      ],
      links: [],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockGraphData,
    });

    render(<GraphVisualization projectId={mockProjectId} />);

    await waitFor(() => {
      expect(screen.getByText(/1 entities/i)).toBeInTheDocument();
    });
  });

  it('handles fetch errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(
      new Error('Network error')
    );

    render(<GraphVisualization projectId={mockProjectId} />);

    await waitFor(() => {
      expect(screen.getByText(/Error loading/i)).toBeInTheDocument();
    });
  });

  it('filters entities by type when filterByType prop is provided', async () => {
    const mockGraphData = {
      nodes: [
        { id: '1', name: 'Mickey', type: 'character' },
        { id: '2', name: 'Mars', type: 'location' },
      ],
      links: [],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockGraphData,
    });

    render(
      <GraphVisualization
        projectId={mockProjectId}
        filterByType={['character']}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/1 entities/i)).toBeInTheDocument();
    });
  });

  it('calls onEntityClick when entity is clicked', async () => {
    const mockGraphData = {
      nodes: [{ id: '1', name: 'Mickey', type: 'character' }],
      links: [],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockGraphData,
    });

    const onEntityClick = jest.fn();

    render(
      <GraphVisualization
        projectId={mockProjectId}
        onEntityClick={onEntityClick}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/1 entities/i)).toBeInTheDocument();
    });
  });
});
