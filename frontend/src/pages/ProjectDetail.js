import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Play, Download } from 'lucide-react';
import api from '../api/client';
import { useToast } from '../components/Toast';
import FSIChart from '../components/FSIChart';
import SetbackDiagram from '../components/SetbackDiagram';
import DrawingUpload from '../components/DrawingUpload';

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => api.get(`/projects/${id}`).then(res => res.data)
  });

  const evaluate = useMutation({
    mutationFn: () => api.post(`/projects/${id}/evaluate`),
    onSuccess: () => {
      queryClient.invalidateQueries(['project', id]);
      toast.success('Compliance check completed successfully!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Evaluation failed');
    }
  });

  if (isLoading) return <div className="p-8">Loading...</div>;

  const result = project?.evaluationResult;
  const hasValidResult = result && (result.fsi_result || result.setback_result || result.parking_result);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <button onClick={() => navigate('/dashboard')} className="hover:bg-gray-100 p-2 rounded">
            <ArrowLeft size={20} />
          </button>
          <h1 className="text-xl font-bold">{project?.name}</h1>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-6">
            {!hasValidResult ? (
              <div className="bg-white p-8 rounded-lg shadow text-center">
                <div className="mb-6">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Play size={32} className="text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Ready to Evaluate</h3>
                  <p className="text-gray-600 mb-4">
                    Run compliance check to calculate FSI, setbacks, parking requirements, and more.
                  </p>
                </div>
                <button
                  onClick={() => evaluate.mutate()}
                  disabled={evaluate.isPending}
                  className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 mx-auto disabled:opacity-50"
                >
                  <Play size={20} />
                  {evaluate.isPending ? 'Evaluating...' : 'Run Compliance Check'}
                </button>
                {evaluate.isError && (
                  <p className="mt-4 text-red-600 text-sm">
                    Error running evaluation. Make sure Rule Engine is running.
                  </p>
                )}
              </div>
            ) : (
              <>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-lg font-semibold mb-4">Compliance Status</h2>
                  <div className={`p-4 rounded-lg ${result.compliant ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                    <p className="font-medium">
                      {result.compliant ? '✓ Compliant' : '✗ Non-Compliant'}
                    </p>
                    {result.violations?.length > 0 && (
                      <ul className="mt-2 space-y-1 text-sm">
                        {result.violations.map((v, i) => (
                          <li key={i}>• {v}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-lg font-semibold mb-4">FSI Analysis</h2>
                  <FSIChart fsiResult={result.fsi_result} />
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-lg font-semibold mb-4">Setbacks</h2>
                  <SetbackDiagram setbackResult={result.setback_result} />
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-lg font-semibold mb-4">Parking</h2>
                  <p className="text-sm text-gray-600">Required ECS</p>
                  <p className="text-2xl font-bold">{result.parking_result?.required_ecs}</p>
                </div>
              </>
            )}
          </div>

          <div className="space-y-6">
            <DrawingUpload 
              projectId={id} 
              onUploadComplete={(data) => toast.success('Drawing analyzed successfully!')}
            />
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold mb-4">Project Details</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-gray-600">Jurisdiction</p>
                  <p className="font-medium">{project?.jurisdiction}</p>
                </div>
                <div>
                  <p className="text-gray-600">Zone</p>
                  <p className="font-medium">{project?.zone}</p>
                </div>
                <div>
                  <p className="text-gray-600">Plot Area</p>
                  <p className="font-medium">{project?.plotDetails?.area_sqm} sqm</p>
                </div>
                <div>
                  <p className="text-gray-600">Road Width</p>
                  <p className="font-medium">{project?.plotDetails?.road_width_m}m</p>
                </div>
              </div>
            </div>

            {hasValidResult && (
              <button 
                onClick={() => {
                  window.open(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/projects/${id}/export/pdf`, '_blank');
                }}
                className="w-full flex items-center justify-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900"
              >
                <Download size={20} />
                Export PDF
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
