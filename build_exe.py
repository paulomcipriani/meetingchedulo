import PyInstaller.__main__
import sys
import os

# Adicionar PyInstaller ao path se necessário
sys.path.append(os.path.dirname(PyInstaller.__file__))

# Configurar os argumentos para o PyInstaller
args = [
    'escala_gui.py',  # Script principal
    '--onefile',  # Criar um único arquivo executável
    '--noconsole',  # Não mostrar console
    '--name=Sistema de Escala',  # Nome do executável
    '--clean',  # Limpar cache antes de construir
    '--add-data=dados.json;.',  # Incluir o arquivo de dados
    '--hidden-import=babel.numbers',  # Importações necessárias
    '--hidden-import=babel.dates',
    '--hidden-import=reportlab.graphics.barcode',
    '--hidden-import=reportlab.graphics.barcode.code39',
    '--hidden-import=reportlab.graphics.barcode.code93',
    '--hidden-import=reportlab.graphics.barcode.code128',
    '--hidden-import=reportlab.graphics.barcode.usps',
    '--hidden-import=reportlab.graphics.barcode.usps4s',
    '--hidden-import=reportlab.graphics.barcode.ecc200datamatrix',
]

# Executar o PyInstaller
PyInstaller.__main__.run(args) 