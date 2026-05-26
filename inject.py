import gzip
import shutil
import os

# 1. Entpacke die originale initrd.gz temporär im Speicher
with gzip.open('initrd.gz', 'rb') as f_in:
    with open('initrd.cpio', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

# 2. Erstelle das CPIO-Format für die preseed.cfg
os.system('echo preseed.cfg | cpio -o -H newc >> initrd.cpio')

# 3. Packe alles wieder als master-initrd.gz zusammen
with open('initrd.cpio', 'rb') as f_in:
    with gzip.open('initrd_master.gz', 'wb', compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)

# Aufräumen
os.remove('initrd.cpio')
print("Erfolgreich! 'initrd_master.gz' wurde erstellt.")
