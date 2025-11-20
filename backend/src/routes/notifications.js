const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const notificationService = require('../services/notification');

// Get user notifications
router.get('/', auth, async (req, res) => {
  try {
    const { limit, unreadOnly } = req.query;
    const notifications = await notificationService.getUserNotifications(
      req.user.userId,
      { limit: parseInt(limit) || 50, unreadOnly: unreadOnly === 'true' }
    );
    res.json(notifications);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get unread count
router.get('/unread-count', auth, async (req, res) => {
  try {
    const count = await notificationService.getUnreadCount(req.user.userId);
    res.json({ count });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Mark as read
router.patch('/:id/read', auth, async (req, res) => {
  try {
    const notification = await notificationService.markAsRead(req.params.id, req.user.userId);
    if (!notification) {
      return res.status(404).json({ error: 'Notification not found' });
    }
    res.json(notification);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Mark all as read
router.patch('/mark-all-read', auth, async (req, res) => {
  try {
    await notificationService.markAllAsRead(req.user.userId);
    res.json({ message: 'All notifications marked as read' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete notification
router.delete('/:id', auth, async (req, res) => {
  try {
    const notification = await notificationService.delete(req.params.id, req.user.userId);
    if (!notification) {
      return res.status(404).json({ error: 'Notification not found' });
    }
    res.json({ message: 'Notification deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
