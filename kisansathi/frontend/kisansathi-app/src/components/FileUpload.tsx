import React, { useState } from 'react';
import { getAPIBaseURL } from '../utils/api';
import '../styles/FileUpload.css';

interface FileUploadProps {
  onUploadSuccess?: (data: any) => void;
  fileType?: 'image' | 'video' | 'document';
  folder?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  onUploadSuccess, 
  fileType = 'image',
  folder = 'kisansathi'
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    try {
      const baseURL = getAPIBaseURL();
      const endpoint = `/files/upload/${fileType}`;
      
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          setUploadProgress(percentComplete);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setUploadedFile(response.data);
          setFile(null);
          setError(null);
          if (onUploadSuccess) {
            onUploadSuccess(response.data);
          }
        } else {
          const response = JSON.parse(xhr.responseText);
          setError(response.error || 'Upload failed');
        }
        setUploading(false);
      });

      xhr.addEventListener('error', () => {
        setError('Upload failed');
        setUploading(false);
      });

      xhr.open('POST', `${baseURL}${endpoint}`);
      xhr.send(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!uploadedFile) return;

    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(
        `${baseURL}/files/delete/${uploadedFile.public_id}?type=${fileType}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        setUploadedFile(null);
        setError(null);
      } else {
        const data = await response.json();
        setError(data.error || 'Delete failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  return (
    <div className="file-upload-container">
      <div className="upload-box">
        <h3>Upload {fileType.charAt(0).toUpperCase() + fileType.slice(1)}</h3>
        
        {!uploadedFile ? (
          <>
            <div className="file-input-wrapper">
              <input
                type="file"
                onChange={handleFileChange}
                disabled={uploading}
                accept={
                  fileType === 'image' ? 'image/*' :
                  fileType === 'video' ? 'video/*' :
                  '.pdf,.doc,.docx,.txt,.xls,.xlsx'
                }
              />
              <span className="file-label">
                {file ? file.name : 'Choose file or drag and drop'}
              </span>
            </div>

            {uploading && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p>{Math.round(uploadProgress)}%</p>
              </div>
            )}

            {error && <p className="error-message">{error}</p>}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="upload-button"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </>
        ) : (
          <div className="uploaded-file">
            <h4>File Uploaded Successfully!</h4>
            
            {fileType === 'image' && (
              <img src={uploadedFile.url} alt="Uploaded" className="preview-image" />
            )}
            
            <div className="file-info">
              <p><strong>URL:</strong> <a href={uploadedFile.url} target="_blank" rel="noopener noreferrer">{uploadedFile.url}</a></p>
              <p><strong>Size:</strong> {(uploadedFile.size / 1024).toFixed(2)} KB</p>
              <p><strong>Format:</strong> {uploadedFile.format}</p>
              {uploadedFile.width && <p><strong>Dimensions:</strong> {uploadedFile.width}x{uploadedFile.height}</p>}
            </div>

            <button onClick={handleDelete} className="delete-button">
              Delete File
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
