import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import api from '../api/client';

export default function ProjectWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const { register, handleSubmit, watch, formState: { errors } } = useForm();

  const createProject = useMutation({
    mutationFn: (data) => api.post('/projects', data),
    onSuccess: (response) => {
      navigate(`/project/${response.data._id}`);
    }
  });

  const onSubmit = (data) => {
    const projectData = {
      name: data.name,
      jurisdiction: data.jurisdiction,
      zone: data.zone,
      plotDetails: {
        area_sqm: parseFloat(data.plot_area),
        road_width_m: parseFloat(data.road_width),
        corner_plot: data.corner_plot === 'true',
        frontage_m: parseFloat(data.frontage)
      },
      buildingDetails: {
        use_type: data.use_type,
        proposed_floors: parseInt(data.proposed_floors),
        proposed_height_m: parseFloat(data.proposed_height),
        proposed_built_up_sqm: parseFloat(data.proposed_built_up)
      },
      specialConditions: {
        tod_zone: data.tod_zone === 'true',
        redevelopment: data.redevelopment === 'true',
        slum_rehab: data.slum_rehab === 'true'
      }
    };

    createProject.mutate(projectData);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold mb-6">New Project</h1>

          <div className="mb-8">
            <div className="flex items-center justify-between">
              {[1, 2, 3].map(s => (
                <div key={s} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    step >= s ? 'bg-blue-600 text-white' : 'bg-gray-200'
                  }`}>
                    {s}
                  </div>
                  {s < 3 && <div className="w-24 h-1 bg-gray-200 mx-2" />}
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-2 text-sm">
              <span>Basic Info</span>
              <span>Plot Details</span>
              <span>Building Details</span>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Project Name</label>
                  <input
                    {...register('name', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                    placeholder="e.g., Residential Complex - Andheri"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Jurisdiction</label>
                  <select {...register('jurisdiction', { required: true })} className="w-full border rounded-lg px-3 py-2">
                    <option value="">Select...</option>
                    <option value="maharashtra_udcpr">Maharashtra UDCPR</option>
                    <option value="mumbai_dcpr">Mumbai DCPR 2034</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Zone</label>
                  <select {...register('zone', { required: true })} className="w-full border rounded-lg px-3 py-2">
                    <option value="">Select...</option>
                    <option value="Residential">Residential</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Industrial">Industrial</option>
                    <option value="Mixed">Mixed Use</option>
                  </select>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Plot Area (sqm)</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('plot_area', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Road Width (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    {...register('road_width', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Frontage (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    {...register('frontage', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Corner Plot?</label>
                  <select {...register('corner_plot')} className="w-full border rounded-lg px-3 py-2">
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                  </select>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Use Type</label>
                  <select {...register('use_type', { required: true })} className="w-full border rounded-lg px-3 py-2">
                    <option value="">Select...</option>
                    <option value="Residential">Residential</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Industrial">Industrial</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Proposed Floors</label>
                  <input
                    type="number"
                    {...register('proposed_floors', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Proposed Height (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    {...register('proposed_height', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Proposed Built-up Area (sqm)</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('proposed_built_up', { required: true })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>

                <div className="border-t pt-4 mt-4">
                  <h3 className="font-medium mb-3">Special Conditions</h3>
                  
                  <div className="space-y-2">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" {...register('tod_zone')} value="true" />
                      <span className="text-sm">TOD Zone</span>
                    </label>
                    
                    <label className="flex items-center gap-2">
                      <input type="checkbox" {...register('redevelopment')} value="true" />
                      <span className="text-sm">Redevelopment Project</span>
                    </label>
                    
                    <label className="flex items-center gap-2">
                      <input type="checkbox" {...register('slum_rehab')} value="true" />
                      <span className="text-sm">Slum Rehabilitation</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-between mt-8">
              <button
                type="button"
                onClick={() => step > 1 ? setStep(step - 1) : navigate('/dashboard')}
                className="px-6 py-2 border rounded-lg hover:bg-gray-50"
              >
                {step === 1 ? 'Cancel' : 'Back'}
              </button>

              {step < 3 ? (
                <button
                  type="button"
                  onClick={() => setStep(step + 1)}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Next
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={createProject.isPending}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createProject.isPending ? 'Creating...' : 'Create Project'}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
