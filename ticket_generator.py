import qrcode
from PIL import Image, ImageDraw, ImageFont
import uuid
import requests
import sqlite3

def generate_ticket(title, description, offer_type, max_scans):
    # Generar un UUID para la oferta
    offer_id = str(uuid.uuid4())

    # Conectar a la base de datos y guardar la oferta
    conn = sqlite3.connect('offers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            offer_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            offer_type INTEGER,
            max_scans INTEGER,
            scans INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        INSERT INTO offers (offer_id, title, description, offer_type, max_scans)
        VALUES (?, ?, ?, ?, ?)
    ''', (offer_id, title, description, offer_type, max_scans))
    conn.commit()
    conn.close()

    # URL del servidor con el ID de la oferta
    qr_url = f"https://qroffer.onrender.com"

    # Generar el código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')

    # Crear la imagen del boleto
    ticket = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(ticket)

    # Fuentes (asegúrate de que las fuentes estén disponibles en tu servidor)
    title_font = ImageFont.truetype("arial.ttf", 40)
    desc_font = ImageFont.truetype("arial.ttf", 24)
    offer_font = ImageFont.truetype("arial.ttf", 32)

    # Añadir el título
    draw.text((20, 20), title, font=title_font, fill='black')

    # Añadir la descripción
    draw.text((20, 80), description, font=desc_font, fill='black')

    # Determinar el tipo de oferta
    if offer_type == 1:
        offer_text = "¡Llévate algo gratis!"
    elif offer_type == 2:
        offer_text = "¡Producto gratis al comprar otro!"
    elif offer_type == 3:
        offer_text = "¡Descuento especial en tu compra!"
    else:
        offer_text = ""

    # Añadir el texto de la oferta
    draw.text((20, 140), offer_text, font=offer_font, fill='red')

    # Insertar el código QR en el boleto
    qr_img = qr_img.resize((200, 200))
    ticket.paste(qr_img, (350, 150))

    # Guardar el boleto
    ticket_filename = f'boleto_{offer_id}.png'
    ticket.save(ticket_filename)
    print(f"Boleto generado exitosamente como '{ticket_filename}'.")
    print(f"URL del QR: {qr_url}")

if __name__ == "__main__":
    # Datos personalizados por el usuario
    titulo = input("Ingrese el título del boleto: ")
    descripcion = input("Ingrese la descripción del boleto: ")
    print("Tipo de oferta:")
    print("1. Algo gratis")
    print("2. Gratis con la compra de otro producto")
    print("3. Porcentaje de descuento en algún producto")
    oferta = int(input("Seleccione el tipo de oferta (1-3): "))
    max_escaneos = int(input("Ingrese la cantidad máxima de escaneos permitidos: "))

    generate_ticket(titulo, descripcion, oferta, max_escaneos)
