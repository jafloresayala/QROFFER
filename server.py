from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Página de inicio para evitar el error 404
@app.route('/')
def home():
    return '''
    <h1>Bienvenido a la App de Escaneo de Ofertas 🎉</h1>
    <p>Escanea un código QR válido para reclamar tu oferta.</p>
    <p>Ejemplo de ruta de escaneo: <a href="/scan/example-offer">/scan/example-offer</a></p>
    '''

# Ruta para manejar el escaneo del código QR
@app.route('/scan/<offer_id>')
def scan(offer_id):
    user_ip = request.remote_addr  # Obtener la IP del usuario
    conn = sqlite3.connect('offers.db')
    cursor = conn.cursor()

    # Verificar si la oferta existe
    cursor.execute('SELECT title, description, offer_type, max_scans, scans FROM offers WHERE offer_id = ?', (offer_id,))
    offer = cursor.fetchone()

    if not offer:
        conn.close()
        return "Oferta no encontrada o inválida."

    title, description, offer_type, max_scans, scans = offer

    # Verificar si el usuario ya reclamó la oferta usando su IP
    cursor.execute('SELECT COUNT(*) FROM scans WHERE offer_id = ? AND user_ip = ?', (offer_id, user_ip))
    user_scans = cursor.fetchone()[0]

    if user_scans > 0:
        conn.close()
        return "Ya has reclamado esta oferta."

    if scans >= max_scans:
        conn.close()
        return "Oferta Expirada."

    # Registrar el escaneo
    cursor.execute('INSERT INTO scans (offer_id, user_ip) VALUES (?, ?)', (offer_id, user_ip))

    # Incrementar el conteo de escaneos
    scans += 1
    cursor.execute('UPDATE offers SET scans = ? WHERE offer_id = ?', (scans, offer_id))

    conn.commit()
    conn.close()

    remaining_scans = max_scans - scans

    # Mostrar una página de confirmación
    return render_template_string('''
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
    <p><strong>¡Oferta reclamada!</strong></p>
    <p>Quedan {{ remaining_scans }} ofertas disponibles.</p>
    ''', title=title, description=description, remaining_scans=remaining_scans)

# Inicialización de la base de datos al iniciar el servidor
if __name__ == "__main__":
    if not os.path.exists('offers.db'):
        conn = sqlite3.connect('offers.db')
        cursor = conn.cursor()

        # Crear la tabla de ofertas si no existe
        cursor.execute('''
            CREATE TABLE offers (
                offer_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                offer_type INTEGER,
                max_scans INTEGER,
                scans INTEGER DEFAULT 0
            )
        ''')

        # Crear la tabla de escaneos si no existe
        cursor.execute('''
            CREATE TABLE scans (
                scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                offer_id TEXT,
                user_ip TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(offer_id) REFERENCES offers(offer_id)
            )
        ''')

        conn.commit()
        conn.close()

    # Ejecutar la aplicación Flask
    app.run(host='0.0.0.0', port=5000)
