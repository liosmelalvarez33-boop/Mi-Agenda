import os
import sys

# Cuando PyInstaller empaqueta, redirigimos el directorio de trabajo
# a ~/.miagenda para que la base de datos persista entre ejecuciones.
if getattr(sys, 'frozen', False):
    user_home = os.path.expanduser("~")
    data_dir = os.path.join(user_home, ".miagenda")
    os.makedirs(data_dir, exist_ok=True)
    os.chdir(data_dir)

from interfaz import MiAgendaApp

if __name__ == "__main__":
    app = MiAgendaApp()
    app.mainloop()
