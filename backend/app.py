from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
import io
import base64

app = Flask(__name__)
CORS(app) 

SUPABASE_URL = 'https://pvohcqzdzmzvzidyvjss.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2b2hjcXpkem16dnppZHl2anNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjcxMTUyNTAsImV4cCI6MjA0MjY5MTI1MH0.sopZMZLs8Kl8miYsS9rKhQ7sn38eRHQDIKfu2ltl1Yg'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
STORAGE_BASE_URL = f'{SUPABASE_URL}/storage/v1/object/public/generate/'

@app.route('/upload', methods=['POST'])
def upload_signature():
    data = request.get_json()

    name = data.get('name')
    age = data.get('age')
    cause_of_death = data.get('causeOfDeath')

    if not name or not age or not cause_of_death:
        return jsonify({'error': 'Nome ou idade ou causa da morte não fornecidos.'}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    font_path = './fanta.otf' 
    template_image = Image.open(f'./assets/{cause_of_death}.png')

    font_size = 85
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(template_image)

    left_section_width = template_image.width / 2
    
    # Posicionar e desenhar o nome
    text_bbox_name = draw.textbbox((0, 0), name, font=font)
    text_width_name = text_bbox_name[2] - text_bbox_name[0]
    text_x_name = (template_image.width - text_width_name) / 2
    text_y_name = 450  # posição vertical do nome

    draw.text((text_x_name, text_y_name), name, font=font, fill='white')

    # Posicionar e desenhar a idade
    text_bbox_age = draw.textbbox((0, 0), age, font=font)
    text_width_age = text_bbox_age[2] - text_bbox_age[0]
    text_x_age = (left_section_width - text_width_age) / 2 + 109
    text_y_age = text_y_name + 140  # ajustar abaixo do nome

    draw.text((text_x_age, text_y_age), age, font=font, fill='white')

    # Salvar a imagem combinada em bytes
    img_byte_arr = io.BytesIO()
    template_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Segundo upload: Upload da nova imagem combinada
    combined_file_name = f'{name}_combined_{timestamp}.png'
    combined_upload_path = f'person-signature/{combined_file_name}'
    response = supabase.storage.from_('generate').upload(combined_upload_path, img_byte_arr)

    # Construir o URL da imagem combinada
    combined_image_url = f'{STORAGE_BASE_URL}{combined_upload_path}'

    return jsonify({
        'message': 'Assinatura e imagem combinada enviadas com sucesso!',
        'combined_image_url': combined_image_url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
