import sys
from cx_Freeze import setup, Executable

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
        "dados_servico.json" if "dados_servico.json" in sys.path else [],
        "data_tpl/pessoas.json" if "data_tpl/pessoas.json" in sys.path else [],
        "data_tpl/carrinhos.json" if "data_tpl/carrinhos.json" in sys.path else [],
        "data_tpl/pontos.json" if "data_tpl/pontos.json" in sys.path else [],
        "data_tpl/config.json" if "data_tpl/config.json" in sys.path else []
    ],
    "excludes": []
}

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