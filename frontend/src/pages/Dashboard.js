import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, FileText, CheckCircle, AlertCircle, Upload } from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';
import NotificationCenter from '../components/NotificationCenter';
import DrawingUploadModal from '../components/DrawingUploadModal';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [showDrawingUpload, setShowDrawingUpload] = useState(false);
  
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.get('/projects').then(res => res.data)
  });

  const stats = {
    total: projects?.length || 0,
    evaluated: projects?.filter(p => p.status === 'evaluated').length || 0,
    compliant: projects?.filter(p => p.evaluationResult?.compliant).length || 0,
    draft: projects?.filter(p => p.status === 'draft').length || 0
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'evaluated':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'draft':
        return <FileText className="text-gray-400" size={20} />;
      default:
        return <AlertCircle className="text-yellow-500" size={20} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'evaluated':
        return 'bg-green-100 text-green-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">UDCPR Master</h1>
              <p className="text-blue-100 text-sm">Maharashtra Building Regulation Compliance</p>
            </div>
            <div className="flex items-center gap-3">
              <NotificationCenter />
              <div className="text-right mr-4">
                <p className="text-white font-medium">{user?.name || 'User'}</p>
                <p className="text-blue-100 text-sm">{user?.email}</p>
              </div>
              <button
                onClick={() => navigate('/rules')}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white hover:bg-white/20 rounded-lg transition"
              >
                <FileText size={20} />
                <span className="hidden md:inline">Browse Rules</span>
              </button>
              <button
                onClick={() => navigate('/ai-assistant')}
                className="flex items-center gap-2 px-4 py-2 bg-white text-blue-600 hover:bg-blue-50 rounded-lg transition font-medium"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <span className="hidden md:inline">AI Assistant</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Stats Cards */}
      <div className="bg-gradient-to-b from-blue-700 to-blue-600 pb-16">
        <div className="max-w-7xl mx-auto px-4 pt-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-white">
              <p className="text-blue-100 text-sm mb-1">Total Projects</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-white">
              <p className="text-blue-100 text-sm mb-1">Evaluated</p>
              <p className="text-3xl font-bold">{stats.evaluated}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-white">
              <p className="text-blue-100 text-sm mb-1">Compliant</p>
              <p className="text-3xl font-bold">{stats.compliant}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-white">
              <p className="text-blue-100 text-sm mb-1">Draft</p>
              <p className="text-3xl font-bold">{stats.draft}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 -mt-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Your Projects</h2>
              <p className="text-gray-600 text-sm mt-1">Manage and track your building compliance projects</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDrawingUpload(true)}
                className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-purple-800 shadow-md transition font-medium"
              >
                <Upload size={20} />
                Upload Drawing
              </button>
              <button
                onClick={() => navigate('/project/new')}
                className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 shadow-md transition font-medium"
              >
                <Plus size={20} />
                New Project
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading projects...</p>
            </div>
          ) : projects?.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText size={48} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No projects yet</h3>
              <p className="text-gray-600 mb-6">Create your first project to start checking compliance</p>
              <button
                onClick={() => navigate('/project/new')}
                className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 shadow-md transition font-medium"
              >
                Create Your First Project
              </button>
            </div>
          ) : (
            <div className="grid gap-4">
              {projects?.map(project => (
                <div
                  key={project._id}
                  onClick={() => navigate(`/project/${project._id}`)}
                  className="bg-gradient-to-r from-white to-gray-50 p-6 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-lg cursor-pointer transition-all duration-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        {getStatusIcon(project.status)}
                        <h3 className="text-xl font-bold text-gray-900">{project.name}</h3>
                        {project.evaluationResult?.compliant !== undefined && (
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            project.evaluationResult.compliant 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {project.evaluationResult.compliant ? '✓ Compliant' : '✗ Non-Compliant'}
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Jurisdiction</p>
                          <p className="font-medium text-gray-900">{project.jurisdiction}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Zone</p>
                          <p className="font-medium text-gray-900">{project.zone}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Plot Area</p>
                          <p className="font-medium text-gray-900">{project.plotDetails?.area_sqm} sqm</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Road Width</p>
                          <p className="font-medium text-gray-900">{project.plotDetails?.road_width_m} m</p>
                        </div>
                      </div>
                    </div>
                    <div className="text-right ml-6">
                      <p className="text-sm text-gray-500 mb-2">
                        {new Date(project.updatedAt).toLocaleDateString()}
                      </p>
                      <span className={`inline-block px-4 py-2 rounded-lg text-sm font-medium ${getStatusColor(project.status)}`}>
                        {project.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Drawing Upload Modal */}
      <DrawingUploadModal
        isOpen={showDrawingUpload}
        onClose={() => setShowDrawingUpload(false)}
        onUploadComplete={(result) => {
          console.log('Drawing processed:', result);
          setShowDrawingUpload(false);
        }}
      />
    </div>
  );
}
