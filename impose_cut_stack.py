from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, lightgrey
import io

MARGIN = 5  # px margin
CUT_LINE = True

def add_cut_line(base_page, width, height):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    # Draw vertical center cut line
    can.setStrokeColor(lightgrey)
    can.setLineWidth(0.6)
    can.line(width / 2, 0, width / 2, height)

    can.save()
    packet.seek(0)

    overlay = PdfReader(packet).pages[0]
    base_page.merge_page(overlay)

def impose_cut_stack(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    # Pad if needed
    pad = (4 - total_pages % 4) % 4
    for _ in range(pad):
        reader.add_blank_page()
    total_pages += pad

    writer = PdfWriter()
    page_width, page_height = landscape(A4)
    num_sheets = total_pages // 4

    slot_w = (page_width - 3 * MARGIN) / 2
    slot_h = page_height - 2 * MARGIN

    def blank():
        return PageObject.create_blank_page(width=page_width, height=page_height)

    def place(src, dst, x_left):
        ow, oh = float(src.mediabox.width), float(src.mediabox.height)
        scale = min(slot_w / ow, slot_h / oh)
        t = (Transformation().scale(scale, scale)
             .translate(x_left + (slot_w - ow * scale) / 2,
                        MARGIN + (slot_h - oh * scale) / 2))
        dst.merge_transformed_page(src, t)

    for s in range(num_sheets):
        p1 = s * 2
        p4 = total_pages - 1 - (s * 2)
        p2 = p1 + 1
        p3 = p4 - 1

        # FRONT
        front = blank()
        place(reader.pages[p1], front, MARGIN)
        place(reader.pages[p4], front, MARGIN * 2 + slot_w)
        if CUT_LINE:
            add_cut_line(front, page_width, page_height)
        writer.add_page(front)

        # BACK
        back = blank()
        place(reader.pages[p2], back, MARGIN)
        place(reader.pages[p3], back, MARGIN * 2 + slot_w)
        if CUT_LINE:
            add_cut_line(back, page_width, page_height)
        writer.add_page(back)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    print("DONE →", output_pdf)


if __name__ == "__main__":
    import sys
    input_pdf = sys.argv[1]
    output_pdf = input_pdf.replace(".pdf", "_CUT_STACK_2UP.pdf")
    impose_cut_stack(input_pdf, output_pdf)
