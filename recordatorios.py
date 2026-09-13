import sqlite3
import threading
import time
from datetime import datetime, timedelta

# Intenta usar plyer, pero no falla si no está disponible
try:
    from plyer import notification
    PLYER_DISPONIBLE = True
except Exception:
    PLYER_DISPONIBLE = False


def obtener_citas_proximas(minutos=60):
    ahora = datetime.now()
    limite = ahora + timedelta(minutes=minutos)

    conexion = sqlite3.connect("agenda.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, cliente, fecha, hora, motivo FROM citas WHERE estado = 'pendiente'")
    filas = cursor.fetchall()
    conexion.close()

    proximas = []
    for id_c, cliente, fecha, hora, motivo in filas:
        try:
            fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if ahora <= fecha_hora <= limite:
            proximas.append((id_c, cliente, fecha_hora, motivo))
    return proximas


def marcar_vencidas():
    ahora = datetime.now()
    conexion = sqlite3.connect("agenda.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, fecha, hora FROM citas WHERE estado = 'pendiente'")
    filas = cursor.fetchall()

    for id_c, fecha, hora in filas:
        try:
            fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if fecha_hora < ahora:
            cursor.execute("UPDATE citas SET estado = 'vencida' WHERE id = ?", (id_c,))

    conexion.commit()
    conexion.close()


def notificar(titulo, mensaje):
    """Intenta notificación de escritorio; si no, imprime en consola."""
    if PLYER_DISPONIBLE:
        try:
            notification.notify(
                title=titulo,
                message=mensaje,
                app_name="MiAgenda",
                timeout=10
            )
            return
        except Exception:
            pass
    print(f"\n🔔 {titulo}: {mensaje}")


def revisar_citas():
    ya_notificadas = set()
    while True:
        try:
            marcar_vencidas()
            for id_c, cliente, fecha_hora, motivo in obtener_citas_proximas(60):
                if id_c in ya_notificadas:
                    continue
                minutos = int((fecha_hora - datetime.now()).total_seconds() // 60)
                notificar(
                    f"⏰ Cita en {minutos} min",
                    f"Cliente: {cliente} | Motivo: {motivo}"
                )
                ya_notificadas.add(id_c)
        except Exception as e:
            print(f"⚠️ Error en revisar_citas: {e}")
        time.sleep(60)


def iniciar_recordatorios():
    hilo = threading.Thread(target=revisar_citas, daemon=True)
    hilo.start()
    return hilo


def citas_proximas_24h():
    ahora = datetime.now()
    limite = ahora + timedelta(hours=24)

    conexion = sqlite3.connect("agenda.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, cliente, telefono, fecha, hora, motivo, estado
        FROM citas WHERE estado = 'pendiente'
        ORDER BY fecha, hora
    """)
    filas = cursor.fetchall()
    conexion.close()

    resultado = []
    for fila in filas:
        id_c, cliente, telefono, fecha, hora, motivo, estado = fila
        try:
            fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if ahora <= fecha_hora <= limite:
            resultado.append(fila)
    return resultado
