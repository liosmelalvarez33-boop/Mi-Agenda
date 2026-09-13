#!/bin/bash
# Instalador de MiAgenda
# Uso: ./instalar.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPIMAGE="$SCRIPT_DIR/MiAgenda-x86_64.AppImage"

if [ ! -f "$APPIMAGE" ]; then
    echo "❌ No se encontró MiAgenda-x86_64.AppImage en esta carpeta."
    echo "   Asegúrate de tener los 2 archivos juntos:"
    echo "   - MiAgenda-x86_64.AppImage"
    echo "   - instalar.sh"
    exit 1
fi

echo "📦 Instalando MiAgenda..."

mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons

cp "$APPIMAGE" ~/.local/bin/MiAgenda.AppImage
chmod +x ~/.local/bin/MiAgenda.AppImage

cd "$SCRIPT_DIR"
"$APPIMAGE" --appimage-extract miagenda.png >/dev/null 2>&1 || true
if [ -f squashfs-root/miagenda.png ]; then
    cp squashfs-root/miagenda.png ~/.local/share/icons/miagenda.png
    rm -rf squashfs-root
fi

cat > ~/.local/share/applications/miagenda.desktop << DESKTOP
[Desktop Entry]
Type=Application
Name=MiAgenda
Comment=Gestión de citas y recordatorios
Exec=$HOME/.local/bin/MiAgenda.AppImage
Icon=$HOME/.local/share/icons/miagenda.png
Terminal=false
Categories=Office;Calendar;
DESKTOP

update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons 2>/dev/null || true

echo ""
echo "✅ ¡MiAgenda instalada!"
echo ""
echo "Búscala en el menú de aplicaciones como 'MiAgenda'"
echo "O ejecútala desde la terminal:"
echo "   ~/.local/bin/MiAgenda.AppImage"
echo ""
echo "Para desinstalar:"
echo "   rm ~/.local/bin/MiAgenda.AppImage"
echo "   rm ~/.local/share/applications/miagenda.desktop"
echo "   rm ~/.local/share/icons/miagenda.png"
