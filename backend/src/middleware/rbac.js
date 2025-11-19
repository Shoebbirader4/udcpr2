/**
 * RBAC Middleware - Role-Based Access Control
 */
const Role = require('../models/Role');

/**
 * Check if user has required permission
 */
const requirePermission = (permission) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({ 
          error: 'Authentication required',
          message: 'Please log in to access this resource'
        });
      }
      
      // Load user's role
      const role = await Role.findOne({ name: req.user.role });
      
      if (!role) {
        return res.status(403).json({ 
          error: 'Invalid role',
          message: 'User role is not configured properly'
        });
      }
      
      // Check permission
      if (!role.hasPermission(permission)) {
        return res.status(403).json({ 
          error: 'Insufficient permissions',
          message: `You need '${permission}' permission to perform this action`,
          required_permission: permission,
          user_role: role.display_name
        });
      }
      
      // Attach role to request
      req.userRole = role;
      
      next();
    } catch (error) {
      console.error('RBAC middleware error:', error);
      res.status(500).json({ 
        error: 'Internal server error',
        message: 'Failed to check permissions'
      });
    }
  };
};

/**
 * Check if user has any of the required permissions
 */
const requireAnyPermission = (permissions) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({ 
          error: 'Authentication required'
        });
      }
      
      const role = await Role.findOne({ name: req.user.role });
      
      if (!role) {
        return res.status(403).json({ 
          error: 'Invalid role'
        });
      }
      
      if (!role.hasAnyPermission(permissions)) {
        return res.status(403).json({ 
          error: 'Insufficient permissions',
          message: `You need one of these permissions: ${permissions.join(', ')}`,
          required_permissions: permissions,
          user_role: role.display_name
        });
      }
      
      req.userRole = role;
      next();
    } catch (error) {
      console.error('RBAC middleware error:', error);
      res.status(500).json({ 
        error: 'Internal server error'
      });
    }
  };
};

/**
 * Check if user has all required permissions
 */
const requireAllPermissions = (permissions) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({ 
          error: 'Authentication required'
        });
      }
      
      const role = await Role.findOne({ name: req.user.role });
      
      if (!role) {
        return res.status(403).json({ 
          error: 'Invalid role'
        });
      }
      
      if (!role.hasAllPermissions(permissions)) {
        return res.status(403).json({ 
          error: 'Insufficient permissions',
          message: `You need all of these permissions: ${permissions.join(', ')}`,
          required_permissions: permissions,
          user_role: role.display_name
        });
      }
      
      req.userRole = role;
      next();
    } catch (error) {
      console.error('RBAC middleware error:', error);
      res.status(500).json({ 
        error: 'Internal server error'
      });
    }
  };
};

/**
 * Check if user has required role
 */
const requireRole = (roleName) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        error: 'Authentication required'
      });
    }
    
    if (req.user.role !== roleName) {
      return res.status(403).json({ 
        error: 'Insufficient permissions',
        message: `This action requires '${roleName}' role`,
        required_role: roleName,
        user_role: req.user.role
      });
    }
    
    next();
  };
};

/**
 * Check if user has any of the required roles
 */
const requireAnyRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        error: 'Authentication required'
      });
    }
    
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ 
        error: 'Insufficient permissions',
        message: `This action requires one of these roles: ${roles.join(', ')}`,
        required_roles: roles,
        user_role: req.user.role
      });
    }
    
    next();
  };
};

module.exports = {
  requirePermission,
  requireAnyPermission,
  requireAllPermissions,
  requireRole,
  requireAnyRole
};
