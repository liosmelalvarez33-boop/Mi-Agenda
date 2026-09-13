from base_datos import conectar

def agregar_cita(cliente, telefono, fecha, hora, motivo):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO citas (cliente, telefono, fecha, hora, motivo, estado) VALUES (?, ?, ?, ?, ?, ?)",
            (cliente, telefono, fecha, hora, motivo, "pendiente")
        )
        conexion.commit()
        conexion.close()
        print(f"\n✅ Cita para {cliente} agregada correctamente.")
    except Exception as e:
        print(f"\n❌ Error al agregar la cita: {e}")

def listar_citas():
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, cliente, telefono, fecha, hora, motivo, estado FROM citas ORDER BY fecha, hora")
        resultados = cursor.fetchall()
        conexion.close()

        if not resultados:
            print("\n📭 No hay citas registradas.")
            return

        print("\n" + "=" * 100)
        print(f"{'ID':<5} {'Cliente':<20} {'Teléfono':<15} {'Fecha':<12} {'Hora':<8} {'Motivo':<25} {'Estado':<12}")
        print("-" * 100)
        for cita in resultados:
            id_c, cliente, telefono, fecha, hora, motivo, estado = cita
            print(f"{id_c:<5} {cliente:<20} {telefono:<15} {fecha:<12} {hora:<8} {motivo:<25} {estado:<12}")
        print("=" * 100)
    except Exception as e:
        print(f"\n❌ Error al listar citas: {e}")

def buscar_citas_por_fecha(fecha):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, cliente, telefono, fecha, hora, motivo, estado FROM citas WHERE fecha = ? ORDER BY hora",
            (fecha,)
        )
        resultados = cursor.fetchall()
        conexion.close()

        if not resultados:
            print(f"\n📭 No hay citas para la fecha {fecha}.")
            return

        print(f"\n📋 Citas para {fecha}:")
        print("-" * 100)
        for cita in resultados:
            id_c, cliente, telefono, fecha, hora, motivo, estado = cita
            print(f"{id_c:<5} {cliente:<20} {telefono:<15} {fecha:<12} {hora:<8} {motivo:<25} {estado:<12}")
        print("-" * 100)
    except Exception as e:
        print(f"\n❌ Error al buscar citas: {e}")

def editar_cita(id_cita, cliente=None, telefono=None, fecha=None, hora=None, motivo=None, estado=None):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT cliente, telefono, fecha, hora, motivo, estado FROM citas WHERE id = ?", (id_cita,))
        actual = cursor.fetchone()
        if not actual:
            print(f"\n❌ No existe una cita con ID {id_cita}.")
            conexion.close()
            return

        nuevos = (
            cliente if cliente else actual[0],
            telefono if telefono else actual[1],
            fecha if fecha else actual[2],
            hora if hora else actual[3],
            motivo if motivo else actual[4],
            estado if estado else actual[5],
        )
        cursor.execute(
            "UPDATE citas SET cliente=?, telefono=?, fecha=?, hora=?, motivo=?, estado=? WHERE id=?",
            (*nuevos, id_cita)
        )
        conexion.commit()
        conexion.close()
        print(f"\n✏️ Cita {id_cita} actualizada correctamente.")
    except Exception as e:
        print(f"\n❌ Error al editar la cita: {e}")

def eliminar_cita(id_cita):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM citas WHERE id = ?", (id_cita,))
        conexion.commit()
        filas = cursor.rowcount
        conexion.close()
        if filas > 0:
            print(f"\n🗑️ Cita {id_cita} eliminada.")
        else:
            print(f"\n❌ No existe una cita con ID {id_cita}.")
    except Exception as e:
        print(f"\n❌ Error al eliminar la cita: {e}")

def marcar_completada(id_cita):
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE citas SET estado = 'completada' WHERE id = ?", (id_cita,))
        conexion.commit()
        filas = cursor.rowcount
        conexion.close()
        if filas > 0:
            print(f"\n✅ Cita {id_cita} marcada como completada.")
        else:
            print(f"\n❌ No existe una cita con ID {id_cita}.")
    except Exception as e:
        print(f"\n❌ Error al marcar la cita: {e}")
