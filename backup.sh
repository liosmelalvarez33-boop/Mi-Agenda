#!/bin/bash
cd "$(dirname "$0")"
FECHA=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp agenda.db "backups/agenda_$FECHA.db"
echo "✅ Copia creada: backups/agenda_$FECHA.db"
ls -t backups/agenda_*.db | tail -n +11 | xargs -r rm
