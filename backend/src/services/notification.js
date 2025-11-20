const Notification = require('../models/Notification');

class NotificationService {
  async create(userId, { title, message, type = 'info', link, metadata, tenantId }) {
    try {
      const notification = await Notification.create({
        user: userId,
        tenant: tenantId,
        title,
        message,
        type,
        link,
        metadata
      });
      return notification;
    } catch (error) {
      console.error('Error creating notification:', error);
      throw error;
    }
  }

  async getUserNotifications(userId, { limit = 50, unreadOnly = false } = {}) {
    const query = { user: userId };
    if (unreadOnly) {
      query.read = false;
    }
    
    return Notification.find(query)
      .sort({ createdAt: -1 })
      .limit(limit);
  }

  async markAsRead(notificationId, userId) {
    return Notification.findOneAndUpdate(
      { _id: notificationId, user: userId },
      { read: true },
      { new: true }
    );
  }

  async markAllAsRead(userId) {
    return Notification.updateMany(
      { user: userId, read: false },
      { read: true }
    );
  }

  async delete(notificationId, userId) {
    return Notification.findOneAndDelete({
      _id: notificationId,
      user: userId
    });
  }

  async getUnreadCount(userId) {
    return Notification.countDocuments({
      user: userId,
      read: false
    });
  }

  // Helper methods for common notifications
  async notifyProjectApproval(userId, projectName, tenantId) {
    return this.create(userId, {
      title: 'Project Approved',
      message: `Your project "${projectName}" has been approved by the municipal officer.`,
      type: 'success',
      tenantId
    });
  }

  async notifyProjectRejection(userId, projectName, reason, tenantId) {
    return this.create(userId, {
      title: 'Project Rejected',
      message: `Your project "${projectName}" has been rejected. Reason: ${reason}`,
      type: 'error',
      tenantId
    });
  }

  async notifyNewSubmission(officerId, projectName, tenantId) {
    return this.create(officerId, {
      title: 'New Project Submission',
      message: `A new project "${projectName}" has been submitted for review.`,
      type: 'info',
      tenantId
    });
  }
}

module.exports = new NotificationService();
