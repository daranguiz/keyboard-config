#!/usr/bin/env python3
"""Split multi-layer SVG into a multi-page PDF."""

import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import tempfile
import xml.etree.ElementTree as ET

# Read the SVG
tree = ET.parse('blank_grids.svg')
root = tree.getroot()

# SVG namespace
ns = {'svg': 'http://www.w3.org/2000/svg'}

# Find all layer groups (keymap-drawer creates g elements for each layer)
groups = root.findall('.//svg:g[@id]', ns)

# Group into pages of 4
layers_per_page = 4
total_layers = 8

# Create PDF
output_file = "blank_grids_multipage.pdf"
c = canvas.Canvas(output_file, pagesize=letter)
page_width, page_height = letter

# Split into 2 pages of 4 layers each
for page_num in range(2):
    # Create a temporary SVG with just 4 layers
    start_idx = page_num * layers_per_page
    end_idx = start_idx + layers_per_page

    # For now, let's use a simpler approach - render the full SVG and crop
    # This is a workaround since splitting SVG is complex
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
        temp_svg = f.name

        # Create new SVG with subset of layers
        new_root = ET.Element('{http://www.w3.org/2000/svg}svg')
        new_root.set('xmlns', 'http://www.w3.org/2000/svg')
        new_root.set('width', root.get('width', '1000'))
        new_root.set('height', str(float(root.get('height', '2000')) / 2))

        # Copy relevant groups
        for i, g in enumerate(groups[start_idx:end_idx]):
            new_g = ET.SubElement(new_root, '{http://www.w3.org/2000/svg}g')
            new_g.set('id', g.get('id'))
            # Copy all children
            for child in g:
                new_g.append(child)

        tree_new = ET.ElementTree(new_root)
        tree_new.write(temp_svg)

    # Convert to ReportLab drawing
    try:
        drawing = svg2rlg(temp_svg)
        if drawing:
            # Scale to fit page
            scale = min(page_width / drawing.width, page_height / drawing.height)
            drawing.scale(scale, scale)
            drawing.drawOn(c, 0, 0)
    except Exception as e:
        print(f"Error rendering page {page_num + 1}: {e}")

    if page_num < 1:  # Don't add page after last one
        c.showPage()

c.save()
print(f"Generated {output_file}")
