from base_datos import crear_tabla
from citas import (
    agregar_cita, listar_citas, buscar_citas_por_fecha,
    editar_cita, eliminar_cita, marcar_completada
)

def pedir_opcion():
    while True:
        opcion = input("\nElige una opción (1-7): ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= 7:
            return int(opcion)
        print("❌ Opción no válida. Debe ser un número entre 1 y 7.")

def menu():
    crear_tabla()
    while True:
        print("\n===== MIAGENDA =====")
        print("1. Agregar cita")
        print("2. Ver todas las citas")
        print("3. Buscar cita por fecha")
        print("4. Editar cita")
        print("5. Eliminar cita")
        print("6. Marcar cita como completada")
        print("7. Salir")

        opcion = pedir_opcion()

        try:
            if opcion == 1:
                cliente = input("Nombre del cliente: ").strip()
                telefono = input("Teléfono: ").strip()
                fecha = input("Fecha (YYYY-MM-DD): ").strip()
                hora = input("Hora (HH:MM): ").strip()
                motivo = input("Motivo: ").strip()
                agregar_cita(cliente, telefono, fecha, hora, motivo)

            elif opcion == 2:
                listar_citas()

            elif opcion == 3:
                fecha = input("Fecha a buscar (YYYY-MM-DD): ").strip()
                buscar_citas_por_fecha(fecha)

            elif opcion == 4:
                listar_citas()
                id_cita = int(input("\nID de la cita a editar: "))
                print("Deja en blanco lo que NO quieras cambiar.")
                cliente = input("Nuevo cliente: ").strip() or None
                telefono = input("Nuevo teléfono: ").strip() or None
                fecha = input("Nueva fecha (YYYY-MM-DD): ").strip() or None
                hora = input("Nueva hora (HH:MM): ").strip() or None
                motivo = input("Nuevo motivo: ").strip() or None
                editar_cita(id_cita, cliente, telefono, fecha, hora, motivo)

            elif opcion == 5:
                listar_citas()
                id_cita = int(input("\nID de la cita a eliminar: "))
                eliminar_cita(id_cita)

            elif opcion == 6:
                listar_citas()
                id_cita = int(input("\nID de la cita a marcar como completada: "))
                marcar_completada(id_cita)

            elif opcion == 7:
                print("\n👋 ¡Gracias por usar MiAgenda! Hasta luego.")
                break

        except ValueError:
            print("❌ Entrada inválida. Intenta de nuevo.")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    menu()