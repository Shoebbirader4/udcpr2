const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.ADMIN_PORT || 3002;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const STAGING_DIR = path.join(__dirname, '..', 'udcpr_master_data', 'staging_rules');
const APPROVED_DIR = path.join(__dirname, '..', 'udcpr_master_data', 'approved_rules');
const IMAGES_DIR = path.join(__dirname, '..', 'udcpr_master_data', 'images');
const TEXT_DIR = path.join(__dirname, '..', 'udcpr_master_data', 'raw_text');

// MongoDB connection
if (process.env.MONGO_URI) {
  mongoose.connect(process.env.MONGO_URI)
    .then(() => console.log('✓ Admin UI connected to MongoDB'))
    .catch(err => console.error('MongoDB connection error:', err));
}

// Get statistics
app.get('/api/stats', async (req, res) => {
  try {
    const stagingFiles = await fs.readdir(STAGING_DIR).catch(() => []);
    const approvedFiles = await fs.readdir(APPROVED_DIR).catch(() => []);
    
    let totalCandidates = 0;
    for (const file of stagingFiles.filter(f => f.endsWith('.json'))) {
      const content = await fs.readFile(path.join(STAGING_DIR, file), 'utf-8');
      const data = JSON.parse(content);
      totalCandidates += Array.isArray(data) ? data.length : 1;
    }
    
    res.json({
      stagingFiles: stagingFiles.filter(f => f.endsWith('.json')).length,
      approvedFiles: approvedFiles.filter(f => f.endsWith('.json')).length,
      totalCandidates
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get list of candidate files with metadata
app.get('/api/candidates', async (req, res) => {
  try {
    await fs.mkdir(STAGING_DIR, { recursive: true });
    const files = await fs.readdir(STAGING_DIR);
    const jsonFiles = files.filter(f => f.endsWith('.json'));
    
    const filesWithMeta = await Promise.all(jsonFiles.map(async (file) => {
      const filePath = path.join(STAGING_DIR, file);
      const stats = await fs.stat(filePath);
      const content = await fs.readFile(filePath, 'utf-8');
      const data = JSON.parse(content);
      const count = Array.isArray(data) ? data.length : 1;
      
      return {
        filename: file,
        size: stats.size,
        modified: stats.mtime,
        candidateCount: count
      };
    }));
    
    res.json({ files: filesWithMeta });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get candidates from a file with pagination
app.get('/api/candidates/:filename', async (req, res) => {
  try {
    const { page = 1, limit = 10 } = req.query;
    const filePath = path.join(STAGING_DIR, req.params.filename);
    const content = await fs.readFile(filePath, 'utf-8');
    let candidates = JSON.parse(content);
    
    if (!Array.isArray(candidates)) {
      candidates = [candidates];
    }
    
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + parseInt(limit);
    const paginatedCandidates = candidates.slice(startIndex, endIndex);
    
    res.json({
      candidates: paginatedCandidates,
      total: candidates.length,
      page: parseInt(page),
      totalPages: Math.ceil(candidates.length / limit)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get page image for a candidate
app.get('/api/images/:pdfName/:pageNum', async (req, res) => {
  try {
    const { pdfName, pageNum } = req.params;
    const imagePath = path.join(IMAGES_DIR, pdfName, `page_${pageNum.padStart(4, '0')}.png`);
    
    const exists = await fs.access(imagePath).then(() => true).catch(() => false);
    if (!exists) {
      return res.status(404).json({ error: 'Image not found' });
    }
    
    res.sendFile(imagePath);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Approve a candidate
app.post('/api/approve', async (req, res) => {
  try {
    const { rule, filename, index } = req.body;
    
    // Add approval metadata
    rule.approved_at = new Date().toISOString();
    rule.approved_by = 'admin';
    rule.source_file = filename;
    rule.source_index = index;
    
    // Generate unique rule_id if not present
    if (!rule.rule_id) {
      const timestamp = Date.now();
      const jurisdiction = rule.jurisdiction || 'unknown';
      rule.rule_id = `${jurisdiction}_${timestamp}_${index}`;
    }
    
    // Save to approved directory
    const approvedFilename = `approved_${rule.rule_id}.json`;
    const filePath = path.join(APPROVED_DIR, approvedFilename);
    
    await fs.mkdir(APPROVED_DIR, { recursive: true });
    await fs.writeFile(filePath, JSON.stringify(rule, null, 2));
    
    // Log to audit
    if (mongoose.connection.readyState === 1) {
      await mongoose.connection.db.collection('audit_logs').insertOne({
        action: 'approve_rule',
        rule_id: rule.rule_id,
        approved_by: 'admin',
        timestamp: new Date(),
        source_file: filename
      });
    }
    
    res.json({ message: 'Rule approved', filename: approvedFilename, rule_id: rule.rule_id });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Reject a candidate
app.post('/api/reject', async (req, res) => {
  try {
    const { rule, filename, index, reason } = req.body;
    
    // Log rejection
    if (mongoose.connection.readyState === 1) {
      await mongoose.connection.db.collection('audit_logs').insertOne({
        action: 'reject_rule',
        rule_id: rule.rule_id || 'unknown',
        rejected_by: 'admin',
        reason: reason || 'No reason provided',
        timestamp: new Date(),
        source_file: filename
      });
    }
    
    res.json({ message: 'Rule rejected' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update/edit a candidate
app.post('/api/update', async (req, res) => {
  try {
    const { rule, filename, index } = req.body;
    
    // Read the original file
    const filePath = path.join(STAGING_DIR, filename);
    const content = await fs.readFile(filePath, 'utf-8');
    let candidates = JSON.parse(content);
    
    if (!Array.isArray(candidates)) {
      candidates = [candidates];
    }
    
    // Update the specific candidate
    if (index >= 0 && index < candidates.length) {
      candidates[index] = rule;
      
      // Write back
      await fs.writeFile(filePath, JSON.stringify(candidates, null, 2));
      
      res.json({ message: 'Rule updated successfully' });
    } else {
      res.status(400).json({ error: 'Invalid index' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Serve the React admin UI
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`✓ Admin UI running on http://localhost:${PORT}`);
  console.log(`  Access at: http://localhost:${PORT}`);
});
