#!C:\Users\silit\PycharmProjects\RTWL\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'Naked==0.1.31','console_scripts','naked'
__requires__ = 'Naked==0.1.31'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('Naked==0.1.31', 'console_scripts', 'naked')()
    )
