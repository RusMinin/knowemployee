import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def create_image_with_qrcode(url, company_name, background_image_path):
    """
    Creating a QR code for anonymous feedback
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").resize((250, 250))

    base_img = Image.new('RGB', (800, 1200), 'white')
    if background_image_path:
        base_img = Image.open(background_image_path)

    x = (base_img.width - qr_img.width) // 2
    y = (base_img.height - qr_img.height) // 2 - 55
    base_img.paste(qr_img, (x, y))

    draw = ImageDraw.Draw(base_img)
    font_path = "msfonts/Arial.ttf"
    font = ImageFont.truetype(font_path, 35)
    
    #text_width, text_height = draw.textlength(company_name, font=font_path)
    _, _, text_width, text_height = font.getbbox(text=company_name)
    text_x = (base_img.width - text_width) // 2
    text_y = y - text_height - 40
    draw.text((text_x, text_y), company_name, fill="black", font=font)

    # Convert image to base64
    buffered = io.BytesIO()
    base_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return f"data:image/png;base64,{img_str}"