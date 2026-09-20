# 📅 MiAgenda

Desktop appointment & reminder manager with email notifications — built with Python, packaged as a Linux AppImage.

![MiAgenda screenshot](miagenda.png)

## ✨ Features

- 🖥️ Modern dark-mode GUI (CustomTkinter) **plus** a full terminal CLI
- 📅 Appointments: create, list, search by date, edit, mark completed, delete
- ⏰ Automatic reminders — upcoming appointments (24h) and overdue detection
- 📧 Email reminders per appointment + daily summary via SMTP
- 📊 Excel export / import (`openpyxl`)
- 💾 One-command backup script
- 📦 Ships as AppImage with a desktop installer (menu entry + icon)

## 🛠️ Tech stack

`Python` · `CustomTkinter` · `SQLite` · `smtplib` · `openpyxl` · `bash`

## 🚀 Install (Linux)

```bash
git clone https://github.com/liosmelalvarez33-boop/Mi-Agenda.git
cd Mi-Agenda
# 1. Build or download MiAgenda-x86_64.AppImage into this folder
# 2. Run the installer:
./instalar.sh
```

Then launch it from your app menu (search **MiAgenda**) or with:

```bash
~/MiAgenda/arrancar.sh
```

### Dependencies

```bash
pip install customtkinter openpyxl
```

## 💻 CLI usage

```bash
python3 main.py
```

```
===== MIAGENDA =====
1. Agregar cita
2. Ver todas las citas
3. Buscar cita por fecha
4. Editar cita
5. Eliminar cita
6. Marcar cita como completada
7. Salir
```

## 📁 Project structure

```
Mi-Agenda/
├── interfaz.py        # CustomTkinter dark-mode GUI
├── main.py            # Terminal CLI
├── citas.py           # Appointment CRUD logic
├── base_datos.py      # SQLite layer
├── recordatorios.py   # Reminder engine (24h / overdue)
├── email_utils.py     # SMTP reminders + daily summary
├── excel_utils.py     # Excel export / import
├── launcher.py        # App entry point
├── instalar.sh       # Desktop installer (menu + icon)
├── arrancar.sh       # Quick launcher
└── backup.sh         # One-command backup
```

## 💾 Backup

```bash
~/MiAgenda/backup.sh
```

---

*Built by [Liem](https://github.com/liosmelalvarez33-boop) — Linux sysadmin & automation freelancer. Available for freelance work, paid in USDT.*
