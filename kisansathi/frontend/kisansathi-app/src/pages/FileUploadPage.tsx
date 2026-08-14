import React from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import FileUpload from '@/components/FileUpload';

const FileUploadPage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-1 bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto px-4">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">File Management</h1>
          <p className="text-gray-600 mb-8">Upload and manage your images, videos, and documents</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">📸 Images</h2>
              <FileUpload fileType="image" folder="kisansathi/images" />
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">🎥 Videos</h2>
              <FileUpload fileType="video" folder="kisansathi/videos" />
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">📄 Documents</h2>
              <FileUpload fileType="document" folder="kisansathi/documents" />
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default FileUploadPage;
