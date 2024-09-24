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
    signature_data = data.get('signature')

    if not name or not signature_data:
        return jsonify({'error': 'Nome ou assinatura não fornecidos.'}), 400

    signature_bytes = base64.b64decode(signature_data.split(',')[1])
    signature_image = Image.open(io.BytesIO(signature_bytes)).convert("RGBA")

    # Remover o fundo branco da assinatura
    datas = signature_image.getdata()
    new_data = []
    for item in datas:
        # Mudança do branco (ou quase branco) para transparente
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_data.append((255, 255, 255, 0))  # Troca para transparente
        else:
            new_data.append(item)

    signature_image.putdata(new_data)

    # Primeiro upload: Upload da assinatura do usuário
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    signature_file_name = f'{name}_signature_{timestamp}.png'
    signature_upload_path = f'person-signature/{signature_file_name}'
    response = supabase.storage.from_('generate').upload(signature_upload_path, signature_bytes)

    # Construir o URL da assinatura
    signature_url = f'{STORAGE_BASE_URL}{signature_upload_path}'

    # Criar uma nova imagem com fundo rosa
    width, height = signature_image.size
    new_height = height + 50  # Espaço para o nome

    combined_image = Image.new('RGBA', (width, new_height), 'pink')
    combined_image.paste(signature_image, (0, 0), signature_image)

    # Adicionar o nome abaixo da assinatura
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_position = ((width - text_width) / 2, height + 10)
    draw.text(text_position, name, fill='black', font=font)

    # Salvar a imagem combinada em bytes
    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Segundo upload: Upload da nova imagem combinada
    combined_file_name = f'{name}_combined_{timestamp}.png'
    combined_upload_path = f'person-signature/{combined_file_name}'
    response = supabase.storage.from_('generate').upload(combined_upload_path, img_byte_arr)

    # Construir o URL da imagem combinada
    combined_image_url = f'{STORAGE_BASE_URL}{combined_upload_path}'

    return jsonify({
        'message': 'Assinatura e imagem combinada enviadas com sucesso!',
        'signature_url': signature_url,
        'combined_image_url': combined_image_url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
