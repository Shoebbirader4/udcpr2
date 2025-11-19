const mongoose = require('mongoose');

const projectSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  name: {
    type: String,
    required: true
  },
  jurisdiction: {
    type: String,
    enum: ['maharashtra_udcpr', 'mumbai_dcpr'],
    required: true
  },
  zone: {
    type: String,
    required: true
  },
  plotDetails: {
    area_sqm: Number,
    road_width_m: Number,
    corner_plot: Boolean,
    frontage_m: Number
  },
  buildingDetails: {
    use_type: String,
    proposed_floors: Number,
    proposed_height_m: Number,
    proposed_built_up_sqm: Number
  },
  specialConditions: {
    tod_zone: Boolean,
    redevelopment: Boolean,
    slum_rehab: Boolean
  },
  evaluationResult: {
    rule_version: String,
    evaluated_at: Date,
    fsi_result: mongoose.Schema.Types.Mixed,
    setback_result: mongoose.Schema.Types.Mixed,
    parking_result: mongoose.Schema.Types.Mixed,
    height_result: mongoose.Schema.Types.Mixed,
    compliant: Boolean,
    violations: [String],
    warnings: [String],
    calculation_traces: [mongoose.Schema.Types.Mixed]
  },
  status: {
    type: String,
    enum: ['draft', 'evaluated', 'submitted', 'approved', 'rejected'],
    default: 'draft'
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Project', projectSchema);
