__author__ = "RONI YAAKOBI"
import os
from os.path import join, getsize

PATH = r"C:\Users\roniy\software_engeeniering\11th\finalProject"
SIGNATURE = '__author__ = "RONI YAAKOBI"\n'
FUTURE_ANNOTATIONS = 'from __future__ import annotations\n'

for root, dirs, files in os.walk(PATH):
    for file in files:
        if not file.endswith(".py") or file == "__init__.py":
            continue

        with open(os.path.join(root, file), "r") as f:
            lines = f.readlines()
        
        if lines and SIGNATURE not in lines[:1:]:
            with open(os.path.join(root, file), "w", newline="") as f:
                if lines[0] == FUTURE_ANNOTATIONS:
                    f.writelines([FUTURE_ANNOTATIONS, SIGNATURE] + lines[1::])
                else: 
                    f.writelines([SIGNATURE] + lines)
                print(f"[+] Signed {file}")

    if '__pycache__' in dirs:
        dirs.remove('__pycache__') # don't visit __pycache__ directories