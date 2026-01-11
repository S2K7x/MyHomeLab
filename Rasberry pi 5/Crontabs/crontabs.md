# Simply my crontabs, nothing to see here

# 1. BackupRepo : Tous les jours à 00h00
# 00 00 * * * cd /home/pi/Scripts/BackupRepo && /home/pi/Scripts/env/bin/python3 backuprepo.py

# 2. Cryptalyst : Tous les jours à 19h00
# 00 19 * * * cd /home/pi/Scripts/Cryptalyst && /home/pi/Scripts/env/bin/python3 Cryptalyst.py

# 3. Forge : Tous les jours à 12h00
00 12 * * * cd /home/pi/Scripts/Forge && /home/pi/Scripts/env/bin/python3 forge.py

# 4. Joker : Toutes les 2 heures (ex: 00h, 02h, 04h...)
00 */2 * * * cd /home/pi/Scripts/Joker && /home/pi/Scripts/env/bin/python3 joker.py

# 5. Miru : Toutes les 2 heures
05 */2 * * * cd /home/pi/Scripts/Miru && /home/pi/Scripts/env/bin/python3 miru.py

# 6. Nexus : Tous les jours à 11h00
00 11 * * * cd /home/pi/Scripts/Nexus && /home/pi/Scripts/env/bin/python3 nexus.py

# 7. Scripties : Tous les jours à 00h00
00 00 * * * cd /home/pi/Scripts/Scripties && /home/pi/Scripts/env/bin/python3 scripties.py

# 7. Jokette xxx : Toute les 4 heures
0 */4 * * * cd /home/pi/Scripts/Joker && /home/pi/Scripts/env/bin/python3 jokerxxx.py