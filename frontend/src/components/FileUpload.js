import React, { useState, useCallback } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Upload, X, File, Image } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FileUpload = ({ onFilesUploaded, maxFiles = 5 }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileSelect(droppedFiles);
  }, []);

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files);
    handleFileSelect(selectedFiles);
  };

  const handleFileSelect = (selectedFiles) => {
    if (files.length + selectedFiles.length > maxFiles) {
      toast.error(`Maksimum ${maxFiles} dosya yükleyebilirsiniz`);
      return;
    }

    // File type validation
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf', 'text/plain'];
    const invalidFiles = selectedFiles.filter(file => !allowedTypes.includes(file.type));
    
    if (invalidFiles.length > 0) {
      toast.error('Sadece resim, PDF ve metin dosyaları yükleyebilirsiniz');
      return;
    }

    // File size validation (max 5MB per file)
    const oversizedFiles = selectedFiles.filter(file => file.size > 5 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      toast.error('Dosya boyutu 5MB dan küçük olmalıdır');
      return;
    }

    const newFiles = selectedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      uploaded: false,
      url: null
    }));

    setFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Yüklenecek dosya seçiniz');
      return;
    }

    setUploading(true);
    const uploadedFiles = [];

    try {
      for (const fileItem of files) {
        if (fileItem.uploaded) {
          uploadedFiles.push(fileItem);
          continue;
        }

        const formData = new FormData();
        formData.append('file', fileItem.file);

        const response = await axios.post(`${API}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        const uploadedFile = {
          ...fileItem,
          uploaded: true,
          url: response.data.file_url,
          filename: response.data.filename
        };
        
        uploadedFiles.push(uploadedFile);
      }

      setFiles(uploadedFiles);
      
      if (onFilesUploaded) {
        onFilesUploaded(uploadedFiles.map(f => ({
          name: f.name,
          url: f.url,
          filename: f.filename,
          type: f.type
        })));
      }

      toast.success('Dosyalar başarıyla yüklendi');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Dosya yükleme hatası');
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) {
      return <Image className="w-4 h-4" />;
    }
    return <File className="w-4 h-4" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      <Card className={`border-2 border-dashed transition-colors ${
        dragOver 
          ? 'border-blue-400 bg-blue-50' 
          : 'border-gray-300 hover:border-gray-400'
      }`}>
        <CardContent 
          className="p-6 text-center"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Dosyaları buraya sürükleyin veya tıklayın
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Resim, PDF, TXT dosyaları (maks. 5MB, {maxFiles} dosyaya kadar)
          </p>
          <input
            type="file"
            multiple
            accept="image/*,.pdf,.txt"
            onChange={handleFileInput}
            className="hidden"
            id="file-input"
          />
          <Button 
            type="button"
            variant="outline" 
            onClick={() => document.getElementById('file-input').click()}
            data-testid="file-upload-btn"
          >
            Dosya Seç
          </Button>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-700">Seçilen Dosyalar:</h4>
          
          {files.map((fileItem) => (
            <div key={fileItem.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getFileIcon(fileItem.type)}
                <div>
                  <p className="text-sm font-medium text-gray-700">{fileItem.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(fileItem.size)}</p>
                </div>
                {fileItem.uploaded && (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                    Yüklendi
                  </span>
                )}
              </div>
              
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeFile(fileItem.id)}
                className="text-red-600 hover:text-red-800"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          ))}
          
          <Button
            type="button"
            onClick={uploadFiles}
            disabled={uploading || files.every(f => f.uploaded)}
            className="w-full"
            data-testid="upload-files-btn"
          >
            {uploading ? 'Yükleniyor...' : 'Dosyaları Yükle'}
          </Button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;