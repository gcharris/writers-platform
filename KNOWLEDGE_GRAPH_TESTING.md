# Knowledge Graph Testing Guide

Comprehensive testing documentation for the Writers Platform Knowledge Graph system.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [E2E Tests](#e2e-tests)
- [Performance Tests](#performance-tests)
- [Writing New Tests](#writing-new-tests)
- [Best Practices](#best-practices)

---

## Test Structure

```
factory-frontend/
├── src/
│   ├── components/
│   │   └── knowledge-graph/
│   │       └── __tests__/
│   │           └── GraphVisualization.test.tsx
│   ├── hooks/
│   │   └── __tests__/
│   │       └── useAutoExtraction.test.ts
│   └── __tests__/
│       ├── integration/
│       │   └── KnowledgeGraphWorkflow.test.tsx
│       └── performance/
│           └── GraphPerformance.test.ts
├── e2e/
│   └── knowledge-graph.spec.ts
├── jest.config.js
├── playwright.config.ts
└── setupTests.ts
```

---

## Running Tests

### All Tests

```bash
cd factory-frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Unit Tests Only

```bash
# Run unit tests
npm run test:unit

# Run specific test file
npm test -- GraphVisualization.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="renders loading"
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# Run with verbose output
npm run test:integration -- --verbose
```

### E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Run specific test
npm run test:e2e -- knowledge-graph.spec.ts

# Debug mode
npm run test:e2e -- --debug
```

### Performance Tests

```bash
# Run performance benchmarks
npm run test:performance

# With detailed output
npm run test:performance -- --verbose
```

---

## Unit Tests

### Component Tests

**Example: GraphVisualization.test.tsx**

Tests for the 3D graph visualization component:

- ✓ Renders loading state initially
- ✓ Fetches and displays graph data
- ✓ Handles fetch errors gracefully
- ✓ Filters entities by type
- ✓ Calls onEntityClick when entity is clicked

**Running:**
```bash
npm test -- GraphVisualization.test.tsx
```

### Hook Tests

**Example: useAutoExtraction.test.ts**

Tests for the auto-extraction hook:

- ✓ Triggers extraction when enabled
- ✓ Does not extract when disabled
- ✓ Handles extraction errors gracefully
- ✓ Uses correct extractor type and model
- ✓ Polls for job completion

**Running:**
```bash
npm test -- useAutoExtraction.test.ts
```

### Mocking Strategies

**Mocking fetch:**
```typescript
global.fetch = jest.fn();

beforeEach(() => {
  (global.fetch as jest.Mock).mockClear();
});

// Mock successful response
(global.fetch as jest.Mock).mockResolvedValueOnce({
  ok: true,
  json: async () => ({ data: 'test' }),
});

// Mock error
(global.fetch as jest.Mock).mockRejectedValueOnce(
  new Error('Network error')
);
```

**Mocking 3D graph library:**
```typescript
jest.mock('react-force-graph-3d', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-graph">Mock</div>,
}));
```

---

## Integration Tests

### Workflow Tests

**Example: KnowledgeGraphWorkflow.test.tsx**

Tests complete user workflows:

- ✓ Edit → Save → Extract → Display workflow
- ✓ Toggle auto-extraction on/off
- ✓ Display entity mention counts
- ✓ Handle extraction job status updates

**Running:**
```bash
npm run test:integration
```

### Testing Complex Interactions

```typescript
it('completes full workflow', async () => {
  // 1. Render component
  render(<SceneEditorWithKnowledgeGraph {...props} />);

  // 2. User interaction
  fireEvent.change(textarea, { target: { value: 'new content' } });
  fireEvent.click(saveButton);

  // 3. Wait for async updates
  await waitFor(() => {
    expect(mockOnSave).toHaveBeenCalled();
  });

  // 4. Verify state changes
  expect(screen.getByText(/saved/i)).toBeInTheDocument();
});
```

---

## E2E Tests

### Playwright Tests

**Example: knowledge-graph.spec.ts**

Full browser automation tests:

- ✓ View knowledge graph visualization
- ✓ Search and select entities
- ✓ Trigger extraction from scene editor
- ✓ Export graph to GraphML
- ✓ Browse entities with filters
- ✓ View entity details and relationships
- ✓ Use graph-powered search
- ✓ View analytics dashboard

**Running:**
```bash
npm run test:e2e
```

### Writing E2E Tests

```typescript
test('can view knowledge graph', async ({ page }) => {
  // Navigate
  await page.goto('/projects/123/knowledge-graph');

  // Wait for elements
  await expect(page.locator('.knowledge-graph')).toBeVisible();

  // Interact
  await page.click('button:has-text("Search")');

  // Verify
  await expect(page.locator('.search-results')).toBeVisible();
});
```

### E2E Best Practices

1. **Use data-testid for stable selectors**
2. **Wait for async operations with expect().toBeVisible()**
3. **Test user journeys, not implementation details**
4. **Clean up test data after each test**
5. **Use page object pattern for complex pages**

---

## Performance Tests

### Benchmark Tests

**Example: GraphPerformance.test.ts**

Performance benchmarks:

- ✓ Handles 1000 entities efficiently (<1s)
- ✓ Fast entity queries (<100ms)
- ✓ Efficient graph serialization (<500ms)
- ✓ Rapid entity additions (avg <50ms per batch)
- ✓ Reasonable memory usage (<10MB for 5000 nodes)

**Running:**
```bash
npm run test:performance
```

### Performance Metrics

Tests log performance metrics:

```
✓ Added 1000 entities in 234.56ms
✓ Queried entities in 12.34ms
✓ Serialized graph in 156.78ms
✓ JSON size: 523.45 KB
✓ Average batch time: 23.45ms
✓ Max batch time: 89.12ms
```

### Performance Thresholds

- Entity addition: < 1ms per entity
- Entity query: < 100ms for 1000 entities
- Graph serialization: < 500ms for 500 nodes
- Memory: < 10MB for 5000 nodes

---

## Writing New Tests

### Unit Test Template

```typescript
import { render, screen } from '@testing-library/react';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
  });

  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    render(<MyComponent />);
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => {
      expect(/* assertion */).toBeTruthy();
    });
  });
});
```

### Integration Test Template

```typescript
describe('Feature Workflow', () => {
  it('completes full user journey', async () => {
    // 1. Setup
    const mockFn = jest.fn();

    // 2. Render
    render(<FeatureComponent onAction={mockFn} />);

    // 3. User actions
    fireEvent.click(screen.getByRole('button'));

    // 4. Assertions
    await waitFor(() => {
      expect(mockFn).toHaveBeenCalled();
    });
  });
});
```

### E2E Test Template

```typescript
test('user can complete task', async ({ page }) => {
  // Navigate
  await page.goto('/feature');

  // Interact
  await page.fill('input[name="field"]', 'value');
  await page.click('button:has-text("Submit")');

  // Verify
  await expect(page.locator('.success-message')).toBeVisible();
});
```

---

## Best Practices

### General

1. **Write descriptive test names** - "should render loading state" not "test 1"
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **Test behavior, not implementation** - Focus on user interactions
4. **Keep tests independent** - No shared state between tests
5. **Mock external dependencies** - APIs, timers, random values

### Component Testing

1. **Query by accessibility roles** - `getByRole('button')`
2. **Avoid implementation details** - Don't test class names
3. **Test user journeys** - Not internal state
4. **Use userEvent for interactions** - More realistic than fireEvent
5. **Wait for async updates** - Use `waitFor` and `findBy`

### Integration Testing

1. **Test complete workflows** - Multiple components together
2. **Mock API responses** - Control test data
3. **Test error states** - Network failures, validation errors
4. **Verify side effects** - API calls, storage updates

### E2E Testing

1. **Test critical user paths** - Login → Create → Save → View
2. **Use stable selectors** - data-testid, ARIA labels
3. **Handle async operations** - Wait for elements, not arbitrary delays
4. **Test across browsers** - Chrome, Firefox, Safari
5. **Screenshot on failure** - Automatic in Playwright

### Performance Testing

1. **Set realistic thresholds** - Based on actual usage patterns
2. **Test edge cases** - Large datasets, slow networks
3. **Monitor trends** - Track performance over time
4. **Profile bottlenecks** - Use browser DevTools
5. **Optimize hot paths** - Focus on critical operations

---

## Coverage Reports

### Generate Coverage

```bash
npm run test:coverage
```

### View Coverage

```bash
# Open HTML report
open coverage/lcov-report/index.html
```

### Coverage Thresholds

Configured in `jest.config.js`:

- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - run: npm run test:e2e
```

---

## Debugging Tests

### Debug Unit Tests

```bash
# Run in debug mode
node --inspect-brk node_modules/.bin/jest --runInBand

# In VS Code, use Jest extension
```

### Debug E2E Tests

```bash
# Run in debug mode
npm run test:e2e -- --debug

# Use Playwright Inspector
PWDEBUG=1 npm run test:e2e
```

### Common Issues

**Tests timeout:**
- Increase timeout: `jest.setTimeout(10000)`
- Check for unresolved promises
- Verify mock implementations

**Flaky tests:**
- Remove arbitrary waits (setTimeout)
- Use waitFor for async operations
- Ensure proper cleanup between tests

**Mock not working:**
- Check mock is called before import
- Verify mock path is correct
- Clear mocks between tests

---

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Last Updated**: November 2024
**Test Coverage**: 70%+ required
