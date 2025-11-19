/**
 * Tenant Model - Multi-tenant support
 */
const mongoose = require('mongoose');

const tenantSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  subdomain: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  status: {
    type: String,
    enum: ['active', 'suspended', 'trial', 'cancelled'],
    default: 'trial'
  },
  plan: {
    type: String,
    enum: ['free', 'basic', 'professional', 'enterprise'],
    default: 'free'
  },
  settings: {
    max_users: { type: Number, default: 5 },
    max_projects: { type: Number, default: 10 },
    max_storage_mb: { type: Number, default: 1000 },
    features: {
      ai_assistant: { type: Boolean, default: false },
      vision_pipeline: { type: Boolean, default: false },
      municipal_portal: { type: Boolean, default: false },
      api_access: { type: Boolean, default: false }
    }
  },
  contact: {
    name: String,
    email: String,
    phone: String
  },
  billing: {
    customer_id: String,
    subscription_id: String,
    current_period_start: Date,
    current_period_end: Date
  },
  usage: {
    users_count: { type: Number, default: 0 },
    projects_count: { type: Number, default: 0 },
    storage_used_mb: { type: Number, default: 0 },
    api_calls_month: { type: Number, default: 0 }
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
});

// Update timestamp on save
tenantSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

// Check if tenant can create more users
tenantSchema.methods.canAddUser = function() {
  return this.usage.users_count < this.settings.max_users;
};

// Check if tenant can create more projects
tenantSchema.methods.canAddProject = function() {
  return this.usage.projects_count < this.settings.max_projects;
};

// Check if feature is enabled
tenantSchema.methods.hasFeature = function(feature) {
  return this.settings.features[feature] === true;
};

module.exports = mongoose.model('Tenant', tenantSchema);
