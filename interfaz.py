import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
from citas import agregar_cita, editar_cita, eliminar_cita, marcar_completada
from base_datos import crear_tabla
from recordatorios import iniciar_recordatorios, citas_proximas_24h, marcar_vencidas
from excel_utils import exportar_a_excel, importar_desde_excel
from email_utils import enviar_recordatorio_cita, enviar_resumen_diario, cargar_config, guardar_config
import sqlite3
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validar_hora(hora):
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except ValueError:
        return False


class MiAgendaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        crear_tabla()
        iniciar_recordatorios()
        marcar_vencidas()

        self.title("MiAgenda")
        self.geometry("1250x760")
        self.minsize(1050, 600)

        self.header = ctk.CTkFrame(self, height=70, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkLabel(self.header, text="MiAgenda",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(side="left", padx=20, pady=15)

        self.resumen_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.resumen_frame.pack(fill="x", padx=15, pady=(10, 5))
        self.lbl_total = self._crear_tarjeta(self.resumen_frame, "Total", "0", "#1f6aa5")
        self.lbl_hoy = self._crear_tarjeta(self.resumen_frame, "Hoy", "0", "#2fa572")
        self.lbl_pendientes = self._crear_tarjeta(self.resumen_frame, "Pendientes", "0", "#3a7ebf")
        self.lbl_vencidas = self._crear_tarjeta(self.resumen_frame, "Vencidas", "0", "#a83232")

        self.botones1 = ctk.CTkFrame(self)
        self.botones1.pack(fill="x", padx=15, pady=(10, 5))
        botones1 = [
            ("Agregar", self.ventana_agregar, "#2fa572"),
            ("Editar", self.ventana_editar, "#1f6aa5"),
            ("Completar", self.accion_completar, "#3a7ebf"),
            ("Eliminar", self.accion_eliminar, "#a83232"),
            ("Proximas 24h", self.ver_proximas, "#8a5cf6"),
        ]
        for texto, comando, color in botones1:
            ctk.CTkButton(self.botones1, text=texto, command=comando,
                          fg_color=color, hover_color="#333333",
                          width=140, height=38, corner_radius=8).pack(side="left", padx=4, pady=6)

        self.botones2 = ctk.CTkFrame(self)
        self.botones2.pack(fill="x", padx=15, pady=(0, 10))
        botones2 = [
            ("Exportar Excel", self.exportar_excel, "#2e7d32"),
            ("Importar Excel", self.importar_excel, "#1565c0"),
            ("Backup", self.hacer_backup, "#8a5c2e"),
            ("Email cliente", self.enviar_email_cliente, "#00695c"),
            ("Resumen diario", self.enviar_resumen, "#4527a0"),
            ("Config Email", self.configurar_email, "#37474f"),
        ]
        for texto, comando, color in botones2:
            ctk.CTkButton(self.botones2, text=texto, command=comando,
                          fg_color=color, hover_color="#333333",
                          width=140, height=38, corner_radius=8).pack(side="left", padx=4, pady=6)

        self.buscar_frame = ctk.CTkFrame(self)
        self.buscar_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.entry_buscar = ctk.CTkEntry(self.buscar_frame,
                                         placeholder_text="Buscar por fecha (YYYY-MM-DD)",
                                         width=300)
        self.entry_buscar.pack(side="left", padx=5, pady=8)
        ctk.CTkButton(self.buscar_frame, text="Buscar", command=self.buscar,
                      width=100, fg_color="#3a7ebf").pack(side="left", padx=5)
        ctk.CTkButton(self.buscar_frame, text="Limpiar", command=self.limpiar_busqueda,
                      width=100, fg_color="#555555").pack(side="left", padx=5)
        ctk.CTkButton(self.buscar_frame, text="Refrescar", command=self.cargar_citas,
                      width=100, fg_color="#555555").pack(side="left", padx=5)

        self.tabla_frame = ctk.CTkFrame(self)
        self.tabla_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        columnas = ("ID", "Cliente", "Telefono", "Fecha", "Hora", "Motivo", "Estado")
        self.tabla = ttk.Treeview(self.tabla_frame, columns=columnas, show="headings", height=20)
        for col in columnas:
            self.tabla.heading(col, text=col, command=lambda c=col: self.ordenar_por(c))
            self.tabla.column(col, width=100, anchor="center")
        self.tabla.column("Cliente", width=180)
        self.tabla.column("Motivo", width=220)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", background="#2b2b2b", foreground="white",
                         fieldbackground="#2b2b2b", rowheight=28, borderwidth=0)
        estilo.configure("Treeview.Heading", background="#1f6aa5",
                         foreground="white", font=("Arial", 11, "bold"))
        estilo.map("Treeview", background=[("selected", "#1f6aa5")])
        self.tabla.tag_configure("completada", foreground="#7ee787")
        self.tabla.tag_configure("vencida", foreground="#ff7b72")
        self.tabla.tag_configure("pendiente", foreground="white")

        scroll = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.bind("<Double-1>", lambda e: self.ventana_editar())

        self.cargar_citas()

    def _crear_tarjeta(self, padre, titulo, valor, color):
        frame = ctk.CTkFrame(padre, fg_color=color, corner_radius=8)
        frame.pack(side="left", padx=8, pady=8, expand=True, fill="x")
        ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=12)).pack(pady=(8, 0))
        label = ctk.CTkLabel(frame, text=valor, font=ctk.CTkFont(size=22, weight="bold"))
        label.pack(pady=(0, 8))
        return label

    def actualizar_resumen(self, resultados):
        hoy = datetime.now().strftime("%Y-%m-%d")
        total = len(resultados)
        citas_hoy = sum(1 for r in resultados if r[3] == hoy)
        pendientes = sum(1 for r in resultados if r[6] == "pendiente")
        vencidas = sum(1 for r in resultados if r[6] == "vencida")
        self.lbl_total.configure(text=str(total))
        self.lbl_hoy.configure(text=str(citas_hoy))
        self.lbl_pendientes.configure(text=str(pendientes))
        self.lbl_vencidas.configure(text=str(vencidas))

    def cargar_citas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        conexion = sqlite3.connect("agenda.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, cliente, telefono, fecha, hora, motivo, estado FROM citas ORDER BY fecha, hora")
        resultados = cursor.fetchall()
        conexion.close()
        for fila in resultados:
            self.tabla.insert("", "end", values=fila, tags=(fila[6],))
        self.actualizar_resumen(resultados)

    def ordenar_por(self, columna):
        items = [(self.tabla.set(k, columna), k) for k in self.tabla.get_children("")]
        items.sort()
        for pos, (_, k) in enumerate(items):
            self.tabla.move(k, "", pos)

    def buscar(self):
        fecha = self.entry_buscar.get().strip()
        if not fecha:
            self.cargar_citas()
            return
        if not validar_fecha(fecha):
            messagebox.showwarning("Fecha invalida", "Usa YYYY-MM-DD.")
            return
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        conexion = sqlite3.connect("agenda.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, cliente, telefono, fecha, hora, motivo, estado FROM citas WHERE fecha = ? ORDER BY hora", (fecha,))
        resultados = cursor.fetchall()
        conexion.close()
        for fila in resultados:
            self.tabla.insert("", "end", values=fila, tags=(fila[6],))
        self.actualizar_resumen(resultados)

    def limpiar_busqueda(self):
        self.entry_buscar.delete(0, "end")
        self.cargar_citas()

    def ver_proximas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        resultados = citas_proximas_24h()
        for fila in resultados:
            self.tabla.insert("", "end", values=fila, tags=(fila[6],))
        self.actualizar_resumen(resultados)
        if not resultados:
            messagebox.showinfo("Proximas 24h", "No hay citas pendientes en las proximas 24 horas.")

    def exportar_excel(self):
        try:
            ruta = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
                initialfile=f"citas_{datetime.now().strftime('%Y%m%d')}.xlsx")
            if not ruta:
                return
            exportar_a_excel(ruta)
            messagebox.showinfo("Exportar Excel", f"Guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def importar_excel(self):
        try:
            ruta = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
            if not ruta:
                return
            importadas, errores = importar_desde_excel(ruta)
            self.cargar_citas()
            messagebox.showinfo("Importar Excel", f"Importadas: {importadas} Errores: {errores}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar: {e}")

    def hacer_backup(self):
        import shutil
        os.makedirs("backups", exist_ok=True)
        nombre = f"backups/agenda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy("agenda.db", nombre)
        messagebox.showinfo("Backup", f"Copia creada:\n{nombre}")

    def enviar_email_cliente(self):
        datos = self.obtener_seleccionado()
        if not datos:
            return
        dialogo = ctk.CTkInputDialog(text="Email del cliente:", title="Enviar recordatorio")
        email = dialogo.get_input()
        if not email:
            return
        ok, msg = enviar_recordatorio_cita(datos, email)
        if ok:
            messagebox.showinfo("Email", "Recordatorio enviado")
        else:
            messagebox.showerror("Email", msg)

    def enviar_resumen(self):
        config = cargar_config()
        if not config:
            messagebox.showwarning("Sin config", "Primero configura el email.")
            return
        ok, msg = enviar_resumen_diario(config["remitente"])
        if ok:
            messagebox.showinfo("Email", "Resumen enviado")
        else:
            messagebox.showerror("Email", msg)

    def configurar_email(self):
        VentanaConfigEmail(self)

    def obtener_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una cita primero.")
            return None
        return self.tabla.item(seleccion[0])["values"]

    def ventana_agregar(self):
        VentanaFormulario(self, modo="agregar", callback=self.cargar_citas)

    def ventana_editar(self):
        datos = self.obtener_seleccionado()
        if not datos:
            return
        VentanaFormulario(self, modo="editar", datos=datos, callback=self.cargar_citas)

    def accion_completar(self):
        datos = self.obtener_seleccionado()
        if not datos:
            return
        marcar_completada(datos[0])
        self.cargar_citas()

    def accion_eliminar(self):
        datos = self.obtener_seleccionado()
        if not datos:
            return
        if messagebox.askyesno("Confirmar", f"Eliminar la cita de {datos[1]}?"):
            eliminar_cita(datos[0])
            self.cargar_citas()


class VentanaFormulario(ctk.CTkToplevel):
    def __init__(self, parent, modo="agregar", datos=None, callback=None):
        super().__init__(parent)
        self.modo = modo
        self.datos = datos
        self.callback = callback
        titulo = "Agregar cita" if modo == "agregar" else "Editar cita"
        self.title(titulo)
        self.geometry("420x500")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        self.campos = {}
        etiquetas = [
            ("cliente", "Cliente *"),
            ("telefono", "Telefono"),
            ("fecha", "Fecha (YYYY-MM-DD) *"),
            ("hora", "Hora (HH:MM) *"),
            ("motivo", "Motivo"),
        ]
        for clave, texto in etiquetas:
            ctk.CTkLabel(self, text=texto, anchor="w").pack(fill="x", padx=30, pady=(8, 0))
            entry = ctk.CTkEntry(self, width=340)
            entry.pack(padx=30, pady=(0, 5))
            self.campos[clave] = entry

        if modo == "editar" and datos:
            self.campos["cliente"].insert(0, datos[1])
            self.campos["telefono"].insert(0, datos[2])
            self.campos["fecha"].insert(0, datos[3])
            self.campos["hora"].insert(0, datos[4])
            self.campos["motivo"].insert(0, datos[5])

        ctk.CTkButton(self, text="Guardar", command=self.guardar,
                      fg_color="#2fa572", width=200, height=40).pack(pady=20)

    def guardar(self):
        valores = {k: v.get().strip() for k, v in self.campos.items()}
        if not valores["cliente"]:
            messagebox.showwarning("Faltan datos", "El cliente es obligatorio.")
            return
        if not validar_fecha(valores["fecha"]):
            messagebox.showwarning("Fecha invalida", "Usa YYYY-MM-DD.")
            return
        if not validar_hora(valores["hora"]):
            messagebox.showwarning("Hora invalida", "Usa HH:MM.")
            return
        try:
            if self.modo == "agregar":
                agregar_cita(valores["cliente"], valores["telefono"],
                             valores["fecha"], valores["hora"], valores["motivo"])
            else:
                editar_cita(self.datos[0], valores["cliente"], valores["telefono"],
                            valores["fecha"], valores["hora"], valores["motivo"])
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class VentanaConfigEmail(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuracion de Email")
        self.geometry("460x420")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Configuracion SMTP",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        config = cargar_config() or {}

        ctk.CTkLabel(self, text="Email remitente (Gmail):", anchor="w").pack(fill="x", padx=30)
        self.entry_remitente = ctk.CTkEntry(self, width=380)
        self.entry_remitente.pack(padx=30, pady=(0, 8))
        if config.get("remitente"):
            self.entry_remitente.insert(0, config["remitente"])

        ctk.CTkLabel(self, text="Contrasena de aplicacion:", anchor="w").pack(fill="x", padx=30)
        self.entry_password = ctk.CTkEntry(self, width=380, show="*")
        self.entry_password.pack(padx=30, pady=(0, 8))
        if config.get("password"):
            self.entry_password.insert(0, config["password"])

        ctk.CTkLabel(self, text="Servidor SMTP:", anchor="w").pack(fill="x", padx=30)
        self.entry_host = ctk.CTkEntry(self, width=380)
        self.entry_host.pack(padx=30, pady=(0, 8))
        self.entry_host.insert(0, config.get("smtp_host", "smtp.gmail.com"))

        ctk.CTkLabel(self, text="Puerto:", anchor="w").pack(fill="x", padx=30)
        self.entry_port = ctk.CTkEntry(self, width=380)
        self.entry_port.pack(padx=30, pady=(0, 15))
        self.entry_port.insert(0, str(config.get("smtp_port", 587)))

        ctk.CTkButton(self, text="Guardar", command=self.guardar,
                      fg_color="#2fa572", width=200, height=40).pack(pady=10)

    def guardar(self):
        remitente = self.entry_remitente.get().strip()
        password = self.entry_password.get().strip()
        host = self.entry_host.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El puerto debe ser un numero.")
            return
        if not remitente or not password:
            messagebox.showwarning("Faltan datos", "Email y contrasena son obligatorios.")
            return
        guardar_config(remitente, password, smtp_host=host, smtp_port=port)
        messagebox.showinfo("Listo", "Configuracion guardada")
        self.destroy()


if __name__ == "__main__":
    app = MiAgendaApp()
    app.mainloop()
