#!/usr/bin/env python3
"""Combine two SVG files into a 2-page PDF."""

import cairosvg
from PyPDF2 import PdfMerger
import tempfile

# Convert each SVG to PDF
with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f1:
    temp_pdf1 = f1.name
    cairosvg.svg2pdf(url='blank_page1.svg', write_to=temp_pdf1)

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f2:
    temp_pdf2 = f2.name
    cairosvg.svg2pdf(url='blank_page2.svg', write_to=temp_pdf2)

# Merge PDFs
merger = PdfMerger()
merger.append(temp_pdf1)
merger.append(temp_pdf2)

output_file = "blank_grids_2page.pdf"
merger.write(output_file)
merger.close()

print(f"Generated {output_file} with 2 pages (4 grids per page)")
