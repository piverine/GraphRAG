'use client';

import React, { useState } from 'react';
import axios from 'axios';

interface UploadInterfaceProps {
  onIngestComplete?: () => void;
}

export default function UploadInterface({ onIngestComplete }: UploadInterfaceProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatusMsg(null);
      setIsError(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setStatusMsg('Uploading PDF and queuing background graph extraction...');
    setIsError(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatusMsg(`✅ ${res.data.message}`);
      setFile(null);
      if (onIngestComplete) onIngestComplete();
    } catch (err: any) {
      setIsError(true);
      setStatusMsg(err.response?.data?.detail || 'Upload failed. Check backend status.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      <h2 className="text-lg font-semibold text-slate-100 mb-1 flex items-center gap-2">
        <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 0115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        Upload Research Paper
      </h2>
      <p className="text-xs text-slate-400 mb-4">
        Upload a PDF to parse and automatically extract entities and relationships into Neo4j.
      </p>

      <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 transition-colors rounded-lg p-6 text-center bg-slate-950/50">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
          id="pdf-upload-input"
        />
        <label htmlFor="pdf-upload-input" className="cursor-pointer flex flex-col items-center justify-center">
          <svg className="w-10 h-10 text-slate-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="text-sm font-medium text-slate-300">
            {file ? file.name : 'Click to select a PDF paper'}
          </span>
          <span className="text-xs text-slate-500 mt-1">Maximum 50MB PDF</span>
        </label>
      </div>

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full mt-4 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium text-sm py-2.5 px-4 rounded-lg shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50"
        >
          {uploading ? 'Processing & Ingesting...' : 'Start Extraction & Ingestion'}
        </button>
      )}

      {statusMsg && (
        <div className={`mt-3 p-3 rounded-lg text-xs border ${isError ? 'bg-rose-950/50 border-rose-800 text-rose-300' : 'bg-indigo-950/50 border-indigo-800 text-indigo-300'}`}>
          {statusMsg}
        </div>
      )}
    </div>
  );
}
