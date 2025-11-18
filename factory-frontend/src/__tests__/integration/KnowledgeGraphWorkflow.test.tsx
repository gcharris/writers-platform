/**
 * Knowledge Graph Workflow Integration Tests
 * Tests the complete workflow from editing to extraction to visualization
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SceneEditorWithKnowledgeGraph } from '../../components/editor/SceneEditorWithKnowledgeGraph';

global.fetch = jest.fn();

// Mock react-force-graph-3d
jest.mock('react-force-graph-3d', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-graph">Mock Graph</div>,
}));

describe('Knowledge Graph Workflow Integration', () => {
  const mockProjectId = 'test-project-123';
  const mockSceneId = 'scene-456';
  const initialContent = 'Mickey met Sarah on Mars.';

  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
    localStorage.setItem('auth_token', 'test-token');
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('completes full workflow: edit → save → extract → display', async () => {
    // Mock API responses
    (global.fetch as jest.Mock)
      // Fetch initial entities for highlighting
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })
      // Save scene
      .mockResolvedValueOnce({ ok: true })
      // Trigger extraction
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: 'job-789' }),
      })
      // Check extraction status (polling)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'completed',
          entities_found: 3,
          relationships_found: 2,
        }),
      })
      // Fetch entities for highlighting after extraction
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: '1', name: 'Mickey', type: 'character' },
          { id: '2', name: 'Sarah', type: 'character' },
          { id: '3', name: 'Mars', type: 'location' },
        ],
      });

    const mockOnSave = jest.fn().mockResolvedValue(undefined);

    render(
      <SceneEditorWithKnowledgeGraph
        projectId={mockProjectId}
        sceneId={mockSceneId}
        initialContent={initialContent}
        onSave={mockOnSave}
      />
    );

    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Write your scene/i)).toBeInTheDocument();
    });

    // Edit content
    const textarea = screen.getByPlaceholderText(/Write your scene/i);
    fireEvent.change(textarea, {
      target: { value: 'Mickey met Sarah on Mars. They explored the colony.' },
    });

    // Save
    const saveBtn = screen.getByText(/Save Scene/i);
    fireEvent.click(saveBtn);

    // Wait for save to complete
    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalled();
    });

    // Fast-forward polling
    await act(async () => {
      jest.advanceTimersByTime(2000);
      await Promise.resolve();
    });

    // Verify extraction was triggered
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/extract'),
      expect.any(Object)
    );
  });

  it('allows toggling auto-extraction', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    const mockOnSave = jest.fn().mockResolvedValue(undefined);

    render(
      <SceneEditorWithKnowledgeGraph
        projectId={mockProjectId}
        sceneId={mockSceneId}
        initialContent={initialContent}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Write your scene/i)).toBeInTheDocument();
    });

    // Disable auto-extraction
    const checkbox = screen.getByLabelText(/Auto-extract entities/i);
    fireEvent.click(checkbox);

    // Save
    const saveBtn = screen.getByText(/Save Scene/i);
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalled();
    });

    // Extraction should not be triggered
    expect(global.fetch).not.toHaveBeenCalledWith(
      expect.stringContaining('/extract'),
      expect.any(Object)
    );
  });

  it('displays entity mentions count', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => [
        { id: '1', name: 'Mickey', type: 'character' },
        { id: '2', name: 'Mars', type: 'location' },
      ],
    });

    const mockOnSave = jest.fn();

    render(
      <SceneEditorWithKnowledgeGraph
        projectId={mockProjectId}
        sceneId={mockSceneId}
        initialContent="Mickey walked on Mars."
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/2 entities mentioned/i)).toBeInTheDocument();
    });
  });
});
