import base64
import io
import pymupdf
from PIL import Image


def _decode_base64_image(b64: str) -> bytes:
    # Accept both raw base64 and data URLs like "data:image/png;base64,..."
    if "," in b64 and b64.strip().lower().startswith("data:"):
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


def _fit_rect_keep_aspect(target_rect: pymupdf.Rect, img_w: int, img_h: int) -> pymupdf.Rect:
    """Return a rect inside target_rect that preserves image aspect ratio and is centered."""
    tw = target_rect.width
    th = target_rect.height
    if img_w == 0 or img_h == 0:
        return target_rect
    img_ratio = img_w / img_h
    rect_ratio = tw / th if th != 0 else img_ratio

    if img_ratio > rect_ratio:
        # Image is wider relative to target: fit by width
        new_w = tw
        new_h = tw / img_ratio
        x0 = target_rect.x0
        y0 = target_rect.y0 + (th - new_h) / 2.0
    else:
        # Image is taller relative to target: fit by height
        new_h = th
        new_w = th * img_ratio
        x0 = target_rect.x0 + (tw - new_w) / 2.0
        y0 = target_rect.y0
    return pymupdf.Rect(x0, y0, x0 + new_w, y0 + new_h)


def fill_signature(
        doc,
        field_name: str,
        b64_image: str,
        remove_field: bool = True
):
    """
    Draw a base64 signature image over the rectangle of a PDF signature (or any) form field.
    If remove_field=True, the form field is deleted, effectively flattening the signature.
    """

    # Decode image + get dimensions
    img_bytes = _decode_base64_image(b64_image)
    # Use PIL to query image size for aspect-correct scaling
    with Image.open(io.BytesIO(img_bytes)) as im:
        img_w, img_h = im.size

    # Find the matching widget by field name
    target_widget = None
    for page in doc:
        for w in page.widgets() or []:
            # w.field_name is None for some widgets; guard it
            if (w.field_name or "").strip() == field_name:
                target_widget = (page, w)
                break
        if target_widget:
            break

    if not target_widget:
        raise ValueError(f"Form field named '{field_name}' not found in PDF.")

    page, widget = target_widget
    rect = pymupdf.Rect(widget.rect)  # widget rectangle in PDF user space

    # Compute fitted rectangle (keeps image aspect ratio; centered)
    draw_rect = _fit_rect_keep_aspect(rect, img_w, img_h)

    # Draw the image over the widget rect
    page.insert_image(draw_rect, stream=img_bytes, keep_proportion=False)

    # Optionally remove the field so it's flattened (no longer editable)
    if remove_field:
        # Remove the annotation for this widget = removes the field appearance.
        # If it's the only widget of that field, this effectively removes the field.
        try:
            page.delete_annot(widget.annot)
        except Exception:
            # Fallback: if delete_annot fails, at least set the field read-only
            try:
                widget.set_readonly(True)
                widget.update()
            except Exception:
                pass


def fill_text_rich(page, field_name: str, html_body: str, pad: float = 1.5, font_size=9):
    # find the widget by field name
    w = next((w for w in (page.widgets() or []) if w.field_name == field_name), None)
    if not w:
        raise ValueError(f"Widget '{field_name}' not found on page.")

    # clear widget value & hide its visuals so our drawn text isn't overlapped
    w.field_value = ""
    w.border_color = None
    w.fill_color = None
    w.update()

    # draw styled text inside the widget rect
    r = w.rect
    draw_rect = pymupdf.Rect(r.x0 + pad, r.y0 + pad, r.x1 - pad, r.y1 - pad)
    html = f"""
        <div style="
            font-family:'Times New Roman', Times, serif;
            font-size:{font_size}pt;
            line-height:1.2;
            color:#000;
            text-align:center;">
          {html_body}
        </div>
        """
    page.insert_htmlbox(draw_rect, html)

    # flatten/remove the widget annotation itself
    for a in (page.annots() or []):
        if a.type[0] == pymupdf.PDF_ANNOT_WIDGET and getattr(a, "field_name", None) == field_name:
            a.flatten()
            break
