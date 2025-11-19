const express = require('express');
const router = express.Router();
const { authenticate, requireAdmin } = require('../middleware/auth');
const mongoose = require('mongoose');

// Get parse jobs
router.get('/parse_jobs', authenticate, requireAdmin, async (req, res) => {
  try {
    const db = mongoose.connection.db;
    const jobs = await db.collection('parse_jobs')
      .find({})
      .sort({ created_at: -1 })
      .limit(50)
      .toArray();
    
    res.json(jobs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get candidate rules for verification
router.get('/candidates', authenticate, requireAdmin, async (req, res) => {
  try {
    // Read from staging_rules directory
    // This would be implemented based on file system access
    res.json({ message: 'Candidates endpoint - to be implemented' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Approve candidate rule
router.post('/approve_candidate', authenticate, requireAdmin, async (req, res) => {
  try {
    const { candidate_id, approved_data } = req.body;
    
    // Save to approved_rules and log audit trail
    const db = mongoose.connection.db;
    await db.collection('audit_logs').insertOne({
      action: 'approve_rule',
      candidate_id,
      reviewer_id: req.user.id,
      timestamp: new Date(),
      data: approved_data
    });
    
    res.json({ message: 'Candidate approved' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
