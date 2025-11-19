const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

// Get rule by ID
router.get('/:id', async (req, res) => {
  try {
    const db = mongoose.connection.db;
    const rule = await db.collection('rules').findOne({ rule_id: req.params.id });
    
    if (!rule) {
      return res.status(404).json({ error: 'Rule not found' });
    }
    
    res.json(rule);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Query rules with search and filtering
router.get('/', async (req, res) => {
  try {
    const { jurisdiction, clause_number, search, category } = req.query;
    const db = mongoose.connection.db;
    
    // Check if rules collection exists and has data
    const collections = await db.listCollections({ name: 'rules' }).toArray();
    if (collections.length === 0) {
      // No rules collection, return mock data from approved_rules files
      const fs = require('fs').promises;
      const path = require('path');
      const approvedDir = path.join(__dirname, '..', '..', '..', 'udcpr_master_data', 'approved_rules');
      
      try {
        const files = await fs.readdir(approvedDir);
        const jsonFiles = files.filter(f => f.endsWith('.json'));
        
        let allRules = [];
        for (const file of jsonFiles) {
          const content = await fs.readFile(path.join(approvedDir, file), 'utf-8');
          const rule = JSON.parse(content);
          allRules.push(rule);
        }
        
        // Apply filters
        let filteredRules = allRules;
        
        if (jurisdiction) {
          filteredRules = filteredRules.filter(r => r.jurisdiction === jurisdiction);
        }
        
        if (clause_number) {
          filteredRules = filteredRules.filter(r => r.clause_number === clause_number);
        }
        
        if (search) {
          const searchLower = search.toLowerCase();
          filteredRules = filteredRules.filter(r => 
            r.title?.toLowerCase().includes(searchLower) ||
            r.clause_text?.toLowerCase().includes(searchLower) ||
            r.clause_number?.toLowerCase().includes(searchLower) ||
            r.rule_id?.toLowerCase().includes(searchLower)
          );
        }
        
        return res.json(filteredRules.slice(0, 100));
      } catch (err) {
        // If no approved rules, return empty array
        return res.json([]);
      }
    }
    
    // Build MongoDB query
    const query = {};
    if (jurisdiction) query.jurisdiction = jurisdiction;
    if (clause_number) query.clause_number = clause_number;
    
    if (search) {
      // Use regex for flexible search
      query.$or = [
        { title: { $regex: search, $options: 'i' } },
        { clause_text: { $regex: search, $options: 'i' } },
        { clause_number: { $regex: search, $options: 'i' } },
        { rule_id: { $regex: search, $options: 'i' } }
      ];
    }
    
    const rules = await db.collection('rules')
      .find(query)
      .limit(100)
      .toArray();
    
    res.json(rules);
  } catch (error) {
    console.error('Error fetching rules:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get rule versions
router.get('/versions/list', async (req, res) => {
  try {
    const db = mongoose.connection.db;
    const versions = await db.collection('rule_versions')
      .find({})
      .sort({ created_at: -1 })
      .toArray();
    
    res.json(versions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
