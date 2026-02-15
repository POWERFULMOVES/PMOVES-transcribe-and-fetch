import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    // Extract force_overwrite parameter from query
    const { searchParams } = new URL(request.url);
    const force_overwrite = searchParams.get('force_overwrite') === 'true';
    
    // Get file from form data
    const formData = await request.formData();
    const file = formData.get('file');

    if (!file) {
      return NextResponse.json({ error: 'File is required' }, { status: 400 });
    }

    console.log(`Forwarding transcript upload to backend: ${file.name}, force_overwrite: ${force_overwrite}`);

    // Create a new FormData to send to the backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    // Forward the file to the backend
    const backendUrl = process.env.INTERNAL_BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/content/upsert/transcript?force_overwrite=${force_overwrite}`, 
      {
        method: 'POST',
        body: backendFormData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json({ error: data.detail || 'Failed to process transcript' }, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error uploading transcript:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 
