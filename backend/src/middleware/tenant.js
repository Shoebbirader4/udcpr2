/**
 * Tenant Middleware - Multi-tenant support
 */
const Tenant = require('../models/Tenant');

/**
 * Extract and validate tenant from request
 */
const tenantMiddleware = async (req, res, next) => {
  try {
    // Get tenant ID from various sources
    let tenantId = req.headers['x-tenant-id'] || 
                   req.query.tenant_id ||
                   req.user?.tenant_id;
    
    // Get tenant from subdomain if available
    if (!tenantId && req.subdomains && req.subdomains.length > 0) {
      const subdomain = req.subdomains[0];
      const tenant = await Tenant.findOne({ subdomain });
      if (tenant) {
        tenantId = tenant._id;
      }
    }
    
    if (!tenantId) {
      return res.status(400).json({ 
        error: 'Tenant not specified',
        message: 'Please provide tenant ID via header, query param, or subdomain'
      });
    }
    
    // Load tenant
    const tenant = await Tenant.findById(tenantId);
    
    if (!tenant) {
      return res.status(404).json({ 
        error: 'Tenant not found',
        message: 'The specified tenant does not exist'
      });
    }
    
    // Check tenant status
    if (tenant.status === 'suspended') {
      return res.status(403).json({ 
        error: 'Tenant suspended',
        message: 'This tenant account has been suspended. Please contact support.'
      });
    }
    
    if (tenant.status === 'cancelled') {
      return res.status(403).json({ 
        error: 'Tenant cancelled',
        message: 'This tenant account has been cancelled.'
      });
    }
    
    // Attach tenant to request
    req.tenant = tenant;
    req.tenantId = tenant._id;
    
    next();
  } catch (error) {
    console.error('Tenant middleware error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to process tenant information'
    });
  }
};

/**
 * Check if tenant has feature enabled
 */
const requireFeature = (feature) => {
  return (req, res, next) => {
    if (!req.tenant) {
      return res.status(400).json({ 
        error: 'Tenant not loaded',
        message: 'Tenant middleware must be used before requireFeature'
      });
    }
    
    if (!req.tenant.hasFeature(feature)) {
      return res.status(403).json({ 
        error: 'Feature not available',
        message: `The ${feature} feature is not available on your plan. Please upgrade.`
      });
    }
    
    next();
  };
};

/**
 * Check tenant usage limits
 */
const checkUsageLimit = (resource) => {
  return async (req, res, next) => {
    if (!req.tenant) {
      return res.status(400).json({ 
        error: 'Tenant not loaded'
      });
    }
    
    let canAdd = false;
    let limitMessage = '';
    
    switch (resource) {
      case 'user':
        canAdd = req.tenant.canAddUser();
        limitMessage = `User limit reached (${req.tenant.settings.max_users}). Please upgrade your plan.`;
        break;
      
      case 'project':
        canAdd = req.tenant.canAddProject();
        limitMessage = `Project limit reached (${req.tenant.settings.max_projects}). Please upgrade your plan.`;
        break;
      
      default:
        canAdd = true;
    }
    
    if (!canAdd) {
      return res.status(403).json({ 
        error: 'Usage limit reached',
        message: limitMessage
      });
    }
    
    next();
  };
};

module.exports = {
  tenantMiddleware,
  requireFeature,
  checkUsageLimit
};
