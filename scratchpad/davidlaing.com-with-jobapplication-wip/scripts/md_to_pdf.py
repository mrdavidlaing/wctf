#!/usr/bin/env python3
"""
Simple markdown to PDF converter using reportlab
"""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import re

def markdown_to_pdf(md_file, pdf_file):
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=12,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=6,
        spaceBefore=12,
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=4,
        spaceBefore=8,
    )
    
    # Split content by lines
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith('# '):
            # Main title
            title_text = line[2:].strip()
            story.append(Paragraph(title_text, title_style))
        elif line.startswith('## '):
            # Section heading
            heading_text = line[3:].strip()
            story.append(Paragraph(heading_text, heading_style))
        elif line.startswith('### '):
            # Subsection
            subheading_text = line[4:].strip()
            story.append(Paragraph(subheading_text, subheading_style))
        elif line.startswith('**') and line.endswith('**'):
            # Bold line
            bold_text = line[2:-2]
            story.append(Paragraph(f"<b>{bold_text}</b>", styles['Normal']))
        elif line.startswith('---'):
            # Horizontal rule
            story.append(Spacer(1, 12))
        else:
            # Regular paragraph
            # Handle basic markdown formatting
            text = line
            # Bold text
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Italic text  
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            # Links
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<link href="\2">\1</link>', text)
            
            if text:
                story.append(Paragraph(text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md_to_pdf.py input.md output.pdf")
        sys.exit(1)
    
    markdown_to_pdf(sys.argv[1], sys.argv[2])