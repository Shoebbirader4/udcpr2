/**
 * Role Model - RBAC support
 */
const mongoose = require('mongoose');

const roleSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    enum: ['super_admin', 'municipal_officer', 'architect', 'developer', 'auditor'],
    unique: true
  },
  display_name: {
    type: String,
    required: true
  },
  description: String,
  permissions: [{
    type: String,
    enum: [
      // Project permissions
      'projects.create',
      'projects.read',
      'projects.update',
      'projects.delete',
      'projects.approve',
      'projects.submit',
      
      // Rule permissions
      'rules.read',
      'rules.manage',
      
      // User permissions
      'users.read',
      'users.create',
      'users.update',
      'users.delete',
      'users.manage_roles',
      
      // Report permissions
      'reports.generate',
      'reports.download',
      
      // Audit permissions
      'audit.read',
      
      // System permissions
      'system.configure',
      'system.monitor'
    ]
  }],
  level: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  created_at: {
    type: Date,
    default: Date.now
  }
});

// Check if role has permission
roleSchema.methods.hasPermission = function(permission) {
  return this.permissions.includes(permission);
};

// Check if role has any of the permissions
roleSchema.methods.hasAnyPermission = function(permissions) {
  return permissions.some(p => this.permissions.includes(p));
};

// Check if role has all permissions
roleSchema.methods.hasAllPermissions = function(permissions) {
  return permissions.every(p => this.permissions.includes(p));
};

module.exports = mongoose.model('Role', roleSchema);
