/**
 * Knowledge Graph End-to-End Tests
 * Uses Playwright for full browser testing
 */

import { test, expect } from '@playwright/test';

test.describe('Knowledge Graph E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login (adjust based on your auth flow)
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await page.waitForURL('/dashboard');
  });

  test('can view knowledge graph visualization', async ({ page }) => {
    // Navigate to project
    await page.click('text=Test Project');

    // Open knowledge graph
    await page.click('text=Knowledge Graph');

    // Wait for graph to load
    await expect(page.locator('.knowledge-graph')).toBeVisible();
    await expect(page.locator('canvas')).toBeVisible();

    // Check stats are displayed
    await expect(page.locator('text=/\\d+ entities/i')).toBeVisible();
  });

  test('can search and select entities', async ({ page }) => {
    await page.goto('/projects/test-project-123/knowledge-graph');

    // Search for entity
    await page.fill('input[placeholder*="Search"]', 'Mickey');
    await page.click('button:has-text("Search")');

    // Wait for results
    await expect(page.locator('.search-result-item')).toBeVisible();

    // Click first result
    await page.click('.search-result-item:first-child');

    // Entity details should appear
    await expect(page.locator('.entity-details-panel')).toBeVisible();
    await expect(page.locator('h2:has-text("Mickey")')).toBeVisible();
  });

  test('can trigger extraction from scene editor', async ({ page }) => {
    await page.goto('/projects/test-project-123/scenes/scene-456');

    // Enable auto-extraction
    await page.check('input[type="checkbox"]:has-text("Auto-extract")');

    // Edit scene
    await page.fill('textarea.scene-content-editor', 'Mickey walked on Mars.');

    // Save
    await page.click('button:has-text("Save Scene")');

    // Wait for save confirmation
    await expect(page.locator('text=/saved/i')).toBeVisible({
      timeout: 5000,
    });
  });

  test('can export graph to GraphML', async ({ page }) => {
    await page.goto('/projects/test-project-123/knowledge-graph');

    // Open export panel
    await page.click('text=Export');

    // Start download
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Export to GraphML")');

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.graphml');
  });

  test('can browse entities with filters', async ({ page }) => {
    await page.goto('/projects/test-project-123/knowledge-graph');

    // Open entity browser
    await page.click('text=Entities');

    // Filter by character type
    await page.click('.type-filter-btn:has-text("Character")');

    // Verify filtered results
    await expect(page.locator('.entity-item')).toHaveCount(
      await page.locator('.entity-item .entity-type-badge:has-text("character")').count()
    );
  });

  test('can view entity details and relationships', async ({ page }) => {
    await page.goto('/projects/test-project-123/knowledge-graph');

    // Click on an entity
    await page.click('.entity-item:first-child');

    // Entity details modal should open
    await expect(page.locator('.entity-details')).toBeVisible();

    // Check relationships tab
    await page.click('button:has-text("Relationships")');

    // Relationships should be visible
    await expect(page.locator('.relationship-item')).toBeVisible();
  });

  test('can use graph-powered search', async ({ page }) => {
    await page.goto('/projects/test-project-123/knowledge-graph');

    // Open search
    await page.click('text=Search');

    // Enter search query
    await page.fill('input[placeholder*="Search knowledge graph"]', 'protagonist');

    // Select semantic search
    await page.selectOption('select.search-type-select', 'semantic');

    // Perform search
    await page.click('button:has-text("Search")');

    // Wait for results
    await expect(page.locator('.search-result-item')).toBeVisible();

    // Verify relevance scores are shown
    await expect(page.locator('.relevance-score')).toBeVisible();
  });

  test('can view analytics dashboard', async ({ page }) => {
    await page.goto('/projects/test-project-123/knowledge-graph');

    // Open analytics
    await page.click('text=Analytics');

    // Verify stats are displayed
    await expect(page.locator('text=/Total Entities/i')).toBeVisible();
    await expect(page.locator('text=/Total Relationships/i')).toBeVisible();
    await expect(page.locator('text=/Most Central Entities/i')).toBeVisible();
  });
});
