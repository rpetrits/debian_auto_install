import gzip
import shutil
import os
import subprocess

# 1. initrd.gz entpacken
with gzip.open('initrd.gz', 'rb') as f_in:
    with open('initrd.cpio', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

# 2. preseed.cfg als neuen CPIO-Eintrag anhängen
with open('initrd.cpio', 'ab') as f_out:
    subprocess.run(
        ['cpio', '-o', '-H', 'newc'],
        input=b'preseed.cfg\n',
        stdout=f_out,
        check=True
    )

# 3. Wieder einpacken
with open('initrd.cpio', 'rb') as f_in:
    with gzip.open('initrd_master.gz', 'wb', compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)

# Aufräumen
os.remove('initrd.cpio')
print("Erfolgreich! 'initrd_master.gz' wurde erstellt.")
