import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
import escala
from datetime import datetime
import os
import platform
import subprocess

class EditarPessoaDialog:
    def __init__(self, parent, nome, designacoes_atuais, todas_designacoes, callback_atualizar):
        self.top = tk.Toplevel(parent)
        self.top.title("Editar Pessoa")
        self.top.geometry("400x500")
        self.top.transient(parent)  # Faz o modal ser dependente da janela principal
        self.top.grab_set()  # Torna o modal modal
        
        # Centralizar a janela
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'+{x}+{y}')
        
        self.callback_atualizar = callback_atualizar
        self.nome_original = nome
        
        # Frame principal
        main_frame = ttk.Frame(self.top, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Campo Nome
        ttk.Label(main_frame, text="Nome:").pack(pady=(0, 5))
        self.entry_nome = ttk.Entry(main_frame)
        self.entry_nome.insert(0, nome)
        self.entry_nome.pack(fill='x', pady=(0, 10))
        
        # Lista de Designações
        ttk.Label(main_frame, text="Designações:").pack(pady=(0, 5))
        
        # Frame para a lista com scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.lista_designacoes = tk.Listbox(list_frame, selectmode='multiple',
                                          height=15, yscrollcommand=scrollbar.set)
        self.lista_designacoes.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.lista_designacoes.yview)
        
        # Preencher lista de designações
        for designacao in todas_designacoes:
            self.lista_designacoes.insert('end', designacao)
            if designacao in designacoes_atuais:
                idx = todas_designacoes.index(designacao)
                self.lista_designacoes.selection_set(idx)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Salvar", 
                  command=self.salvar).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.top.destroy).pack(side='right')
    
    def salvar(self):
        novo_nome = self.entry_nome.get().strip()
        if not novo_nome:
            messagebox.showerror("Erro", "O nome não pode estar vazio")
            return
        
        # Obter designações selecionadas
        sel = self.lista_designacoes.curselection()
        if not sel:
            messagebox.showerror("Erro", "Selecione pelo menos uma designação")
            return
        
        # Ordenar designações alfabeticamente
        designacoes = sorted([self.lista_designacoes.get(i) for i in sel])
        
        # Se o nome mudou, remover o antigo e adicionar o novo
        if novo_nome != self.nome_original:
            del escala.pessoas[self.nome_original]
        
        # Atualizar dados
        escala.pessoas[novo_nome] = designacoes
        escala.salvar_dados()
        
        # Chamar callback de atualização
        self.callback_atualizar()
        
        # Fechar janela
        self.top.destroy()

class GerarEscalaDialog:
    def __init__(self, parent, callback_gerar):
        self.top = tk.Toplevel(parent)
        self.top.title("Gerar Escala")
        self.top.geometry("400x420")  # Increased height for better spacing
        self.top.transient(parent)  # Make the modal dependent on the main window
        self.top.grab_set()  # Make it modal
        
        # Center the window
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'+{x}+{y}')
        
        # Main frame
        main_frame = ttk.Frame(self.top, padding="20")  # Increased padding
        main_frame.pack(fill='both', expand=True)
        
        # Calendar
        ttk.Label(main_frame, text="Data Inicial:").pack(pady=5)
        self.cal = Calendar(main_frame, selectmode='day', 
                          date_pattern='dd/mm/yyyy')
        self.cal.pack(pady=10)  # Increased padding
        
        # Number of weeks
        ttk.Label(main_frame, text="Número de Semanas:").pack(pady=5)
        self.spinbox_semanas = ttk.Spinbox(main_frame, from_=1, to=52)
        self.spinbox_semanas.pack(pady=10)  # Increased padding
        
        # Style for button
        style = ttk.Style()
        style.configure('Modal.TButton', padding=(20, 15))  # Increased vertical padding
        
        # Add full-width confirm button
        ttk.Button(main_frame, 
                  text="Confirmar", 
                  style='Modal.TButton',
                  command=lambda: self.confirmar_geracao(callback_gerar)).pack(fill='x', pady=(20, 0))
    
    def confirmar_geracao(self, callback):
        try:
            data = self.cal.get_date()
            semanas = int(self.spinbox_semanas.get())
            if semanas < 1:
                raise ValueError("O número de semanas deve ser maior que zero")
            
            # Call the callback with the selected values
            callback(data, semanas)
            
            # Close the dialog
            self.top.destroy()
                
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

class EscalaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Escala")
        self.root.geometry("1000x680")
        
        # Create main frame to hold notebook and footer
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both')
        
        # Load data
        escala.carregar_dados()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.criar_aba_designacoes()
        self.criar_aba_pessoas()
        self.criar_aba_datas_especiais()
        
        # Create footer
        self.criar_footer()
        
        # Update all lists after creating tabs
        self.atualizar_todas_listas()
    
    def criar_footer(self):
        """Create footer with generate schedule button"""
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill='x', padx=10, pady=5)
        
        # Add a separator above the footer
        separator = ttk.Separator(footer_frame, orient='horizontal')
        separator.pack(fill='x', pady=5)
        
        # Create a container frame for the button to enable centering
        button_container = ttk.Frame(footer_frame)
        button_container.pack(fill='x', pady=10)
        
        # Configure the container for center alignment
        button_container.columnconfigure(0, weight=1)
        
        # Add the generate button with increased size
        style = ttk.Style()
        style.configure('Large.TButton', padding=(20, 10))  # Increase padding for larger button
        
        btn_gerar = ttk.Button(button_container, 
                             text="Gerar Escala", 
                             command=self.abrir_dialog_gerar_escala,
                             style='Large.TButton')
        btn_gerar.grid(row=0, column=0)  # Use grid for center alignment

    def abrir_dialog_gerar_escala(self):
        """Open the generate schedule dialog"""
        dialog = GerarEscalaDialog(self.root, self.gerar_escala)

    def gerar_escala(self, data, semanas):
        """Generate schedule with the selected date and number of weeks"""
        try:
            # Open dialog to select directory and filename
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            nome_arquivo_sugerido = f"escala_{data_obj.strftime('%d_%m_%Y')}.pdf"
            
            caminho_completo = filedialog.asksaveasfilename(
                title="Salvar escala como",
                initialdir=os.getcwd(),
                initialfile=nome_arquivo_sugerido,
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
            )
            
            if not caminho_completo:  # If user cancelled selection
                return
            
            # Generate schedule
            escala.gerar_escala_com_data(data_obj, semanas, caminho_completo)
            messagebox.showinfo("Sucesso", f"Escala gerada com sucesso!\nSalva em: {caminho_completo}")
            
            # Open the PDF
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', caminho_completo])
                elif platform.system() == 'Windows':  # Windows
                    os.startfile(caminho_completo)
                else:  # Linux
                    subprocess.run(['xdg-open', caminho_completo])
            except Exception as e:
                messagebox.showwarning(
                    "Aviso",
                    f"PDF gerado com sucesso, mas não foi possível abri-lo automaticamente.\n"
                    f"O arquivo está salvo em:\n{caminho_completo}"
                )
                
        except ValueError:
            messagebox.showerror("Erro", "Número de semanas inválido")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def atualizar_todas_listas(self):
        """Atualiza todas as listas da interface"""
        self.atualizar_lista_designacoes()
        self.atualizar_lista_pessoas()
        self.atualizar_lista_designacoes_selecao()
        self.atualizar_lista_datas()
    
    def criar_aba_designacoes(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Designações')
        
        # Lista de designações
        frame_lista = ttk.Frame(frame)
        frame_lista.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(frame_lista, text="Designações Cadastradas").pack()
        
        # Criar frame para lista com scrollbar
        list_frame = ttk.Frame(frame_lista)
        list_frame.pack(fill='both', expand=True)
        
        # Criar scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_designacoes = tk.Listbox(list_frame, height=20, 
                                          yscrollcommand=scrollbar.set)
        self.lista_designacoes.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.lista_designacoes.yview)
        
        self.atualizar_lista_designacoes()
        
        # Frame para adicionar/remover
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        
        ttk.Label(frame_botoes, text="Nova Designação:").pack(pady=5)
        self.entry_designacao = ttk.Entry(frame_botoes)
        self.entry_designacao.pack(pady=5)
        self.entry_designacao.bind('<Return>', lambda e: self.adicionar_designacao())
        
        ttk.Button(frame_botoes, text="Adicionar", 
                  command=self.adicionar_designacao).pack(pady=5)
        ttk.Button(frame_botoes, text="Remover Selecionada", 
                  command=self.remover_designacao).pack(pady=5)
    
    def criar_aba_pessoas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Pessoas')
        
        # Lista de pessoas com colunas
        frame_lista = ttk.Frame(frame)
        frame_lista.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(frame_lista, text="Pessoas Cadastradas").pack()
        
        # Criar Treeview com scrollbar
        tree_frame = ttk.Frame(frame_lista)
        tree_frame.pack(fill='both', expand=True)
        
        # Criar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Criar Treeview
        self.lista_pessoas = ttk.Treeview(tree_frame, columns=('nome', 'designacoes'), 
                                        show='headings', selectmode='browse',
                                        yscrollcommand=scrollbar.set)
        
        # Configurar colunas
        self.lista_pessoas.heading('nome', text='Nome')
        self.lista_pessoas.heading('designacoes', text='Designações')
        self.lista_pessoas.column('nome', width=100, minwidth=100, stretch=False)
        self.lista_pessoas.column('designacoes', width=350, minwidth=200)
        
        # Adicionar binding para duplo clique
        self.lista_pessoas.bind('<Double-1>', self.editar_pessoa_selecionada)
        
        self.lista_pessoas.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.lista_pessoas.yview)
        
        # Frame para adicionar/remover pessoas
        frame_cadastro = ttk.Frame(frame)
        frame_cadastro.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        
        ttk.Label(frame_cadastro, text="Nome:").pack(pady=5)
        self.entry_nome = ttk.Entry(frame_cadastro)
        self.entry_nome.pack(pady=5)
        # Adicionar binding para tecla Enter
        self.entry_nome.bind('<Return>', lambda e: self.focar_lista_designacoes())
        
        ttk.Label(frame_cadastro, text="Designações:").pack(pady=5)
        self.lista_designacoes_pessoa = tk.Listbox(frame_cadastro, 
                                                  selectmode=tk.MULTIPLE, 
                                                  height=20)
        self.lista_designacoes_pessoa.pack(pady=5)
        # Adicionar binding para tecla Enter na lista de designações
        self.lista_designacoes_pessoa.bind('<Return>', lambda e: self.adicionar_pessoa())
        self.atualizar_lista_designacoes_selecao()
        
        ttk.Button(frame_cadastro, text="Adicionar Pessoa", 
                  command=self.adicionar_pessoa).pack(pady=5)
        ttk.Button(frame_cadastro, text="Remover Pessoa", 
                  command=self.remover_pessoa).pack(pady=5)
    
    def criar_aba_datas_especiais(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Datas Especiais')
        
        # Lista de datas especiais com colunas
        frame_lista = ttk.Frame(frame)
        frame_lista.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(frame_lista, text="Datas Especiais").pack()
        
        # Criar Treeview com scrollbar
        tree_frame = ttk.Frame(frame_lista)
        tree_frame.pack(fill='both', expand=True)
        
        # Criar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Criar Treeview
        self.lista_datas = ttk.Treeview(tree_frame, columns=('data', 'descricao'), 
                                      show='headings', selectmode='browse',
                                      yscrollcommand=scrollbar.set)
        
        # Configurar colunas
        self.lista_datas.heading('data', text='Data Início')
        self.lista_datas.heading('descricao', text='Descrição')
        self.lista_datas.column('data', width=50, minwidth=50)
        self.lista_datas.column('descricao', width=350, minwidth=200)
        
        self.lista_datas.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.lista_datas.yview)
        
        # Frame para adicionar/remover datas
        frame_cadastro = ttk.Frame(frame)
        frame_cadastro.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        
        ttk.Label(frame_cadastro, text="Data:").pack(pady=5)
        self.cal = Calendar(frame_cadastro, selectmode='day', 
                          date_pattern='dd/mm/yyyy')
        self.cal.pack(pady=5)
        
        ttk.Label(frame_cadastro, text="Evento:").pack(pady=5)
        self.entry_evento = ttk.Entry(frame_cadastro)
        self.entry_evento.pack(pady=5)
        # Adicionar binding para tecla Enter
        self.entry_evento.bind('<Return>', lambda e: self.adicionar_data_especial())
        
        ttk.Button(frame_cadastro, text="Adicionar Data Especial", 
                  command=self.adicionar_data_especial).pack(pady=5)
        ttk.Button(frame_cadastro, text="Remover Data Especial", 
                  command=self.remover_data_especial).pack(pady=5)
    
    # Métodos de atualização das listas
    def atualizar_lista_designacoes(self):
        self.lista_designacoes.delete(0, tk.END)
        for cargo in escala.cargos:
            self.lista_designacoes.insert(tk.END, cargo)
    
    def atualizar_lista_pessoas(self):
        # Limpar lista atual
        for item in self.lista_pessoas.get_children():
            self.lista_pessoas.delete(item)
        
        # Inserir dados atualizados em ordem alfabética
        for nome in sorted(escala.pessoas.keys()):
            cargos = escala.pessoas[nome]
            # Ordenar cargos alfabeticamente
            cargos_ordenados = sorted(cargos)
            self.lista_pessoas.insert('', 'end', values=(nome, ', '.join(cargos_ordenados)))
    
    def atualizar_lista_designacoes_selecao(self):
        self.lista_designacoes_pessoa.delete(0, tk.END)
        for cargo in escala.cargos:
            self.lista_designacoes_pessoa.insert(tk.END, cargo)
    
    def atualizar_lista_datas(self):
        # Limpar lista atual
        for item in self.lista_datas.get_children():
            self.lista_datas.delete(item)
        
        # Inserir dados atualizados
        for data, evento in sorted(escala.datas_especiais.items()):
            self.lista_datas.insert('', 'end', values=(data, evento))
    
    # Métodos de ação
    def adicionar_designacao(self):
        nome = self.entry_designacao.get().strip()
        if nome and nome not in escala.cargos:
            escala.cargos.append(nome)
            escala.salvar_dados()
            self.atualizar_todas_listas()
            self.entry_designacao.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Designação inválida ou já existe")
    
    def remover_designacao(self):
        sel = self.lista_designacoes.curselection()
        if sel:
            cargo = escala.cargos[sel[0]]
            escala.cargos.remove(cargo)
            for p in list(escala.pessoas):
                if cargo in escala.pessoas[p]:
                    escala.pessoas[p].remove(cargo)
            escala.salvar_dados()
            self.atualizar_todas_listas()
    
    def adicionar_pessoa(self):
        nome = self.entry_nome.get().strip()
        sel = self.lista_designacoes_pessoa.curselection()
        if nome and sel:
            # Ordenar cargos alfabeticamente
            cargos_selecionados = sorted([escala.cargos[i] for i in sel])
            escala.pessoas[nome] = cargos_selecionados
            escala.salvar_dados()
            self.atualizar_todas_listas()
            self.entry_nome.delete(0, tk.END)
            self.lista_designacoes_pessoa.selection_clear(0, tk.END)
        else:
            messagebox.showerror("Erro", 
                               "Nome inválido ou nenhuma designação selecionada")
    
    def remover_pessoa(self):
        sel = self.lista_pessoas.selection()
        if sel:
            item = self.lista_pessoas.item(sel[0])
            nome = item['values'][0]
            if nome in escala.pessoas:
                del escala.pessoas[nome]
                escala.salvar_dados()
                self.atualizar_todas_listas()
    
    def atualizar_designacoes_pessoa(self):
        sel_pessoa = self.lista_pessoas.selection()
        sel_designacoes = self.lista_designacoes_pessoa.curselection()
        if sel_pessoa and sel_designacoes:
            item = self.lista_pessoas.item(sel_pessoa[0])
            nome = item['values'][0]
            # Ordenar cargos alfabeticamente
            cargos_selecionados = sorted([escala.cargos[i] for i in sel_designacoes])
            escala.pessoas[nome] = cargos_selecionados
            escala.salvar_dados()
            self.atualizar_todas_listas()
    
    def adicionar_data_especial(self):
        data = self.cal.get_date()
        evento = self.entry_evento.get().strip()
        if evento:
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            data_key = data_obj.strftime("%d/%m")
            escala.datas_especiais[data_key] = evento
            escala.salvar_dados()
            self.atualizar_todas_listas()
            self.entry_evento.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Descrição do evento não pode estar vazia")
    
    def remover_data_especial(self):
        sel = self.lista_datas.selection()
        if sel:
            item = self.lista_datas.item(sel[0])
            data = item['values'][0]
            if data in escala.datas_especiais:
                del escala.datas_especiais[data]
                escala.salvar_dados()
                self.atualizar_todas_listas()
    
    def focar_lista_designacoes(self):
        """Após digitar o nome, foca na lista de designações"""
        self.lista_designacoes_pessoa.focus_set()

    def editar_pessoa_selecionada(self, event=None):
        sel = self.lista_pessoas.selection()
        if not sel:
            return
        
        # Obter dados da pessoa selecionada
        item = self.lista_pessoas.item(sel[0])
        nome = item['values'][0]
        designacoes_atuais = escala.pessoas[nome]
        
        # Criar diálogo de edição
        dialog = EditarPessoaDialog(
            self.root,
            nome,
            designacoes_atuais,
            escala.cargos,
            self.atualizar_todas_listas
        )
        
        # Aguardar o fechamento do diálogo
        self.root.wait_window(dialog.top)

if __name__ == '__main__':
    root = tk.Tk()
    app = EscalaApp(root)
    root.mainloop() 