const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const { requireRole } = require('../middleware/rbac');
const User = require('../models/User');
const Tenant = require('../models/Tenant');
const AuditLog = require('../models/AuditLog');

// Get all users (super admin only)
router.get('/users', auth, requireRole('super_admin'), async (req, res) => {
  try {
    const users = await User.find()
      .select('-password')
      .populate('tenant', 'name')
      .sort({ createdAt: -1 });
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all tenants
router.get('/tenants', auth, requireRole('super_admin'), async (req, res) => {
  try {
    const tenants = await Tenant.find().sort({ createdAt: -1 });
    res.json(tenants);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create tenant
router.post('/tenants', auth, requireRole('super_admin'), async (req, res) => {
  try {
    const tenant = await Tenant.create(req.body);
    res.status(201).json(tenant);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update tenant
router.patch('/tenants/:id', auth, requireRole('super_admin'), async (req, res) => {
  try {
    const tenant = await Tenant.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    if (!tenant) {
      return res.status(404).json({ error: 'Tenant not found' });
    }
    res.json(tenant);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get audit logs
router.get('/audit-logs', auth, requireRole('super_admin'), async (req, res) => {
  try {
    const { limit = 100, category, userId } = req.query;
    
    const query = {};
    if (category) query.category = category;
    if (userId) query.user = userId;
    
    const logs = await AuditLog.find(query)
      .populate('user', 'name email')
      .sort({ timestamp: -1 })
      .limit(parseInt(limit));
    
    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get system statistics
router.get('/stats', auth, requireRole('super_admin'), async (req, res) => {
  try {
    const [userCount, tenantCount, activeUsers] = await Promise.all([
      User.countDocuments(),
      Tenant.countDocuments(),
      User.countDocuments({ lastLogin: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } })
    ]);
    
    res.json({
      users: userCount,
      tenants: tenantCount,
      activeUsers,
      timestamp: new Date()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
