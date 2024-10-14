from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Ruta para manejar el escaneo del código QR
@app.route('/production/QROFFER')
def scan(offer_id):
    conn = sqlite3.connect('offers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, description, offer_type, max_scans, scans FROM offers WHERE offer_id = ?', (offer_id,))
    offer = cursor.fetchone()

    if not offer:
        conn.close()
        return "Oferta no encontrada o inválida."

    title, description, offer_type, max_scans, scans = offer

    if scans >= max_scans:
        conn.close()
        return "Oferta Expirada"

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

if __name__ == "__main__":
    # Asegurarse de que la base de datos exista
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
        conn.commit()
        conn.close()

    app.run(debug=False, host='0.0.0.0', port=5000)
