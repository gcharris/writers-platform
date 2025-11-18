/**
 * Knowledge Graph Performance Benchmarks
 * Tests performance characteristics of graph operations
 */

import { performance } from 'perf_hooks';

// Mock graph service (would use actual service in real tests)
class MockGraphService {
  private nodes: Map<string, any> = new Map();
  private edges: Map<string, any> = new Map();

  addEntity(entity: any) {
    this.nodes.set(entity.id, entity);
  }

  addRelationship(relationship: any) {
    const key = `${relationship.source}-${relationship.target}`;
    this.edges.set(key, relationship);
  }

  queryEntities(filter: any): any[] {
    const results: any[] = [];
    for (const [id, entity] of this.nodes.entries()) {
      if (!filter.type || entity.type === filter.type) {
        results.push(entity);
      }
    }
    return results;
  }

  toJSON(): string {
    return JSON.stringify({
      nodes: Array.from(this.nodes.values()),
      edges: Array.from(this.edges.values()),
    });
  }

  getEntityCount(): number {
    return this.nodes.size;
  }

  getRelationshipCount(): number {
    return this.edges.size;
  }
}

describe('Graph Performance Benchmarks', () => {
  it('handles 1000 entities efficiently', () => {
    const service = new MockGraphService();

    const start = performance.now();

    // Add 1000 entities
    for (let i = 0; i < 1000; i++) {
      service.addEntity({
        id: `entity-${i}`,
        name: `Entity ${i}`,
        type: 'character',
        mentions: Math.floor(Math.random() * 10),
        confidence: Math.random(),
      });
    }

    const addTime = performance.now() - start;
    console.log(`✓ Added 1000 entities in ${addTime.toFixed(2)}ms`);

    expect(addTime).toBeLessThan(1000); // Should take less than 1 second
    expect(service.getEntityCount()).toBe(1000);
  });

  it('performs fast entity queries', () => {
    const service = new MockGraphService();

    // Add entities
    for (let i = 0; i < 100; i++) {
      service.addEntity({
        id: `entity-${i}`,
        name: `Entity ${i}`,
        type: i % 2 === 0 ? 'character' : 'location',
        mentions: 1,
        confidence: 0.9,
      });
    }

    const start = performance.now();
    const characters = service.queryEntities({ type: 'character' });
    const queryTime = performance.now() - start;

    console.log(`✓ Queried entities in ${queryTime.toFixed(2)}ms`);

    expect(characters.length).toBe(50);
    expect(queryTime).toBeLessThan(100); // Should be very fast
  });

  it('serializes large graphs efficiently', () => {
    const service = new MockGraphService();

    // Add 500 entities and 1000 relationships
    for (let i = 0; i < 500; i++) {
      service.addEntity({
        id: `entity-${i}`,
        name: `Entity ${i}`,
        type: 'character',
        mentions: 1,
        confidence: 0.9,
      });
    }

    for (let i = 0; i < 1000; i++) {
      service.addRelationship({
        source: `entity-${i % 500}`,
        target: `entity-${(i + 1) % 500}`,
        relation: 'knows',
        strength: Math.random(),
      });
    }

    const start = performance.now();
    const json = service.toJSON();
    const serializeTime = performance.now() - start;

    console.log(`✓ Serialized graph in ${serializeTime.toFixed(2)}ms`);
    console.log(`✓ JSON size: ${(json.length / 1024).toFixed(2)} KB`);

    expect(serializeTime).toBeLessThan(500); // Should serialize quickly
    expect(service.getEntityCount()).toBe(500);
    expect(service.getRelationshipCount()).toBe(1000);
  });

  it('handles rapid entity additions', () => {
    const service = new MockGraphService();

    const iterations = 100;
    const batchSize = 10;
    const times: number[] = [];

    for (let batch = 0; batch < iterations; batch++) {
      const start = performance.now();

      for (let i = 0; i < batchSize; i++) {
        service.addEntity({
          id: `entity-${batch * batchSize + i}`,
          name: `Entity ${batch * batchSize + i}`,
          type: 'character',
          mentions: 1,
          confidence: 0.9,
        });
      }

      times.push(performance.now() - start);
    }

    const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
    const maxTime = Math.max(...times);

    console.log(`✓ Average batch time: ${avgTime.toFixed(2)}ms`);
    console.log(`✓ Max batch time: ${maxTime.toFixed(2)}ms`);

    expect(avgTime).toBeLessThan(50); // Average should be fast
    expect(maxTime).toBeLessThan(200); // Even worst case should be reasonable
  });

  it('memory usage stays reasonable with large graphs', () => {
    const service = new MockGraphService();

    // Add 5000 entities with various relationships
    for (let i = 0; i < 5000; i++) {
      service.addEntity({
        id: `entity-${i}`,
        name: `Entity ${i}`,
        type: ['character', 'location', 'object', 'concept'][i % 4],
        mentions: Math.floor(Math.random() * 20),
        confidence: Math.random(),
        description: `Description for entity ${i}`,
      });
    }

    // Add 10000 relationships
    for (let i = 0; i < 10000; i++) {
      service.addRelationship({
        source: `entity-${i % 5000}`,
        target: `entity-${(i + 1) % 5000}`,
        relation: ['knows', 'located_in', 'owns'][i % 3],
        strength: Math.random(),
      });
    }

    const json = service.toJSON();
    const sizeKB = json.length / 1024;

    console.log(`✓ Large graph size: ${sizeKB.toFixed(2)} KB`);
    console.log(`✓ Entities: ${service.getEntityCount()}`);
    console.log(`✓ Relationships: ${service.getRelationshipCount()}`);

    // Size should be reasonable (< 10MB for 5000 nodes)
    expect(sizeKB).toBeLessThan(10 * 1024);
  });
});
