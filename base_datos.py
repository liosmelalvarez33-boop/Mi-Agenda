import sqlite3

def conectar():
    """Conecta a la base de datos (la crea si no existe)."""
    conexion = sqlite3.connect("agenda.db")
    return conexion

def crear_tabla():
    """Crea la tabla de citas si no existe."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            telefono TEXT,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT,
            estado TEXT DEFAULT 'pendiente'
        )
    """)
    conexion.commit()
    conexion.close()
