import React, { useState, useCallback } from 'react';
import { Upload, X, FileImage, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import axios from 'axios';

const DrawingUploadModal = ({ isOpen, onClose, projectId, onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    handleFile(droppedFile);
  }, []);

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;
    
    const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp', 'application/pdf'];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Please upload a valid image or PDF file');
      return;
    }

    setFile(selectedFile);
    setError(null);
    
    // Create preview for images
    if (selectedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const uploadDrawing = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8001/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setJobId(response.data.job_id);
      setUploading(false);
      setProcessing(true);
      
      // Poll for results
      pollResults(response.data.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      setUploading(false);
    }
  };

  const pollResults = async (id) => {
    const maxAttempts = 30;
    let attempts = 0;

    const poll = setInterval(async () => {
      attempts++;
      
      try {
        const statusRes = await axios.get(`http://localhost:8001/status/${id}`);
        
        if (statusRes.data.status === 'completed') {
          clearInterval(poll);
          const resultRes = await axios.get(`http://localhost:8001/result/${id}`);
          setResult(resultRes.data);
          setProcessing(false);
          
          if (onUploadComplete) {
            onUploadComplete(resultRes.data);
          }
        } else if (statusRes.data.status === 'failed') {
          clearInterval(poll);
          setError('Processing failed');
          setProcessing(false);
        }
        
        if (attempts >= maxAttempts) {
          clearInterval(poll);
          setError('Processing timeout');
          setProcessing(false);
        }
      } catch (err) {
        clearInterval(poll);
        setError('Failed to get results');
        setProcessing(false);
      }
    }, 2000);
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setJobId(null);
    setUploading(false);
    setProcessing(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b flex justify-between items-center">
          <h2 className="text-2xl font-bold">Upload Drawing</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="p-6">
          {!result ? (
            <>
              {/* Upload Area */}
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors"
              >
                <input
                  type="file"
                  id="drawing-upload"
                  className="hidden"
                  accept=".jpg,.jpeg,.png,.tiff,.bmp,.pdf"
                  onChange={(e) => handleFile(e.target.files[0])}
                />
                
                {!file ? (
                  <label htmlFor="drawing-upload" className="cursor-pointer">
                    <Upload className="mx-auto mb-4 text-gray-400" size={48} />
                    <p className="text-lg mb-2">Drop your drawing here or click to browse</p>
                    <p className="text-sm text-gray-500">Supports: JPG, PNG, TIFF, BMP, PDF</p>
                  </label>
                ) : (
                  <div className="space-y-4">
                    {preview && (
                      <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded" />
                    )}
                    <div className="flex items-center justify-center gap-2">
                      <FileImage size={20} />
                      <span className="font-medium">{file.name}</span>
                      <button onClick={reset} className="text-red-500 hover:text-red-700">
                        <X size={20} />
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                  <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
                  <p className="text-red-700">{error}</p>
                </div>
              )}

              {file && !uploading && !processing && (
                <button
                  onClick={uploadDrawing}
                  className="mt-6 w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Process Drawing
                </button>
              )}

              {(uploading || processing) && (
                <div className="mt-6 text-center">
                  <Loader className="animate-spin mx-auto mb-2 text-blue-600" size={32} />
                  <p className="text-gray-600">
                    {uploading ? 'Uploading...' : 'Processing drawing...'}
                  </p>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Results */}
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle size={24} />
                  <h3 className="text-xl font-bold">Processing Complete</h3>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Plot Area</p>
                    <p className="text-2xl font-bold">{result.plot_area?.toFixed(2) || 'N/A'} m²</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Building Area</p>
                    <p className="text-2xl font-bold">{result.building_area?.toFixed(2) || 'N/A'} m²</p>
                  </div>
                </div>

                {result.setbacks && (
                  <div>
                    <h4 className="font-bold mb-2">Detected Setbacks</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-3 bg-blue-50 rounded">
                        <p className="text-sm text-gray-600">Front</p>
                        <p className="font-bold">{result.setbacks.front?.toFixed(2) || 'N/A'} m</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded">
                        <p className="text-sm text-gray-600">Rear</p>
                        <p className="font-bold">{result.setbacks.rear?.toFixed(2) || 'N/A'} m</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded">
                        <p className="text-sm text-gray-600">Left</p>
                        <p className="font-bold">{result.setbacks.left?.toFixed(2) || 'N/A'} m</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded">
                        <p className="text-sm text-gray-600">Right</p>
                        <p className="font-bold">{result.setbacks.right?.toFixed(2) || 'N/A'} m</p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={reset}
                    className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
                  >
                    Upload Another
                  </button>
                  <button
                    onClick={onClose}
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                  >
                    Done
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DrawingUploadModal;
