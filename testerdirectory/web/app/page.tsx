'use client';

import { useState, useRef } from 'react';

interface Document {
  id: string;
  text?: string;
  metadata?: Record<string, any>;
  uri?: string;
}

interface ApiResponse {
  message?: string;
  error?: string;
}

export default function Home() {
  const [collections, setCollections] = useState<string[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string>('');
  const [newCollectionName, setNewCollectionName] = useState<string>('');
  const [documents, setDocuments] = useState<Document[]>([{ id: '', text: '', metadata: {} }]);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE_URL = 'http://localhost:8000';
  const API_KEY = 'your-secure-api-key';

  const apiHeaders = {
    'Content-Type': 'application/json',
    'access_token': API_KEY,
  };

  // Create a new collection
  const createCollection = async () => {
    if (!newCollectionName.trim()) {
      setError('Collection name is required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/collections/create_collection?name=${encodeURIComponent(newCollectionName)}`, {
        method: 'POST',
        headers: apiHeaders,
      });

      const data: ApiResponse = await response.json();
      
      if (response.ok) {
        setMessage(`Collection "${newCollectionName}" created successfully!`);
        setCollections(prev => [...prev, newCollectionName]);
        setSelectedCollection(newCollectionName);
        setNewCollectionName('');
      } else {
        setError(data.error || 'Failed to create collection');
      }
    } catch (err) {
      setError('Network error: Could not connect to API');
    } finally {
      setLoading(false);
    }
  };

  // Add a new document form
  const addDocumentForm = () => {
    setDocuments(prev => [...prev, { id: '', text: '', metadata: {} }]);
  };

  // Remove a document form
  const removeDocumentForm = (index: number) => {
    setDocuments(prev => prev.filter((_, i) => i !== index));
  };

  // Update document data
  const updateDocument = (index: number, field: keyof Document, value: any) => {
    setDocuments(prev => prev.map((doc, i) => 
      i === index ? { ...doc, [field]: value } : doc
    ));
  };

  // Handle file upload
  const handleFileUpload = async (index: number, file: File) => {
    const text = await file.text();
    const fileName = file.name.split('.')[0];
    
    updateDocument(index, 'id', fileName);
    updateDocument(index, 'text', text);
    updateDocument(index, 'metadata', { 
      fileName: file.name, 
      fileSize: file.size, 
      fileType: file.type,
      uploadDate: new Date().toISOString()
    });
  };

  // Upload documents to collection
  const uploadDocuments = async () => {
    if (!selectedCollection) {
      setError('Please select a collection');
      return;
    }

    const validDocuments = documents.filter(doc => doc.id.trim() && (doc.text?.trim() || doc.uri?.trim()));
    
    if (validDocuments.length === 0) {
      setError('Please provide at least one document with an ID and content');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/documents/add_documents_background/${encodeURIComponent(selectedCollection)}`, {
        method: 'POST',
        headers: apiHeaders,
        body: JSON.stringify(validDocuments),
      });

      const data: ApiResponse = await response.json();
      
      if (response.ok) {
        setMessage(`Successfully uploaded ${validDocuments.length} document(s) to "${selectedCollection}"!`);
        setDocuments([{ id: '', text: '', metadata: {} }]);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        setError(data.error || 'Failed to upload documents');
      }
    } catch (err) {
      setError('Network error: Could not connect to API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            ChromaRAG Document Upload
          </h1>

          {/* Messages */}
          {message && (
            <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
              {message}
            </div>
          )}
          
          {error && (
            <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {/* Collection Management */}
          <div className="mb-8 p-6 bg-gray-50 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Collection Management</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Create New Collection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Create New Collection
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newCollectionName}
                    onChange={(e) => setNewCollectionName(e.target.value)}
                    placeholder="Enter collection name"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={createCollection}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    Create
                  </button>
                </div>
              </div>

              {/* Select Existing Collection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Collection for Upload
                </label>
                <select
                  value={selectedCollection}
                  onChange={(e) => setSelectedCollection(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a collection...</option>
                  {collections.map((collection) => (
                    <option key={collection} value={collection}>
                      {collection}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Document Upload */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Document Upload</h2>
              <button
                onClick={addDocumentForm}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                + Add Document
              </button>
            </div>

            {documents.map((document, index) => (
              <div key={index} className="mb-6 p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-medium">Document {index + 1}</h3>
                  {documents.length > 1 && (
                    <button
                      onClick={() => removeDocumentForm(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Document ID */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Document ID *
                    </label>
                    <input
                      type="text"
                      value={document.id}
                      onChange={(e) => updateDocument(index, 'id', e.target.value)}
                      placeholder="Unique document identifier"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* URI */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      URI (optional)
                    </label>
                    <input
                      type="url"
                      value={document.uri || ''}
                      onChange={(e) => updateDocument(index, 'uri', e.target.value)}
                      placeholder="https://example.com/document"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* File Upload */}
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Upload File
                  </label>
                  <input
                    ref={index === 0 ? fileInputRef : undefined}
                    type="file"
                    accept=".txt,.md,.json,.csv"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(index, file);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Text Content */}
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Text Content
                  </label>
                  <textarea
                    value={document.text || ''}
                    onChange={(e) => updateDocument(index, 'text', e.target.value)}
                    rows={4}
                    placeholder="Enter document text content..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Metadata */}
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Metadata (JSON format)
                  </label>
                  <textarea
                    value={JSON.stringify(document.metadata || {}, null, 2)}
                    onChange={(e) => {
                      try {
                        const metadata = JSON.parse(e.target.value);
                        updateDocument(index, 'metadata', metadata);
                      } catch {
                        // Invalid JSON, keep as is for user to fix
                      }
                    }}
                    rows={3}
                    placeholder='{"category": "example", "tags": ["tag1", "tag2"]}'
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          <div className="text-center">
            <button
              onClick={uploadDocuments}
              disabled={loading || !selectedCollection}
              className="px-8 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium text-lg"
            >
              {loading ? 'Uploading...' : 'Upload Documents'}
            </button>
          </div>

          {/* Instructions */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Instructions:</h3>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Create a collection or select an existing one</li>
              <li>• Provide a unique ID for each document</li>
              <li>• Upload files or paste text content directly</li>
              <li>• Add metadata in JSON format for better organization</li>
              <li>• Click "Upload Documents" to send to ChromaRAG API</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
