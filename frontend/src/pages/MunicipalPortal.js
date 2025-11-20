import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, XCircle, Clock, FileText, MessageSquare, Download } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const MunicipalPortal = () => {
  const [selectedProject, setSelectedProject] = useState(null);
  const [comment, setComment] = useState('');
  const [filter, setFilter] = useState('pending');
  const queryClient = useQueryClient();

  const { data: projects, isLoading } = useQuery({
    queryKey: ['municipal-projects', filter],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/municipal/projects?status=${filter}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    }
  });

  const approveMutation = useMutation({
    mutationFn: async ({ projectId, comments }) => {
      const token = localStorage.getItem('token');
      return axios.post(
        `${API_URL}/municipal/projects/${projectId}/approve`,
        { comments },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['municipal-projects']);
      setSelectedProject(null);
      setComment('');
    }
  });

  const rejectMutation = useMutation({
    mutationFn: async ({ projectId, comments }) => {
      const token = localStorage.getItem('token');
      return axios.post(
        `${API_URL}/municipal/projects/${projectId}/reject`,
        { comments },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['municipal-projects']);
      setSelectedProject(null);
      setComment('');
    }
  });

  const getStatusBadge = (status) => {
    const badges = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock, text: 'Pending Review' },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: 'Approved' },
      rejected: { color: 'bg-red-100 text-red-800', icon: XCircle, text: 'Rejected' }
    };
    const badge = badges[status] || badges.pending;
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        <Icon size={16} />
        {badge.text}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold">Municipal Officer Portal</h1>
          <p className="mt-2 text-blue-100">Review and approve building compliance applications</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex gap-2">
            {['pending', 'approved', 'rejected', 'all'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Project List */}
          <div className="lg:col-span-1 space-y-4">
            {isLoading ? (
              <div className="text-center py-8">Loading projects...</div>
            ) : projects?.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center text-gray-500">
                No projects found
              </div>
            ) : (
              projects?.map((project) => (
                <div
                  key={project._id}
                  onClick={() => setSelectedProject(project)}
                  className={`bg-white rounded-lg shadow-sm p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedProject?._id === project._id ? 'ring-2 ring-blue-500' : ''
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg">{project.name}</h3>
                    {getStatusBadge(project.approvalStatus || 'pending')}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{project.location}</p>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Plot: {project.plotArea} m²</span>
                    <span className="text-gray-500">{project.zone}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Project Details */}
          <div className="lg:col-span-2">
            {selectedProject ? (
              <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
                <div>
                  <h2 className="text-2xl font-bold mb-2">{selectedProject.name}</h2>
                  {getStatusBadge(selectedProject.approvalStatus || 'pending')}
                </div>

                {/* Project Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Location</p>
                    <p className="font-medium">{selectedProject.location}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Jurisdiction</p>
                    <p className="font-medium">{selectedProject.jurisdiction}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Zone</p>
                    <p className="font-medium">{selectedProject.zone}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Plot Area</p>
                    <p className="font-medium">{selectedProject.plotArea} m²</p>
                  </div>
                </div>

                {/* Compliance Status */}
                {selectedProject.evaluation && (
                  <div>
                    <h3 className="font-bold mb-3">Compliance Status</h3>
                    <div className="space-y-2">
                      {selectedProject.evaluation.violations?.length > 0 ? (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                          <p className="font-medium text-red-800 mb-2">Violations Found:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {selectedProject.evaluation.violations.map((v, i) => (
                              <li key={i} className="text-red-700">{v}</li>
                            ))}
                          </ul>
                        </div>
                      ) : (
                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                          <p className="font-medium text-green-800">✓ All compliance checks passed</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Comments Section */}
                {selectedProject.approvalStatus === 'pending' && (
                  <div>
                    <label className="block font-medium mb-2">
                      <MessageSquare className="inline mr-2" size={20} />
                      Comments
                    </label>
                    <textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      className="w-full border rounded-lg p-3 h-32"
                      placeholder="Add your review comments..."
                    />
                  </div>
                )}

                {/* Actions */}
                {selectedProject.approvalStatus === 'pending' && (
                  <div className="flex gap-3">
                    <button
                      onClick={() => rejectMutation.mutate({ 
                        projectId: selectedProject._id, 
                        comments: comment 
                      })}
                      disabled={rejectMutation.isPending}
                      className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium"
                    >
                      <XCircle className="inline mr-2" size={20} />
                      Reject
                    </button>
                    <button
                      onClick={() => approveMutation.mutate({ 
                        projectId: selectedProject._id, 
                        comments: comment 
                      })}
                      disabled={approveMutation.isPending}
                      className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                    >
                      <CheckCircle className="inline mr-2" size={20} />
                      Approve
                    </button>
                  </div>
                )}

                {selectedProject.approvalComments && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="font-medium mb-2">Officer Comments:</p>
                    <p className="text-gray-700">{selectedProject.approvalComments}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center text-gray-500">
                <FileText className="mx-auto mb-4 text-gray-400" size={64} />
                <p>Select a project to review</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MunicipalPortal;
