/**
 * Audit Log Model - Track all system actions
 */
const mongoose = require('mongoose');

const auditLogSchema = new mongoose.Schema({
  timestamp: {
    type: Date,
    default: Date.now,
    required: true,
    index: true
  },
  tenant_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Tenant',
    required: true,
    index: true
  },
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  action: {
    type: String,
    required: true,
    index: true,
    enum: [
      // Authentication
      'auth.login',
      'auth.logout',
      'auth.failed_login',
      
      // Projects
      'project.create',
      'project.read',
      'project.update',
      'project.delete',
      'project.submit',
      'project.approve',
      'project.reject',
      
      // Rules
      'rule.create',
      'rule.update',
      'rule.delete',
      
      // Users
      'user.create',
      'user.update',
      'user.delete',
      'user.role_change',
      
      // System
      'system.config_change',
      'system.backup',
      'system.restore'
    ]
  },
  resource_type: {
    type: String,
    enum: ['project', 'user', 'rule', 'tenant', 'system']
  },
  resource_id: {
    type: String,
    index: true
  },
  result: {
    type: String,
    enum: ['success', 'failure', 'error'],
    required: true
  },
  ip_address: String,
  user_agent: String,
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  error_message: String
});

// Compound indexes for common queries
auditLogSchema.index({ tenant_id: 1, timestamp: -1 });
auditLogSchema.index({ user_id: 1, timestamp: -1 });
auditLogSchema.index({ action: 1, timestamp: -1 });
auditLogSchema.index({ resource_type: 1, resource_id: 1, timestamp: -1 });

// TTL index - automatically delete logs older than 90 days
auditLogSchema.index({ timestamp: 1 }, { expireAfterSeconds: 7776000 }); // 90 days

module.exports = mongoose.model('AuditLog', auditLogSchema);
