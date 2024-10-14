from flask import Flask, request, redirect, render_template_string, jsonify
import sqlite3
import os

app = Flask(__name__)  # Definir la instancia de Flask

# Ruta para manejar el escaneo del código QR
@app.route('/scan/<offer_id>')
def scan(offer_id):
    user_ip = request.remote_addr
    conn = sqlite3.connect('offers.db')
    cursor = conn.cursor()

    # Verificar si la oferta existe
    cursor.execute('SELECT title, description, offer_type, max_scans, scans FROM offers WHERE offer_id = ?', (offer_id,))
    offer = cursor.fetchone()

    if not offer:
        conn.close()
        return "Oferta no encontrada o inválida."

    title, description, offer_type, max_scans, scans = offer

    # Verificar si el usuario ya ha reclamado la oferta
    cursor.execute('SELECT COUNT(*) FROM scans WHERE offer_id = ? AND user_ip = ?', (offer_id, user_ip))
    user_scans = cursor.fetchone()[0]

    if user_scans > 0:
        conn.close()
        return "Ya has reclamado esta oferta."

    if scans >= max_scans:
        conn.close()
        return "Oferta Expirada"

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

# Ejecutar la aplicación si se ejecuta este archivo directamente
if __name__ == "__main__":
    # Inicializar la base de datos si no existe
    if not os.path.exists('offers.db'):
        conn = sqlite3.connect('offers.db')
        cursor = conn.cursor()
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
