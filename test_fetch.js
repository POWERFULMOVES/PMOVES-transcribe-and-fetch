// Test script for the URL fetching endpoint

async function testFetchEndpoint() {
  try {
    console.log('Making request to backend API...');
    
    // Call the backend API directly rather than through Next.js
    const response = await fetch('http://localhost:8000/api/content/upsert/fetch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: 'https://www.example.com',
        metadata: {
          title: 'Example Website',
          description: 'A simple example website for testing'
        }
      }),
    });
    
    const data = await response.json();
    console.log('Response status:', response.status);
    console.log('Response:', data);
    
    if (!response.ok) {
      console.error('Error:', data.detail || 'Unknown error');
    }
  } catch (err) {
    console.error('Fetch error:', err);
  }
}

// Run the test
testFetchEndpoint(); 