import asyncio
import aiofiles
import pandas as pd
import markdown2
import pdfkit
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import textwrap
import os
import logging

logger = logging.getLogger(__name__)

async def save_text_to_markdown(text, output_path):
    async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:
        await file.write(text)

async def save_data_to_markdown(df, output_path, watch_url, video_id):
    async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:
        # Write header information
        await file.write(f"# Transcription for Video: [{video_id}]({watch_url})\n\n")

        # Create the table header
        columns = df.columns.tolist()
        header = "| " + " | ".join(columns) + " |\n"
        separator = "|" + "|".join(["---" for _ in columns]) + "|\n"

        await file.write(header)
        await file.write(separator)

        # Write each row of the DataFrame
        for _, row in df.iterrows():
            row_data = []
            for col in columns:
                if col == 'start' or col == 'end':
                    row_data.append(format_timestamp(row[col]))
                elif col == 'watch_url':
                    row_data.append(f"[Link]({row[col]})")
                else:
                    row_data.append(str(row[col]))

            row_str = "| " + " | ".join(row_data) + " |\n"
            await file.write(row_str)

async def convert_text_to_pdf(text, pdf_path):
    def create_pdf():
        try:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter

            # Try to register the DejaVuSans font, fall back to Helvetica if not found
            font_name = 'Helvetica'
            font_size = 12
            try:
                font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
                pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                font_name = 'DejaVuSans'
            except Exception as e:
                logger.warning(f"Could not load DejaVuSans font: {str(e)}. Using Helvetica instead.")

            line_height = font_size * 1.2
            margin = 72  # 1 inch margin

            # Split the text into lines that fit within the page width
            lines = []
            for paragraph in text.split('\n'):
                lines.extend(textwrap.wrap(paragraph, width=80))  # Adjust the width as needed

            x = margin
            y = height - margin

            for line in lines:
                if y < margin:  # Start a new page if we've reached the bottom margin
                    c.showPage()
                    y = height - margin

                c.setFont(font_name, font_size)
                c.drawString(x, y, line)
                y -= line_height

            c.save()
            logger.info(f"PDF created successfully: {pdf_path}")
        except Exception as e:
            logger.error(f"Error creating PDF: {str(e)}", exc_info=True)
            raise

    try:
        await asyncio.to_thread(create_pdf)
    except Exception as e:
        logger.error(f"Error in convert_text_to_pdf: {str(e)}", exc_info=True)
        raise

async def save_segments_to_csv(df, output_path):
    """Save segments to CSV with proper columns"""
    try:
        # Ensure DataFrame has all required columns
        required_columns = ['watch_url', 'video_id', 'id', 'start', 'end', 'text']

        # If DataFrame doesn't have the required columns, it might be a list of segments
        if not all(col in df.columns for col in required_columns):
            # Convert list to DataFrame with proper columns
            df = pd.DataFrame(df)

        # Reorder columns to match desired format
        df = df[required_columns]

        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved CSV file to: {output_path}")

    except Exception as e:
        logger.error(f"Error saving CSV file: {str(e)}")
        raise

async def save_segments_to_excel(df, output_path):
    """Save segments to Excel with proper columns and formatting"""
    try:
        # Ensure DataFrame has all required columns
        required_columns = ['watch_url', 'video_id', 'id', 'start', 'end', 'text']

        # If DataFrame doesn't have the required columns, it might be a list of segments
        if not all(col in df.columns for col in required_columns):
            # Convert list to DataFrame with proper columns
            df = pd.DataFrame(df)

        # Reorder columns to match desired format
        df = df[required_columns]

        # Create Excel writer with xlsxwriter engine
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Transcription')

            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Transcription']

            # Add hyperlink format
            url_format = workbook.add_format({
                'color': 'blue',
                'underline': True,
            })

            # Format watch_url column as hyperlinks
            for idx, url in enumerate(df['watch_url'], start=1):
                # Remove the markdown link formatting if present
                if '[Link]' in url:
                    url = url.split('"')[1]  # Extract URL from markdown link
                worksheet.write_url(idx, 0, url, url_format, 'Link')

            # Adjust column widths
            worksheet.set_column('A:A', 50)  # watch_url
            worksheet.set_column('B:B', 15)  # video_id
            worksheet.set_column('C:C', 8)   # id
            worksheet.set_column('D:D', 12)  # start
            worksheet.set_column('E:E', 12)  # end
            worksheet.set_column('F:F', 100) # text

        logger.info(f"Saved Excel file to: {output_path}")

    except Exception as e:
        logger.error(f"Error saving Excel file: {str(e)}")
        raise

def format_timestamp(seconds):
    """ Convert seconds to HH:MM:SS format without decimal places """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"