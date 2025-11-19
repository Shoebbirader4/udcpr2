import React, { useState } from 'react';
import { Upload, FileText, X, Loader, CheckCircle } from 'lucide-react';
import axios from 'axios';

export default function DrawingUpload({ projectId, onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    try {
      const visionUrl = process.env.REACT_APP_VISION_SERVICE_URL || 'http://localhost:8001/api/vision';
      const response = await axios.post(`${visionUrl}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);
      if (onUploadComplete) {
        onUploadComplete(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Upload Drawing</h3>

      {!file ? (
        <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition">
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload size={48} className="text-gray-400 mb-3" />
            <p className="mb-2 text-sm text-gray-600">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">PDF, JPG, PNG, TIFF (MAX. 10MB)</p>
          </div>
          <input
            type="file"
            className="hidden"
            accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
            onChange={handleFileSelect}
          />
        </label>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <FileText size={24} className="text-blue-600" />
              <div>
                <p className="font-medium text-sm">{file.name}</p>
                <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <button onClick={handleRemove} className="text-gray-400 hover:text-red-600">
              <X size={20} />
            </button>
          </div>

          {!result && !uploading && (
            <button
              onClick={handleUpload}
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
            >
              <Upload size={20} />
              Upload & Analyze
            </button>
          )}

          {uploading && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Loader size={20} className="animate-spin text-blue-600" />
              <span className="text-sm text-gray-600">Analyzing drawing...</span>
            </div>
          )}

          {result && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={20} className="text-green-600" />
                <span className="font-medium text-green-900">Analysis Complete</span>
              </div>
              <div className="text-sm text-gray-700 space-y-1">
                <p>Upload ID: {result.upload_id}</p>
                <p>Status: {result.status}</p>
                {result.geometry && (
                  <>
                    <p>Plot Area: {result.geometry.plot_area_sqm?.toFixed(2)} sqm</p>
                    <p>Building Area: {result.geometry.building_area_sqm?.toFixed(2)} sqm</p>
                  </>
                )}
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-900">{error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
