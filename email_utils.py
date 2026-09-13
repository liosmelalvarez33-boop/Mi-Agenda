import smtplib
import json
import os
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_email.json")


def cargar_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def guardar_config(remitente, password, nombre="MiAgenda", smtp_host="smtp.gmail.com", smtp_port=587):
    config = {"remitente": remitente, "password": password, "nombre": nombre,
              "smtp_host": smtp_host, "smtp_port": smtp_port}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    return config


def enviar_email(destinatario, asunto, cuerpo_html):
    config = cargar_config()
    if not config:
        return False, "No hay configuración de email."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = f"{config['nombre']} <{config['remitente']}>"
        msg["To"] = destinatario
        msg.attach(MIMEText(cuerpo_html, "html"))
        with smtplib.SMTP(config["smtp_host"], config["smtp_port"], timeout=30) as server:
            server.starttls()
            server.login(config["remitente"], config["password"])
            server.send_message(msg)
        return True, "Email enviado"
    except Exception as e:
        return False, f"Error: {e}"


def enviar_recordatorio_cita(cita, email_destino):
    id_c, cliente, telefono, fecha, hora, motivo, estado = cita
    asunto = f"Recordatorio de su cita - {fecha} {hora}"
    cuerpo = f"""
    <html><body style="font-family: Arial;">
        <h2>Recordatorio de cita</h2>
        <p>Hola <b>{cliente}</b>,</p>
        <p>Le recordamos su cita:</p>
        <table style="border-collapse: collapse;">
            <tr><td style="padding: 5px 15px;"><b>Fecha:</b></td><td>{fecha}</td></tr>
            <tr><td style="padding: 5px 15px;"><b>Hora:</b></td><td>{hora}</td></tr>
            <tr><td style="padding: 5px 15px;"><b>Motivo:</b></td><td>{motivo}</td></tr>
        </table>
        <p>Si necesita reprogramar, contáctenos.</p>
        <p style="color: #888; font-size: 12px;">Enviado por MiAgenda</p>
    </body></html>
    """
    return enviar_email(email_destino, asunto, cuerpo)


def enviar_resumen_diario(destinatario):
    hoy = datetime.now().strftime("%Y-%m-%d")
    conexion = sqlite3.connect("agenda.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, cliente, telefono, fecha, hora, motivo, estado FROM citas WHERE fecha = ? ORDER BY hora", (hoy,))
    citas = cursor.fetchall()
    conexion.close()
    if not citas:
        cuerpo = f"<html><body><h2>MiAgenda - {hoy}</h2><p>No hay citas para hoy.</p></body></html>"
    else:
        filas = "".join(
            f"<tr><td style='padding: 5px 10px;'>{c[4]}</td>"
            f"<td style='padding: 5px 10px;'>{c[1]}</td>"
            f"<td style='padding: 5px 10px;'>{c[5]}</td>"
            f"<td style='padding: 5px 10px;'>{c[6]}</td></tr>"
            for c in citas)
        cuerpo = f"""<html><body style="font-family: Arial;">
        <h2>MiAgenda - Citas de hoy ({hoy})</h2>
        <table border="1" style="border-collapse: collapse;">
            <tr style="background:#1f6aa5; color:white;">
                <th style="padding: 5px 10px;">Hora</th>
                <th style="padding: 5px 10px;">Cliente</th>
                <th style="padding: 5px 10px;">Motivo</th>
                <th style="padding: 5px 10px;">Estado</th>
            </tr>{filas}</table></body></html>"""
    asunto = f"MiAgenda - Resumen de hoy ({hoy}) - {len(citas)} citas"
    return enviar_email(destinatario, asunto, cuerpo)
