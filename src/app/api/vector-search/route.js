import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request) {
  try {
    const { query, threshold = 0.7 } = await request.json();

    if (!query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // Path to the Python script
    const scriptPath = path.join(process.cwd(), 'PMOVES Supabase', 'pmoves_vector_search.py');

    return new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        scriptPath,
        '--query', query,
        '--threshold', threshold.toString()
      ]);

      let results = '';
      let errors = '';

      pythonProcess.stdout.on('data', (data) => {
        results += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        errors += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error('Python script error:', errors);
          resolve(NextResponse.json(
            { error: 'Error executing search' },
            { status: 500 }
          ));
          return;
        }

        try {
          const searchResults = JSON.parse(results);
          resolve(NextResponse.json({ results: searchResults }));
        } catch (error) {
          console.error('Error parsing results:', error);
          resolve(NextResponse.json(
            { error: 'Error parsing search results' },
            { status: 500 }
          ));
        }
      });
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
