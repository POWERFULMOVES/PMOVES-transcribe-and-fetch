import requests
import markdown2
import pdfkit
import re
from datetime import datetime

def fetch_content_from_url(url):
    api_url = f"https://r.jina.ai/{url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def extract_title_from_url(url):
    title = url.split('//')[-1].split('/')[0]
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'__', '_', title)
    return title

def generate_unique_filename(url, extension):
    title = extract_title_from_url(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{title}_{timestamp}.{extension}"

def save_text_to_markdown(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def convert_markdown_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()
    html_text = markdown2.markdown(markdown_text)
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    pdfkit.from_string(html_text, pdf_path, configuration=config)