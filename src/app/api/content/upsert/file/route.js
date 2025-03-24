import { NextResponse } from 'next/server';

export const config = {
  api: {
    bodyParser: false,
    responseLimit: false,
  },
};

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const content_type = formData.get('content_type');
    const metadata_json = formData.get('metadata_json');

    if (!file) {
      return NextResponse.json({ error: 'File is required' }, { status: 400 });
    }

    console.log(`Forwarding file upload to backend: ${file.name}, type: ${content_type || 'auto-detect'}`);

    // Create a new FormData to send to the backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);
    
    if (content_type) {
      backendFormData.append('content_type', content_type);
    }
    
    if (metadata_json) {
      backendFormData.append('metadata_json', metadata_json);
    }

    // Forward the file to the backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/content/upsert/file`, {
      method: 'POST',
      body: backendFormData,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json({ error: data.detail || 'Failed to process file' }, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 