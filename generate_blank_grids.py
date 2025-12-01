#!/usr/bin/env python3
"""Generate a PDF with blank 3x5 keyboard grids for drawing."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def draw_3x5_grid(c, x, y, cell_width=0.5*inch, cell_height=0.5*inch):
    """Draw a single 3x5 grid (3 rows, 5 columns) at position (x, y)."""
    # Draw the grid
    for row in range(3):
        for col in range(5):
            cell_x = x + (col * cell_width)
            cell_y = y - (row * cell_height)
            c.rect(cell_x, cell_y, cell_width, cell_height)

def main():
    output_file = "blank_keyboard_grids.pdf"
    c = canvas.Canvas(output_file, pagesize=letter)
    page_width, page_height = letter

    # Grid dimensions
    cell_width = 0.5 * inch
    cell_height = 0.5 * inch
    grid_width = 5 * cell_width
    grid_height = 3 * cell_height

    # Spacing
    h_spacing = 0.75 * inch  # horizontal spacing between grids
    v_spacing = 0.75 * inch  # vertical spacing between grids
    margin = 0.75 * inch

    # Calculate positions for 4 grids per page (2x2 layout)
    # Start from top of page
    top_y = page_height - margin

    # Left column x position
    left_x = margin
    # Right column x position
    right_x = margin + grid_width + h_spacing

    # Top row y position
    top_row_y = top_y
    # Bottom row y position
    bottom_row_y = top_y - grid_height - v_spacing

    positions = [
        (left_x, top_row_y),      # Top left
        (right_x, top_row_y),     # Top right
        (left_x, bottom_row_y),   # Bottom left
        (right_x, bottom_row_y),  # Bottom right
    ]

    # Page 1
    for x, y in positions:
        draw_3x5_grid(c, x, y, cell_width, cell_height)

    c.showPage()

    # Page 2
    for x, y in positions:
        draw_3x5_grid(c, x, y, cell_width, cell_height)

    c.save()
    print(f"Generated {output_file} with 8 blank 3x5 grids (4 per page, 2 pages)")

if __name__ == "__main__":
    main()
