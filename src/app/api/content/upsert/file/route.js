import { NextResponse } from 'next/server';
import { createClient } from '@/lib/server'; // Adjusted path assuming lib is at src/lib

export async function POST(request) {
  try {
    const body = await request.json();
    const { fileInfo, metadata } = body;

    // Validate incoming data
    if (!fileInfo || typeof fileInfo !== 'object' || !metadata || typeof metadata !== 'object') {
      return NextResponse.json({ error: 'Invalid request payload: fileInfo and metadata are required.' }, { status: 400 });
    }

    const { path: file_path, name: file_name, size: file_size, type: file_type, url: storage_url } = fileInfo;
    const { title, description, contentType: content_type, overwriteExisting, additionalMetadata: additional_metadata_string } = metadata;

    if (!file_path || !file_name) {
      return NextResponse.json({ error: 'Missing required fields in fileInfo: path and name are required.' }, { status: 400 });
    }
    if (typeof title === 'undefined' || typeof description === 'undefined' || typeof content_type === 'undefined') {
      return NextResponse.json({ error: 'Missing required fields in metadata: title, description, and contentType are required.' }, { status: 400 });
    }

    let parsedAdditionalMetadata = {};
    if (additional_metadata_string) {
      try {
        parsedAdditionalMetadata = JSON.parse(additional_metadata_string);
      } catch (parseError) {
        console.error('Error parsing additionalMetadata JSON:', parseError);
        return NextResponse.json({ error: 'Invalid JSON format for additionalMetadata.' }, { status: 400 });
      }
    }

    const supabase = await createClient();
    const tableName = 'content_items';

    const recordToUpsert = {
      file_path,
      file_name,
      file_size: file_size || null,
      file_type: file_type || null,
      storage_url: storage_url || null,
      title,
      description,
      content_type,
      additional_metadata: parsedAdditionalMetadata,
      // created_at and updated_at will be handled by Supabase defaults or triggers
    };

    let data, error, status, statusText;

    if (overwriteExisting && file_path) {
      // Attempt to update if overwriteExisting is true and file_path is provided
      const { data: updateData, error: updateError } = await supabase
        .from(tableName)
        .update({ ...recordToUpsert, updated_at: new Date().toISOString() })
        .eq('file_path', file_path)
        .select()
        .single(); // Use single() if you expect at most one match or want an error if multiple

      if (updateError && updateError.code !== 'PGRST116') { // PGRST116: 0 rows updated (record not found)
        console.error('Supabase update error:', updateError);
        return NextResponse.json({ error: `Supabase update error: ${updateError.message}` }, { status: 500 });
      }

      if (updateData) {
        data = updateData;
        status = 200;
        statusText = 'Record updated successfully.';
      } else {
        // Record not found for update, so insert it
        const { data: insertData, error: insertError } = await supabase
          .from(tableName)
          .insert(recordToUpsert)
          .select()
          .single();
        
        if (insertError) {
          console.error('Supabase insert error (after failed update attempt):', insertError);
          return NextResponse.json({ error: `Supabase insert error: ${insertError.message}` }, { status: 500 });
        }
        data = insertData;
        status = 201;
        statusText = 'Record created successfully.';
      }
    } else {
      // Insert a new record
      const { data: insertData, error: insertError } = await supabase
        .from(tableName)
        .insert(recordToUpsert)
        .select()
        .single();

      if (insertError) {
        // Check for unique constraint violation if not overwriting (e.g., duplicate file_path)
        if (insertError.code === '23505') { // Unique violation
             return NextResponse.json({ error: `A record with this file path already exists. Set overwriteExisting to true to update it. Details: ${insertError.message}` }, { status: 409 }); // 409 Conflict
        }
        console.error('Supabase insert error:', insertError);
        return NextResponse.json({ error: `Supabase insert error: ${insertError.message}` }, { status: 500 });
      }
      data = insertData;
      status = 201;
      statusText = 'Record created successfully.';
    }

    return NextResponse.json({ message: statusText, data }, { status });

  } catch (error) {
    console.error('API Route Error:', error);
    if (error instanceof SyntaxError && error.message.includes("JSON")) {
        return NextResponse.json({ error: 'Invalid JSON payload provided.' }, { status: 400 });
    }
    return NextResponse.json({ error: 'Internal server error', details: error.message }, { status: 500 });
  }
}