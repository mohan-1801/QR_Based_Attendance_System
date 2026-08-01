import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code_image(token_data, session_id):
    """
    Generates a QR code image from token string and returns ContentFile for Django FileField.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(token_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f"qr_{session_id}.png"
    return file_name, ContentFile(buffer.getvalue())
