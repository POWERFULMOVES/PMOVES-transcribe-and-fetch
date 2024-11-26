import os
import asyncio
import yt_dlp as youtube_dl
import pandas as pd
from datetime import datetime
from faster_whisper import WhisperModel
from pydub import AudioSegment
from .utils import ensure_directory_exists, clean_filename, download_audio, save_text_to_markdown, convert_markdown_to_pdf, save_segments_to_csv, save_segments_to_excel, format_as_hyperlink, generate_unique_filename

# Set environment variable to allow duplicate OpenMP runtimes
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Initialize the Whisper model with GPU and FP16
model = WhisperModel("large-v2", device="cuda", compute_type="float16")

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02}:{seconds:.3f}"

async def process_video(youtube_video_url, obsidian_dir, status_updates, transcription_updates):
    try:
        await ensure_directory_exists('mp4')
        await ensure_directory_exists('csv')
        await ensure_directory_exists('xlsx')
        await ensure_directory_exists(obsidian_dir)

        await status_updates.put("Extracting video information...")
        ydl_opts = {'quiet': True}
        info_dict = await asyncio.to_thread(youtube_dl.YoutubeDL(ydl_opts).extract_info, youtube_video_url, download=False)
        title = info_dict.get('title', None)
        watch_url = info_dict.get('webpage_url', None)
        video_id = info_dict.get('id', None)

        title = clean_filename(title)
        audio_output_path = os.path.join('mp4', f"{title}.mp4")
        await status_updates.put(f"Downloading audio to {audio_output_path}")
        await download_audio(youtube_video_url, audio_output_path)

        await status_updates.put("Transcribing audio")
        result = await transcribe_audio(audio_output_path, status_updates, transcription_updates)

        # Convert segments to DataFrame
        df = pd.DataFrame(result['segments'])
        
        # Cache the transcription
        csv_filename = f"{video_id}.csv"
        csv_path = os.path.join('csv', csv_filename)
        await asyncio.to_thread(df.to_csv, csv_path, index=False)
        
        # Create export DataFrame
        df_export = df[['id', 'start', 'text']].copy()
        df_export.insert(0, 'video_id', video_id)
        df_export.insert(0, 'watch_url', watch_url)
        
        # Modify watch_url to include timestamp
        df_export.loc[:, 'watch_url'] = df_export.apply(lambda row: f"{row['watch_url']}&t={int(row['start'])}", axis=1)
        
        # Format watch_url as hyperlink
        df_export.loc[:, 'watch_url'] = df_export['watch_url'].apply(format_as_hyperlink)
        
        # Export to Markdown
        markdown_filename = f"{title}_table.md"
        markdown_path = os.path.join(obsidian_dir, markdown_filename)
        await asyncio.to_thread(df_export.to_markdown, markdown_path)
        
        # Export to Excel
        xlsx_filename = f"{video_id}.xlsx"
        xlsx_path = os.path.join('xlsx', xlsx_filename)
        await asyncio.to_thread(df_export.to_excel, xlsx_path, sheet_name=video_id, index=False)

        # Save full transcription text
        full_text_filename = f"{title}_full_text.md"
        full_text_path = os.path.join(obsidian_dir, full_text_filename)
        await save_text_to_markdown(result['text'], full_text_path)

        # Convert full text to PDF
        pdf_filename = f"{title}_full_text.pdf"
        pdf_path = os.path.join(obsidian_dir, pdf_filename)
        await convert_markdown_to_pdf(full_text_path, pdf_path)

        await status_updates.put("Video processing completed")
        return {
            'transcription_text': result['text'],
            'markdown_path': markdown_path,
            'full_text_path': full_text_path,
            'pdf_path': pdf_path,
            'csv_path': csv_path,
            'xlsx_path': xlsx_path,
            'segments': df_export.head(5).to_dict(orient='records')
        }
    except Exception as e:
        await status_updates.put(f"Error processing video: {str(e)}")
        raise RuntimeError(f"Error processing video: {str(e)}")

async def transcribe_audio(audio_path, status_updates, transcription_updates):
    await status_updates.put("Loading Faster Whisper model")

    audio = await asyncio.to_thread(AudioSegment.from_file, audio_path)
    await status_updates.put("Transcribing with Faster Whisper")

    segments, info = await asyncio.to_thread(model.transcribe, audio_path, beam_size=5)
    total_duration = format_duration(info.duration)
    await status_updates.put(f"Detected language '{info.language}' with probability {info.language_probability}")
    await status_updates.put(f"Processing audio with duration {total_duration}")

    transcription_text = ""
    segment_list = []

    for segment in segments:
        transcription_text += segment.text + " "
        segment_list.append({
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        await transcription_updates.put(segment.text)

    await status_updates.put("Transcription completed")
    return {"text": transcription_text, "segments": segment_list, "total_duration": total_duration}

# You may need to add any missing utility functions or imports depending on your project structure