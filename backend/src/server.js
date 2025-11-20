const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const projectRoutes = require('./routes/projects');
const ruleRoutes = require('./routes/rules');
const adminRoutes = require('./routes/admin');
const municipalRoutes = require('./routes/municipal');
const notificationRoutes = require('./routes/notifications');

const securityMiddleware = require('./middleware/security');
const compressionMiddleware = require('./middleware/compression');
const { apiLimiter, authLimiter } = require('./middleware/rateLimit');

const app = express();
const PORT = process.env.PORT || 3001;

// Security & Performance Middleware
app.use(securityMiddleware);
app.use(compressionMiddleware);
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(apiLimiter);

// MongoDB connection
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('✓ MongoDB connected'))
.catch(err => console.error('MongoDB connection error:', err));

// Routes
app.use('/api/auth', authLimiter, authRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/rules', ruleRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/municipal', municipalRoutes);
app.use('/api/notifications', notificationRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`✓ UDCPR Master Backend running on port ${PORT}`);
});

module.exports = app;
