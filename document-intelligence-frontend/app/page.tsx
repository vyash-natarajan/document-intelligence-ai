"use client";

import { useEffect, useState, ChangeEvent } from "react";

type StructuredData = {
  [key: string]: string | string[] | null | undefined;
};

type UploadResult = {
  id?: number;
  filename: string;
  document_type: string;
  message: string;
  structured_data: StructuredData;
  summary: string;
  key_points: string[];
  recommended_next_action: string;
  extracted_text: string;
};

type DocumentItem = {
  id: number;
  filename: string;
  document_type: string;
  structured_data: StructuredData;
  summary: string;
  key_points: string[];
  recommended_next_action: string;
  uploaded_at: string;
};

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [error, setError] = useState<string>("");

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (API_BASE_URL.startsWith("postgres")) {
      setError(
        "NEXT_PUBLIC_API_URL is incorrectly set. Use the Render backend URL, not the database URL."
      );
      return;
    }

    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`, {
        method: "GET",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }

      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError("Failed to fetch uploaded documents.");
    }
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a PDF file first.");
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setError("Only PDF files are allowed.");
      return;
    }

    if (API_BASE_URL.startsWith("postgres")) {
      setError(
        "NEXT_PUBLIC_API_URL is incorrectly set. Use the Render backend URL, not the database URL."
      );
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setUploading(true);
      setError("");
      setUploadResult(null);

      const response = await fetch(`${API_BASE_URL}/upload_pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadResult(data);
      setSelectedFile(null);

      await fetchDocuments();
    } catch (err: unknown) {
      console.error("Upload error:", err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong during upload.");
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-10">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            Document Intelligence Platform
          </h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Upload PDF documents, classify them, extract structured data,
            generate AI-ready summaries, and review document history.
          </p>
        </div>

        <section className="mb-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-4 text-2xl font-semibold text-slate-900">
            Upload PDF
          </h2>

          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:opacity-90"
            />

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploading ? "Uploading..." : "Upload and Analyze"}
            </button>
          </div>

          {selectedFile && (
            <p className="mt-4 text-sm text-slate-600">
              Selected file:{" "}
              <span className="font-medium text-slate-900">
                {selectedFile.name}
              </span>
            </p>
          )}

          {error && (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {error}
            </div>
          )}
        </section>

        {uploadResult && (
          <section className="mb-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <h2 className="mb-5 text-2xl font-semibold text-slate-900">
              Latest Analysis Result
            </h2>

            <div className="mb-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-slate-200 p-4">
                <p className="text-sm text-slate-500">Filename</p>
                <p className="mt-1 font-semibold text-slate-900">
                  {uploadResult.filename}
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 p-4">
                <p className="text-sm text-slate-500">Document Type</p>
                <p className="mt-1 font-semibold uppercase text-slate-900">
                  {uploadResult.document_type}
                </p>
              </div>
            </div>

            <div className="mb-5 rounded-xl border border-slate-200 p-4">
              <p className="mb-2 text-sm text-slate-500">Message</p>
              <p className="text-slate-800">{uploadResult.message}</p>
            </div>

            <div className="mb-5 rounded-xl border border-slate-200 p-4">
              <p className="mb-2 text-sm text-slate-500">Summary</p>
              <p className="text-slate-800">{uploadResult.summary}</p>
            </div>

            <div className="mb-5 rounded-xl border border-slate-200 p-4">
              <p className="mb-2 text-sm text-slate-500">Key Points</p>
              <ul className="list-disc space-y-1 pl-5 text-slate-800">
                {uploadResult.key_points?.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
            </div>

            <div className="mb-5 rounded-xl border border-slate-200 p-4">
              <p className="mb-2 text-sm text-slate-500">
                Recommended Next Action
              </p>
              <p className="text-slate-800">
                {uploadResult.recommended_next_action}
              </p>
            </div>

            <div className="mb-5 rounded-xl border border-slate-200 p-4">
              <p className="mb-2 text-sm text-slate-500">Structured Data</p>
              <pre className="overflow-x-auto rounded-xl bg-slate-100 p-4 text-sm text-slate-800">
                {JSON.stringify(uploadResult.structured_data, null, 2)}
              </pre>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <p className="mb-2 text-sm text-slate-500">
                Extracted Text Preview
              </p>
              <div className="max-h-96 overflow-y-auto whitespace-pre-wrap rounded-xl bg-slate-100 p-4 text-sm text-slate-800">
                {uploadResult.extracted_text}
              </div>
            </div>
          </section>
        )}

        <section className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-5 text-2xl font-semibold text-slate-900">
            Uploaded Documents History
          </h2>

          {documents.length === 0 ? (
            <p className="text-slate-500">No documents uploaded yet.</p>
          ) : (
            <div className="space-y-4">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="rounded-2xl border border-slate-200 p-5"
                >
                  <div className="mb-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {doc.filename}
                      </h3>
                      <p className="text-sm uppercase text-slate-500">
                        {doc.document_type}
                      </p>
                    </div>
                    <p className="text-sm text-slate-500">
                      {doc.uploaded_at
                        ? new Date(doc.uploaded_at).toLocaleString()
                        : "N/A"}
                    </p>
                  </div>

                  <div className="mb-3">
                    <p className="mb-1 text-sm text-slate-500">Summary</p>
                    <p className="text-slate-800">{doc.summary}</p>
                  </div>

                  <div className="mb-3">
                    <p className="mb-1 text-sm text-slate-500">Key Points</p>
                    <ul className="list-disc space-y-1 pl-5 text-slate-800">
                      {doc.key_points?.map((point, index) => (
                        <li key={index}>{point}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="mb-3">
                    <p className="mb-1 text-sm text-slate-500">
                      Recommended Next Action
                    </p>
                    <p className="text-slate-800">
                      {doc.recommended_next_action}
                    </p>
                  </div>

                  <div>
                    <p className="mb-1 text-sm text-slate-500">
                      Structured Data
                    </p>
                    <pre className="max-w-full overflow-x-auto rounded-xl bg-slate-100 p-3 text-xs text-slate-800">
                      {JSON.stringify(doc.structured_data, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}