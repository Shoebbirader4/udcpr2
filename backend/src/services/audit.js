/**
 * Audit Service - Track all system actions
 */
const AuditLog = require('../models/AuditLog');

class AuditService {
  /**
   * Log an action
   */
  async log(event) {
    try {
      const auditLog = await AuditLog.create({
        timestamp: new Date(),
        tenant_id: event.tenant_id,
        user_id: event.user_id,
        action: event.action,
        resource_type: event.resource_type,
        resource_id: event.resource_id,
        result: event.result || 'success',
        ip_address: event.ip_address,
        user_agent: event.user_agent,
        metadata: event.metadata || {},
        error_message: event.error_message
      });
      
      return auditLog;
    } catch (error) {
      console.error('Failed to create audit log:', error);
      // Don't throw - audit logging should not break the main flow
    }
  }
  
  /**
   * Log from Express request
   */
  async logFromRequest(req, action, result, metadata = {}) {
    return this.log({
      tenant_id: req.tenantId || req.user?.tenant_id,
      user_id: req.user?._id,
      action,
      result,
      ip_address: req.ip || req.connection.remoteAddress,
      user_agent: req.get('user-agent'),
      metadata
    });
  }
  
  /**
   * Log authentication event
   */
  async logAuth(req, action, result, userId = null) {
    return this.log({
      tenant_id: req.tenantId,
      user_id: userId || req.user?._id,
      action,
      result,
      ip_address: req.ip,
      user_agent: req.get('user-agent'),
      metadata: {
        email: req.body?.email
      }
    });
  }
  
  /**
   * Log project action
   */
  async logProject(req, action, projectId, result = 'success', metadata = {}) {
    return this.log({
      tenant_id: req.tenantId,
      user_id: req.user._id,
      action,
      resource_type: 'project',
      resource_id: projectId,
      result,
      ip_address: req.ip,
      user_agent: req.get('user-agent'),
      metadata
    });
  }
  
  /**
   * Log user action
   */
  async logUser(req, action, targetUserId, result = 'success', metadata = {}) {
    return this.log({
      tenant_id: req.tenantId,
      user_id: req.user._id,
      action,
      resource_type: 'user',
      resource_id: targetUserId,
      result,
      ip_address: req.ip,
      user_agent: req.get('user-agent'),
      metadata
    });
  }
  
  /**
   * Get audit trail for a resource
   */
  async getAuditTrail(filters = {}, options = {}) {
    const {
      tenant_id,
      user_id,
      action,
      resource_type,
      resource_id,
      start_date,
      end_date
    } = filters;
    
    const {
      limit = 100,
      skip = 0,
      sort = { timestamp: -1 }
    } = options;
    
    const query = {};
    
    if (tenant_id) query.tenant_id = tenant_id;
    if (user_id) query.user_id = user_id;
    if (action) query.action = action;
    if (resource_type) query.resource_type = resource_type;
    if (resource_id) query.resource_id = resource_id;
    
    if (start_date || end_date) {
      query.timestamp = {};
      if (start_date) query.timestamp.$gte = new Date(start_date);
      if (end_date) query.timestamp.$lte = new Date(end_date);
    }
    
    const logs = await AuditLog.find(query)
      .sort(sort)
      .limit(limit)
      .skip(skip)
      .populate('user_id', 'name email')
      .lean();
    
    const total = await AuditLog.countDocuments(query);
    
    return {
      logs,
      total,
      limit,
      skip,
      has_more: total > (skip + limit)
    };
  }
  
  /**
   * Get audit statistics
   */
  async getStatistics(tenant_id, start_date, end_date) {
    const match = {
      tenant_id,
      timestamp: {
        $gte: new Date(start_date),
        $lte: new Date(end_date)
      }
    };
    
    const stats = await AuditLog.aggregate([
      { $match: match },
      {
        $group: {
          _id: '$action',
          count: { $sum: 1 },
          success_count: {
            $sum: { $cond: [{ $eq: ['$result', 'success'] }, 1, 0] }
          },
          failure_count: {
            $sum: { $cond: [{ $eq: ['$result', 'failure'] }, 1, 0] }
          }
        }
      },
      { $sort: { count: -1 } }
    ]);
    
    const total = await AuditLog.countDocuments(match);
    
    return {
      total_actions: total,
      actions_by_type: stats,
      period: {
        start: start_date,
        end: end_date
      }
    };
  }
  
  /**
   * Get user activity
   */
  async getUserActivity(user_id, limit = 50) {
    return await AuditLog.find({ user_id })
      .sort({ timestamp: -1 })
      .limit(limit)
      .select('timestamp action resource_type resource_id result')
      .lean();
  }
}

// Export singleton instance
module.exports = new AuditService();
