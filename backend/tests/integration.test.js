/**
 * Integration tests for UDCPR Master Backend
 * Phase 2 - Backend Integration Tests
 */
const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../src/server');

describe('UDCPR Master Backend Integration Tests', () => {
  let authToken;
  let testProjectId;
  
  beforeAll(async () => {
    // Connect to test database
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/udcpr_test');
    }
  });
  
  afterAll(async () => {
    // Cleanup
    if (testProjectId) {
      await mongoose.connection.db.collection('projects').deleteOne({ _id: new mongoose.Types.ObjectId(testProjectId) });
    }
    await mongoose.connection.db.collection('users').deleteOne({ email: 'test@integration.com' });
    await mongoose.connection.close();
  });
  
  describe('Authentication', () => {
    it('should register a new user', async () => {
      const res = await request(app)
        .post('/api/auth/signup')
        .send({
          email: 'test@integration.com',
          password: 'testpass123',
          name: 'Integration Test User'
        });
      
      expect(res.status).toBe(201);
      expect(res.body).toHaveProperty('token');
      expect(res.body.user.email).toBe('test@integration.com');
      authToken = res.body.token;
    });
    
    it('should login with correct credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@integration.com',
          password: 'testpass123'
        });
      
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('token');
    });
    
    it('should reject login with wrong password', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@integration.com',
          password: 'wrongpassword'
        });
      
      expect(res.status).toBe(401);
    });
  });
  
  describe('Projects', () => {
    it('should create a new project', async () => {
      const res = await request(app)
        .post('/api/projects')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          name: 'Test Residential Project',
          jurisdiction: 'maharashtra_udcpr',
          zone: 'Residential',
          plotDetails: {
            area_sqm: 500,
            road_width_m: 12,
            corner_plot: false,
            frontage_m: 20
          },
          buildingDetails: {
            use_type: 'Residential',
            proposed_floors: 4,
            proposed_height_m: 12,
            proposed_built_up_sqm: 500
          },
          specialConditions: {
            tod_zone: false,
            redevelopment: false,
            slum_rehab: false
          }
        });
      
      expect(res.status).toBe(201);
      expect(res.body.name).toBe('Test Residential Project');
      expect(res.body.status).toBe('draft');
      testProjectId = res.body._id;
    });
    
    it('should get all projects for user', async () => {
      const res = await request(app)
        .get('/api/projects')
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.status).toBe(200);
      expect(Array.isArray(res.body)).toBe(true);
      expect(res.body.length).toBeGreaterThan(0);
    });
    
    it('should get a single project', async () => {
      const res = await request(app)
        .get(`/api/projects/${testProjectId}`)
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.status).toBe(200);
      expect(res.body._id).toBe(testProjectId);
    });
    
    it('should evaluate a project', async () => {
      const res = await request(app)
        .post(`/api/projects/${testProjectId}/evaluate`)
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.status).toBe(200);
      expect(res.body.evaluationResult).toBeDefined();
      expect(res.body.evaluationResult.fsi_result).toBeDefined();
      expect(res.body.evaluationResult.setback_result).toBeDefined();
      expect(res.body.evaluationResult.parking_result).toBeDefined();
      expect(res.body.evaluationResult.height_result).toBeDefined();
      expect(res.body.status).toBe('evaluated');
    });
    
    it('should update a project', async () => {
      const res = await request(app)
        .put(`/api/projects/${testProjectId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          name: 'Updated Test Project'
        });
      
      expect(res.status).toBe(200);
      expect(res.body.name).toBe('Updated Test Project');
    });
  });
  
  describe('Rules', () => {
    it('should get rules info', async () => {
      const res = await request(app)
        .get('/api/rules');
      
      expect(res.status).toBe(200);
    });
  });
  
  describe('Health Check', () => {
    it('should return health status', async () => {
      const res = await request(app)
        .get('/health');
      
      expect(res.status).toBe(200);
      expect(res.body.status).toBe('ok');
    });
  });
});
