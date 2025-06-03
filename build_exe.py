import sys
from cx_Freeze import setup, Executable
import os

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "tkinter", 
        "tkcalendar",
        "babel.numbers",
        "babel.dates",
        "reportlab",
        "reportlab.graphics.barcode",
        "reportlab.graphics.barcode.code39",
        "reportlab.graphics.barcode.code93",
        "reportlab.graphics.barcode.code128",
        "reportlab.graphics.barcode.usps",
        "reportlab.graphics.barcode.usps4s",
        "reportlab.graphics.barcode.ecc200datamatrix"
    ],
    "includes": ["tkinter", "tkcalendar"],
    "include_files": [
        ("dados_servico.json", "dados_servico.json") if os.path.exists("dados_servico.json") else None,
        ("data_tpl/pessoas.json", "data_tpl/pessoas.json") if os.path.exists("data_tpl/pessoas.json") else None,
        ("data_tpl/carrinhos.json", "data_tpl/carrinhos.json") if os.path.exists("data_tpl/carrinhos.json") else None,
        ("data_tpl/pontos.json", "data_tpl/pontos.json") if os.path.exists("data_tpl/pontos.json") else None,
        ("data_tpl/config.json", "data_tpl/config.json") if os.path.exists("data_tpl/config.json") else None
    ],
    "excludes": []
}

# Remove None entries from include_files
build_exe_options["include_files"] = [x for x in build_exe_options["include_files"] if x is not None]

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Meeting Schedulo",
    version="1.0",
    description="Sistema modular para gerenciamento de escalas",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "modulo_selector.py",
            base=base,
            target_name="Meeting Schedulo.exe"
        )
    ]
) 