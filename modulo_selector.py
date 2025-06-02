import tkinter as tk
from tkinter import ttk
import escala_servico_gui
import escala_tpl_gui

class ModuloSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Escalas")
        self.root.geometry("400x310")
        
        # Centralizar a janela
        self.center_window()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Selecione o Módulo",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Estilo para botões grandes
        style = ttk.Style()
        style.configure('Large.TButton', padding=(10, 20))
        
        # Botão para Escala de Serviço
        btn_escala = ttk.Button(
            main_frame,
            text="Escala de Serviço e Fim de Semana",
            style='Large.TButton',
            command=self.abrir_escala_servico
        )
        btn_escala.pack(fill='x', pady=5)
        
        # Botão para Escala TPL
        btn_tpl = ttk.Button(
            main_frame,
            text="Escala TPL",
            style='Large.TButton',
            command=self.abrir_escala_tpl
        )
        btn_tpl.pack(fill='x', pady=5)

        # Botão para Escala Meio de Semana (desabilitado)
        btn_tpl = ttk.Button(
            main_frame,
            text="Escala Meio de Semana (Em desenvolvimento)",
            style='Large.TButton',
            state='disabled'
        )
        btn_tpl.pack(fill='x', pady=5)
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
    def abrir_escala_servico(self):
        """Abre o módulo de Escala de Serviço"""
        self.root.withdraw()  # Esconde a janela de seleção
        
        # Cria nova janela para o módulo
        modulo_window = tk.Toplevel()
        app = escala_servico_gui.EscalaApp(modulo_window)
        
        # Quando a janela do módulo for fechada, mostra a seleção novamente
        def on_closing():
            modulo_window.destroy()
            self.root.deiconify()  # Mostra a janela de seleção novamente
            
        modulo_window.protocol("WM_DELETE_WINDOW", on_closing)
        
    def abrir_escala_tpl(self):
        """Abre o módulo de Escala TPL"""
        self.root.withdraw()  # Esconde a janela de seleção
        
        # Cria nova janela para o módulo
        modulo_window = tk.Toplevel()
        app = escala_tpl_gui.TPLApp(modulo_window)
        
        # Quando a janela do módulo for fechada, mostra a seleção novamente
        def on_closing():
            modulo_window.destroy()
            self.root.deiconify()  # Mostra a janela de seleção novamente
            
        modulo_window.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    root = tk.Tk()
    app = ModuloSelector(root)
    root.mainloop() 