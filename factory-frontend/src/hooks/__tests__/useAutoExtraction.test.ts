/**
 * useAutoExtraction Hook Unit Tests
 */

import { renderHook, act } from '@testing-library/react-hooks';
import { useAutoExtraction } from '../useAutoExtraction';

global.fetch = jest.fn();

describe('useAutoExtraction', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
    localStorage.setItem('auth_token', 'test-token');
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('triggers extraction when enabled', async () => {
    const mockProjectId = 'test-project-123';
    const mockSceneId = 'scene-456';
    const mockSceneContent = 'Mickey walked on Mars.';

    (global.fetch as jest.Mock)
      // Initial extraction request
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ job_id: 'job-789', status: 'pending' }),
      })
      // Status polling
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'completed' }),
      });

    const onExtractionStart = jest.fn();
    const onExtractionComplete = jest.fn();

    const { result } = renderHook(() =>
      useAutoExtraction({
        projectId: mockProjectId,
        enabled: true,
        extractorType: 'ner',
        onExtractionStart,
        onExtractionComplete,
      })
    );

    await act(async () => {
      await result.current.extractFromScene(mockSceneId, mockSceneContent);
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/extract'),
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining(mockSceneContent),
      })
    );

    expect(onExtractionStart).toHaveBeenCalledWith('job-789');

    // Fast-forward polling interval
    await act(async () => {
      jest.advanceTimersByTime(2000);
      await Promise.resolve();
    });

    expect(onExtractionComplete).toHaveBeenCalled();
  });

  it('does not extract when disabled', async () => {
    const { result } = renderHook(() =>
      useAutoExtraction({
        projectId: 'test-project-123',
        enabled: false,
      })
    );

    await act(async () => {
      await result.current.extractFromScene('scene-456', 'Test content');
    });

    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('handles extraction errors gracefully', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();

    (global.fetch as jest.Mock).mockRejectedValueOnce(
      new Error('Extraction failed')
    );

    const { result } = renderHook(() =>
      useAutoExtraction({
        projectId: 'test-project-123',
        enabled: true,
      })
    );

    await act(async () => {
      await result.current.extractFromScene('scene-456', 'Test content');
    });

    expect(consoleError).toHaveBeenCalledWith(
      'Auto-extraction failed:',
      expect.any(Error)
    );

    consoleError.mockRestore();
  });

  it('uses correct extractor type and model', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ job_id: 'job-789' }),
    });

    const { result } = renderHook(() =>
      useAutoExtraction({
        projectId: 'test-project-123',
        enabled: true,
        extractorType: 'llm',
        modelName: 'claude-sonnet-4.5',
      })
    );

    await act(async () => {
      await result.current.extractFromScene('scene-456', 'Test content');
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: expect.stringContaining('claude-sonnet-4.5'),
      })
    );
  });
});
