const express = require('express');
const router = express.Router();
const Project = require('../models/Project');
const { authenticate } = require('../middleware/auth');
const axios = require('axios');

// Get all projects for user
router.get('/', authenticate, async (req, res) => {
  try {
    const projects = await Project.find({ userId: req.user.id })
      .sort({ updatedAt: -1 });
    res.json(projects);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get single project
router.get('/:id', authenticate, async (req, res) => {
  try {
    const project = await Project.findOne({
      _id: req.params.id,
      userId: req.user.id
    });
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    res.json(project);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create project
router.post('/', authenticate, async (req, res) => {
  try {
    const project = new Project({
      ...req.body,
      userId: req.user.id
    });
    
    await project.save();
    res.status(201).json(project);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Evaluate project (call Python rule engine)
router.post('/:id/evaluate', authenticate, async (req, res) => {
  try {
    const project = await Project.findOne({
      _id: req.params.id,
      userId: req.user.id
    });
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    // Call Python rule engine API
    const ruleEngineUrl = process.env.RULE_ENGINE_URL || 'http://localhost:5000';
    
    const evaluationInput = {
      jurisdiction: project.jurisdiction,
      zone: project.zone,
      plot_area_sqm: project.plotDetails.area_sqm,
      road_width_m: project.plotDetails.road_width_m,
      corner_plot: project.plotDetails.corner_plot,
      frontage_m: project.plotDetails.frontage_m,
      use_type: project.buildingDetails.use_type,
      proposed_floors: project.buildingDetails.proposed_floors,
      proposed_height_m: project.buildingDetails.proposed_height_m,
      proposed_built_up_sqm: project.buildingDetails.proposed_built_up_sqm,
      tod_zone: project.specialConditions?.tod_zone || false,
      redevelopment: project.specialConditions?.redevelopment || false,
      slum_rehab: project.specialConditions?.slum_rehab || false
    };
    
    let evaluationResult;
    
    try {
      // Try to call the Python rule engine API
      const response = await axios.post(`${ruleEngineUrl}/evaluate`, evaluationInput);
      evaluationResult = response.data;
    } catch (error) {
      console.warn('Rule engine API not available, using fallback calculation:', error.message);
      
      // Fallback to simple calculation if API is not available
      const proposed_fsi = evaluationInput.proposed_built_up_sqm / evaluationInput.plot_area_sqm;
      evaluationResult = {
        rule_version: 'fallback_v1',
        evaluated_at: new Date().toISOString(),
        fsi_result: {
          base_fsi: 1.0,
          bonus_fsi: 0,
          permissible_fsi: 1.0,
          proposed_fsi: proposed_fsi,
          fsi_utilization_percent: proposed_fsi * 100
        },
        setback_result: {
          front_m: 4.5,
          side_m: 3.0,
          rear_m: 3.0
        },
        parking_result: {
          required_ecs: Math.ceil(evaluationInput.proposed_built_up_sqm / 100),
          area_per_ecs_sqm: 25
        },
        height_result: {
          permissible_height_m: 45,
          proposed_height_m: evaluationInput.proposed_height_m
        },
        tdr_result: null,
        compliant: proposed_fsi <= 1.0,
        violations: proposed_fsi > 1.0 ? ['FSI exceeds limit (fallback calculation)'] : [],
        warnings: ['Using fallback calculation - start rule engine API for accurate results'],
        calculation_traces: []
      };
    }
    
    project.evaluationResult = evaluationResult;
    project.status = 'evaluated';
    await project.save();
    
    res.json(project);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update project
router.put('/:id', authenticate, async (req, res) => {
  try {
    const project = await Project.findOneAndUpdate(
      { _id: req.params.id, userId: req.user.id },
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    res.json(project);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Export project as PDF
router.get('/:id/export/pdf', authenticate, async (req, res) => {
  try {
    const project = await Project.findOne({
      _id: req.params.id,
      userId: req.user.id
    });
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    if (!project.evaluationResult) {
      return res.status(400).json({ error: 'Project not evaluated yet' });
    }
    
    const pdfReport = require('../services/pdfReport');
    const doc = pdfReport.generateComplianceReport(project, project.evaluationResult);
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${project.name}-compliance-report.pdf"`);
    
    doc.pipe(res);
    doc.end();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete project
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const project = await Project.findOneAndDelete({
      _id: req.params.id,
      userId: req.user.id
    });
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    res.json({ message: 'Project deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
