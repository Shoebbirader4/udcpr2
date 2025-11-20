const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const Project = require('../models/Project');
const notificationService = require('../services/notification');
const auditService = require('../services/audit');

// Simple role check middleware
const requireMunicipal = (req, res, next) => {
  if (!req.user || (req.user.role !== 'municipal_officer' && req.user.role !== 'admin' && req.user.role !== 'super_admin')) {
    return res.status(403).json({ error: 'Municipal officer access required' });
  }
  next();
};

// Get projects for review (municipal officers only)
router.get('/projects', authenticate, requireMunicipal, async (req, res) => {
  try {
    const { status = 'pending' } = req.query;
    
    const query = status === 'all' ? {} : { approvalStatus: status };
    
    const projects = await Project.find(query)
      .populate('user', 'name email')
      .sort({ createdAt: -1 });
    
    res.json(projects);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Approve project
router.post('/projects/:id/approve', authenticate, requireMunicipal, async (req, res) => {
  try {
    const { comments } = req.body;
    
    const project = await Project.findByIdAndUpdate(
      req.params.id,
      {
        approvalStatus: 'approved',
        approvalComments: comments,
        approvedBy: req.user.userId,
        approvedAt: new Date()
      },
      { new: true }
    ).populate('user', 'name email');
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    // Send notification to project owner
    await notificationService.notifyProjectApproval(
      project.user._id,
      project.name,
      project.tenant
    );
    
    // Log audit
    await auditService.log({
      userId: req.user.userId,
      tenantId: project.tenant,
      action: 'project.approved',
      category: 'projects',
      details: {
        projectId: project._id,
        projectName: project.name,
        comments
      },
      ipAddress: req.ip
    });
    
    res.json(project);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Reject project
router.post('/projects/:id/reject', authenticate, requireMunicipal, async (req, res) => {
  try {
    const { comments } = req.body;
    
    if (!comments) {
      return res.status(400).json({ error: 'Comments are required for rejection' });
    }
    
    const project = await Project.findByIdAndUpdate(
      req.params.id,
      {
        approvalStatus: 'rejected',
        approvalComments: comments,
        approvedBy: req.user.userId,
        approvedAt: new Date()
      },
      { new: true }
    ).populate('user', 'name email');
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    // Send notification to project owner
    await notificationService.notifyProjectRejection(
      project.user._id,
      project.name,
      comments,
      project.tenant
    );
    
    // Log audit
    await auditService.log({
      userId: req.user.userId,
      tenantId: project.tenant,
      action: 'project.rejected',
      category: 'projects',
      details: {
        projectId: project._id,
        projectName: project.name,
        comments
      },
      ipAddress: req.ip
    });
    
    res.json(project);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get approval statistics
router.get('/stats', authenticate, requireMunicipal, async (req, res) => {
  try {
    const [pending, approved, rejected, total] = await Promise.all([
      Project.countDocuments({ approvalStatus: 'pending' }),
      Project.countDocuments({ approvalStatus: 'approved' }),
      Project.countDocuments({ approvalStatus: 'rejected' }),
      Project.countDocuments()
    ]);
    
    res.json({
      pending,
      approved,
      rejected,
      total,
      approvalRate: total > 0 ? ((approved / total) * 100).toFixed(1) : 0
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
