import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import json
from datetime import datetime, timedelta
import os

class DayScheduleFrame(ttk.LabelFrame):
    def __init__(self, parent, day_name):
        super().__init__(parent, text=day_name)
        self.time_vars = {}
        
        # Create time slots from 07:00 to 19:00
        current_time = 7 * 60  # 07:00 in minutes
        end_time = 19 * 60    # 19:00 in minutes
        
        # Get configuration for slot duration
        try:
            with open('data_tpl/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            duration = config.get('duracao_padrao', 60)
        except:
            duration = 60
            
        # Day enabled checkbox
        self.enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Disponível", 
                       variable=self.enabled_var,
                       command=self.toggle_times).pack(pady=5)
                       
        # Create scrollable frame for time slots
        canvas = tk.Canvas(self, height=150)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.times_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        
        # Create window inside canvas
        canvas.create_window((0, 0), window=self.times_frame, anchor="nw")
        
        # Configure scroll region when frame size changes
        self.times_frame.bind("<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
        # Create time slots
        while current_time + duration <= end_time:
            time_str = f"{current_time//60:02d}:{current_time%60:02d}-{(current_time+duration)//60:02d}:{(current_time+duration)%60:02d}"
            var = tk.BooleanVar(value=False)
            self.time_vars[time_str] = var
            
            cb = ttk.Checkbutton(self.times_frame, text=time_str, variable=var, state='disabled')
            cb.pack(anchor='w')
            
            current_time += duration
            
        self.checkbuttons = self.times_frame.winfo_children()
        
    def toggle_times(self):
        """Enable/disable time checkboxes based on day checkbox"""
        state = 'normal' if self.enabled_var.get() else 'disabled'
        for cb in self.checkbuttons:
            cb.configure(state=state)
            
    def get_selected_times(self):
        """Get list of selected time ranges"""
        if not self.enabled_var.get():
            return []
            
        return [time_str for time_str, var in self.time_vars.items() 
                if var.get()]
                
    def set_times(self, times):
        """Set selected times"""
        if times:
            self.enabled_var.set(True)
            self.toggle_times()
            
            for time_str, var in self.time_vars.items():
                var.set(time_str in times)
        else:
            self.enabled_var.set(False)
            self.toggle_times()

class TPLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Escala TPL")
        self.root.geometry("800x600")
        
        # Ensure data directory exists
        if not os.path.exists('data_tpl'):
            os.makedirs('data_tpl')
            
        # Initialize data files if they don't exist
        self.data_files = {
            'pessoas': 'data_tpl/pessoas.json',
            'carrinhos': 'data_tpl/carrinhos.json',
            'pontos': 'data_tpl/pontos.json',
            'config': 'data_tpl/config.json'
        }
        
        self.initialize_data_files()
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.setup_pessoas_tab()
        self.setup_carrinhos_tab()
        self.setup_pontos_tab()
        self.setup_config_tab()
        
        # Create footer with generate button
        self.setup_footer()
        
    def initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        default_data = {
            'pessoas': [],
            'carrinhos': [],
            'pontos': [],
            'config': {'duracao_padrao': 60}  # duração em minutos
        }
        
        for file_key, file_path in self.data_files.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data[file_key], f, ensure_ascii=False, indent=4)
    
    def setup_pessoas_tab(self):
        """Setup the People management tab"""
        pessoas_frame = ttk.Frame(self.notebook)
        self.notebook.add(pessoas_frame, text='Pessoas')
        
        # Main frame with horizontal split
        main_frame = ttk.Frame(pessoas_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left frame for list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Right frame for preview
        right_frame = ttk.LabelFrame(main_frame, text="Visualização")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_pessoas_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # List frame with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.pessoas_listbox = tk.Listbox(list_frame, selectmode='single')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.pessoas_listbox.yview)
        self.pessoas_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.pessoas_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # Bind events
        self.pessoas_listbox.bind('<Double-Button-1>', lambda e: self.edit_pessoa())
        self.pessoas_listbox.bind('<<ListboxSelect>>', self.show_pessoa_preview)
        self.pessoas_listbox.bind('<Delete>', lambda e: self.delete_pessoa())
        self.pessoas_listbox.bind('<Return>', lambda e: self.new_pessoa())
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Novo", command=self.new_pessoa).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Editar", command=self.edit_pessoa).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Excluir", command=self.delete_pessoa).pack(side='left', padx=2)
        
        # Preview content
        self.pessoa_preview = ttk.Label(right_frame, text="Selecione uma pessoa para visualizar")
        self.pessoa_preview.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Load initial data
        self.load_pessoas()
        
    def show_pessoa_preview(self, event=None):
        """Show preview of selected person"""
        if not self.pessoas_listbox.curselection():
            self.pessoa_preview.config(text="Selecione uma pessoa para visualizar")
            return
            
        nome = self.pessoas_listbox.get(self.pessoas_listbox.curselection())
        pessoa = next((p for p in self.pessoas_data if p['nome'] == nome), None)
        
        if pessoa:
            preview_text = f"""Nome: {pessoa['nome']}
Sexo: {'Masculino' if pessoa['sexo'] == 'M' else 'Feminino'}
Cônjuge: {pessoa.get('spouse', 'Não possui')}

Horários Disponíveis:"""
            
            for day, times in pessoa.get('horarios', {}).items():
                preview_text += f"\n\n{day}:"
                for time in times:
                    preview_text += f"\n  {time}"
                    
            self.pessoa_preview.config(text=preview_text)
        
    def setup_carrinhos_tab(self):
        """Setup the Carts management tab"""
        carrinhos_frame = ttk.Frame(self.notebook)
        self.notebook.add(carrinhos_frame, text='Carrinhos')
        
        # Main frame with horizontal split
        main_frame = ttk.Frame(carrinhos_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left frame for list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Right frame for preview
        right_frame = ttk.LabelFrame(main_frame, text="Visualização")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.carrinho_search_var = tk.StringVar()
        self.carrinho_search_var.trace('w', self.filter_carrinhos_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.carrinho_search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # List frame with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.carrinhos_listbox = tk.Listbox(list_frame, selectmode='single')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.carrinhos_listbox.yview)
        self.carrinhos_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.carrinhos_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # Bind events
        self.carrinhos_listbox.bind('<Double-Button-1>', lambda e: self.edit_carrinho())
        self.carrinhos_listbox.bind('<<ListboxSelect>>', self.show_carrinho_preview)
        self.carrinhos_listbox.bind('<Delete>', lambda e: self.delete_carrinho())
        self.carrinhos_listbox.bind('<Return>', lambda e: self.new_carrinho())
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Novo", command=self.new_carrinho).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Editar", command=self.edit_carrinho).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Excluir", command=self.delete_carrinho).pack(side='left', padx=2)
        
        # Preview content
        self.carrinho_preview = ttk.Label(right_frame, text="Selecione um carrinho para visualizar")
        self.carrinho_preview.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Load initial data
        self.load_carrinhos()
        
    def show_carrinho_preview(self, event=None):
        """Show preview of selected cart"""
        if not self.carrinhos_listbox.curselection():
            self.carrinho_preview.config(text="Selecione um carrinho para visualizar")
            return
            
        nome = self.carrinhos_listbox.get(self.carrinhos_listbox.curselection())
        carrinho = next((c for c in self.carrinhos_data if c['nome'] == nome), None)
        
        if carrinho:
            preview_text = f"""Nome: {carrinho['nome']}

Pontos Vinculados:"""
            
            for ponto in carrinho.get('pontos', []):
                preview_text += f"\n• {ponto}"
                
            self.carrinho_preview.config(text=preview_text)
        
    def setup_pontos_tab(self):
        """Setup the Points management tab"""
        pontos_frame = ttk.Frame(self.notebook)
        self.notebook.add(pontos_frame, text='Pontos')
        
        # Main frame with horizontal split
        main_frame = ttk.Frame(pontos_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left frame for list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Right frame for preview
        right_frame = ttk.LabelFrame(main_frame, text="Visualização")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.ponto_search_var = tk.StringVar()
        self.ponto_search_var.trace('w', self.filter_pontos_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.ponto_search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # List frame with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.pontos_listbox = tk.Listbox(list_frame, selectmode='single')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.pontos_listbox.yview)
        self.pontos_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.pontos_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # Bind events
        self.pontos_listbox.bind('<Double-Button-1>', lambda e: self.edit_ponto())
        self.pontos_listbox.bind('<<ListboxSelect>>', self.show_ponto_preview)
        self.pontos_listbox.bind('<Delete>', lambda e: self.delete_ponto())
        self.pontos_listbox.bind('<Return>', lambda e: self.new_ponto())
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Novo", command=self.new_ponto).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Editar", command=self.edit_ponto).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Excluir", command=self.delete_ponto).pack(side='left', padx=2)
        
        # Preview content
        self.ponto_preview = ttk.Label(right_frame, text="Selecione um ponto para visualizar")
        self.ponto_preview.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Load initial data
        self.load_pontos()
        
    def show_ponto_preview(self, event=None):
        """Show preview of selected point"""
        if not self.pontos_listbox.curselection():
            self.ponto_preview.config(text="Selecione um ponto para visualizar")
            return
            
        nome = self.pontos_listbox.get(self.pontos_listbox.curselection())
        ponto = next((p for p in self.pontos_data if p['nome'] == nome), None)
        
        if ponto:
            preview_text = f"""Nome: {ponto['nome']}

Horários Disponíveis:"""
            
            for day, times in ponto.get('horarios', {}).items():
                preview_text += f"\n\n{day}:"
                for time in times:
                    preview_text += f"\n  {time}"
                    
            self.ponto_preview.config(text=preview_text)
        
    def setup_footer(self):
        """Setup the footer with generate schedule button"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill='x', padx=10, pady=5)
        
        generate_btn = ttk.Button(
            footer_frame,
            text="Gerar Escala",
            command=self.show_generate_dialog,
            style='Large.TButton'
        )
        generate_btn.pack(pady=10)
        
    def load_pessoas(self):
        """Load people from JSON file"""
        try:
            with open(self.data_files['pessoas'], 'r', encoding='utf-8') as f:
                self.pessoas_data = json.load(f)
        except FileNotFoundError:
            self.pessoas_data = []
            
        self.update_pessoas_list()
        
    def update_pessoas_list(self):
        """Update the listbox with filtered people"""
        self.pessoas_listbox.delete(0, tk.END)
        search_term = self.search_var.get().lower()
        
        for pessoa in sorted(self.pessoas_data, key=lambda x: x['nome']):
            if search_term in pessoa['nome'].lower():
                self.pessoas_listbox.insert(tk.END, pessoa['nome'])
                
    def filter_pessoas_list(self, *args):
        """Filter the people list based on search term"""
        self.update_pessoas_list()
        
    def load_carrinhos(self):
        """Load carts from JSON file"""
        try:
            with open(self.data_files['carrinhos'], 'r', encoding='utf-8') as f:
                self.carrinhos_data = json.load(f)
        except FileNotFoundError:
            self.carrinhos_data = []
            
        self.update_carrinhos_list()
        
    def update_carrinhos_list(self):
        """Update the listbox with filtered carts"""
        self.carrinhos_listbox.delete(0, tk.END)
        search_term = self.carrinho_search_var.get().lower()
        
        for carrinho in sorted(self.carrinhos_data, key=lambda x: x['nome']):
            if search_term in carrinho['nome'].lower():
                self.carrinhos_listbox.insert(tk.END, carrinho['nome'])
                
    def filter_carrinhos_list(self, *args):
        """Filter the carts list based on search term"""
        self.update_carrinhos_list()
        
    def load_pontos(self):
        """Load points from JSON file"""
        try:
            with open(self.data_files['pontos'], 'r', encoding='utf-8') as f:
                self.pontos_data = json.load(f)
        except FileNotFoundError:
            self.pontos_data = []
            
        self.update_pontos_list()
        
    def update_pontos_list(self):
        """Update the listbox with filtered points"""
        self.pontos_listbox.delete(0, tk.END)
        search_term = self.ponto_search_var.get().lower()
        
        for ponto in sorted(self.pontos_data, key=lambda x: x['nome']):
            if search_term in ponto['nome'].lower():
                self.pontos_listbox.insert(tk.END, ponto['nome'])
                
    def filter_pontos_list(self, *args):
        """Filter the points list based on search term"""
        self.update_pontos_list()
        
    def save_pessoas_data(self):
        """Save all people data to JSON file"""
        with open(self.data_files['pessoas'], 'w', encoding='utf-8') as f:
            json.dump(self.pessoas_data, f, ensure_ascii=False, indent=4)
        self.update_pessoas_list()
        
    def save_carrinhos_data(self):
        """Save all carts data to JSON file"""
        with open(self.data_files['carrinhos'], 'w', encoding='utf-8') as f:
            json.dump(self.carrinhos_data, f, ensure_ascii=False, indent=4)
        self.update_carrinhos_list()
        
    def save_pontos_data(self):
        """Save all points data to JSON file"""
        with open(self.data_files['pontos'], 'w', encoding='utf-8') as f:
            json.dump(self.pontos_data, f, ensure_ascii=False, indent=4)
        self.update_pontos_list()
        
    def delete_pessoa(self):
        """Delete selected person"""
        if not self.pessoas_listbox.curselection():
            messagebox.showwarning("Aviso", "Selecione uma pessoa para excluir")
            return
            
        nome = self.pessoas_listbox.get(self.pessoas_listbox.curselection())
        if messagebox.askyesno("Confirmar", f"Deseja excluir {nome}?"):
            self.pessoas_data = [p for p in self.pessoas_data if p['nome'] != nome]
            self.save_pessoas_data()
            
    def delete_carrinho(self):
        """Delete selected cart"""
        if not self.carrinhos_listbox.curselection():
            messagebox.showwarning("Aviso", "Selecione um carrinho para excluir")
            return
            
        nome = self.carrinhos_listbox.get(self.carrinhos_listbox.curselection())
        if messagebox.askyesno("Confirmar", f"Deseja excluir o carrinho {nome}?"):
            self.carrinhos_data = [c for c in self.carrinhos_data if c['nome'] != nome]
            self.save_carrinhos_data()
            
    def delete_ponto(self):
        """Delete selected point"""
        if not self.pontos_listbox.curselection():
            messagebox.showwarning("Aviso", "Selecione um ponto para excluir")
            return
            
        nome = self.pontos_listbox.get(self.pontos_listbox.curselection())
        if messagebox.askyesno("Confirmar", f"Deseja excluir o ponto {nome}?"):
            self.pontos_data = [p for p in self.pontos_data if p['nome'] != nome]
            self.save_pontos_data()

    def setup_config_tab(self):
        """Setup the Configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text='Configurações')
        
        # Main content
        content = ttk.Frame(config_frame)
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Duration configuration
        duration_frame = ttk.LabelFrame(content, text="Duração Padrão das Escalas")
        duration_frame.pack(fill='x', pady=10)
        
        # Hours and minutes
        time_frame = ttk.Frame(duration_frame)
        time_frame.pack(pady=10)
        
        ttk.Label(time_frame, text="Horas:").pack(side='left', padx=5)
        self.duration_hours = ttk.Spinbox(time_frame, from_=0, to=12, width=3)
        self.duration_hours.pack(side='left', padx=5)
        
        ttk.Label(time_frame, text="Minutos:").pack(side='left', padx=5)
        self.duration_minutes = ttk.Spinbox(time_frame, from_=0, to=59, width=3)
        self.duration_minutes.pack(side='left', padx=5)
        
        # Save button
        ttk.Button(duration_frame, text="Salvar Configurações",
                  command=self.save_config).pack(pady=10)
        
        # Load current config
        self.load_config()
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.data_files['config'], 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Convert minutes to hours and minutes
            total_minutes = config.get('duracao_padrao', 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            self.duration_hours.set(hours)
            self.duration_minutes.set(minutes)
        except FileNotFoundError:
            # Set defaults
            self.duration_hours.set(1)
            self.duration_minutes.set(0)
            
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            hours = int(self.duration_hours.get())
            minutes = int(self.duration_minutes.get())
            
            if hours == 0 and minutes == 0:
                messagebox.showwarning("Aviso", "A duração não pode ser zero")
                return
                
            total_minutes = (hours * 60) + minutes
            
            config = {
                'duracao_padrao': total_minutes
            }
            
            with open(self.data_files['config'], 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos para duração")

    def show_generate_dialog(self):
        """Show dialog for generating schedule"""
        # Validate if there are carts with points
        if not any(len(c.get('pontos', [])) > 0 for c in self.carrinhos_data):
            messagebox.showwarning(
                "Aviso",
                "Não há carrinhos com pontos vinculados. Por favor, vincule pontos aos carrinhos antes de gerar a escala."
            )
            return
            
        # Validate if points have schedules
        pontos_sem_horario = []
        for carrinho in self.carrinhos_data:
            for ponto_nome in carrinho.get('pontos', []):
                ponto = next((p for p in self.pontos_data if p['nome'] == ponto_nome), None)
                if not ponto or not ponto.get('horarios'):
                    pontos_sem_horario.append(ponto_nome)
                    
        if pontos_sem_horario:
            messagebox.showwarning(
                "Aviso",
                f"Os seguintes pontos não têm horários cadastrados:\n\n{', '.join(pontos_sem_horario)}\n\nPor favor, cadastre os horários antes de gerar a escala."
            )
            return
            
        # Validate if there are available people
        if not self.pessoas_data:
            messagebox.showwarning(
                "Aviso",
                "Não há pessoas cadastradas. Por favor, cadastre pessoas antes de gerar a escala."
            )
            return
            
        # Create the dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Gerar Escala")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("400x300")
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = ttk.Frame(dialog, padding="20")
        content.pack(fill='both', expand=True)
        
        # Date selection
        date_frame = ttk.Frame(content)
        date_frame.pack(fill='x', pady=10)
        
        ttk.Label(date_frame, text="Data Inicial:").pack(side='left', padx=5)
        self.start_date = DateEntry(date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.pack(side='left', padx=5)
        
        # Weeks selection
        weeks_frame = ttk.Frame(content)
        weeks_frame.pack(fill='x', pady=10)
        
        ttk.Label(weeks_frame, text="Número de Semanas:").pack(side='left', padx=5)
        self.num_weeks = ttk.Spinbox(weeks_frame, from_=1, to=52, width=3)
        self.num_weeks.set(4)  # Default to 4 weeks
        self.num_weeks.pack(side='left', padx=5)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(content, text="Resumo", padding="10")
        summary_frame.pack(fill='x', pady=10)
        
        # Add summary information
        summary_text = f"""
Carrinhos com pontos: {sum(1 for c in self.carrinhos_data if c.get('pontos'))}
Total de pontos: {len(self.pontos_data)}
Total de pessoas: {len(self.pessoas_data)}
"""
        ttk.Label(summary_frame, text=summary_text.strip()).pack()
        
        # Buttons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill='x', pady=20)
        
        ttk.Button(btn_frame, text="Gerar",
                  command=lambda: self.generate_schedule(dialog)).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar",
                  command=dialog.destroy).pack(side='right')
        
    def generate_schedule(self, dialog):
        """Generate the schedule"""
        try:
            # Get and validate the date
            start_date = self.start_date.get_date()
            if not start_date:
                messagebox.showwarning("Aviso", "Selecione uma data válida")
                return
                
            # Get and validate number of weeks
            try:
                num_weeks = int(self.num_weeks.get())
                if num_weeks < 1:
                    messagebox.showwarning("Aviso", "O número de semanas deve ser maior que zero")
                    return
            except ValueError:
                messagebox.showwarning("Aviso", "Número de semanas inválido")
                return
                
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Salvar Escala"
            )
            
            if not filename:
                return
                
            # Close the dialog
            dialog.destroy()
            
            # Generate the schedule
            try:
                self.create_schedule_pdf(filename, start_date, num_weeks)
                
                # Show success message
                messagebox.showinfo("Sucesso", "Escala gerada com sucesso!")
                
                # Open the generated file
                os.startfile(filename)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            
    def split_time_range(self, time_range, duration_minutes):
        """Split a time range into slots based on duration"""
        start, end = time_range.split('-')
        start_minutes = self.time_to_minutes(start)
        end_minutes = self.time_to_minutes(end)
        
        slots = []
        current = start_minutes
        while current + duration_minutes <= end_minutes:
            slot_end = current + duration_minutes
            slots.append(f"{self.minutes_to_time(current)}-{self.minutes_to_time(slot_end)}")
            current = slot_end
            
        return slots
        
    def time_to_minutes(self, time_str):
        """Convert time string (HH:MM) to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
        
    def minutes_to_time(self, minutes):
        """Convert minutes since midnight to time string (HH:MM)"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
        
    def get_time_range_minutes(self, time_range):
        """Get start and end times in minutes for a time range"""
        start, end = time_range.split('-')
        return (self.time_to_minutes(start), self.time_to_minutes(end))
        
    def is_cart_available(self, cart_name, time_slot, cart_times_used):
        """Check if cart is available for the given time slot"""
        start_time, end_time = self.get_time_range_minutes(time_slot)
        
        # Check against all used time slots for this cart
        for used_start, used_end in cart_times_used.get(cart_name, []):
            if not (end_time <= used_start or start_time >= used_end):
                return False
                
        return True
        
    def find_available_people(self, day, time_range):
        """Find people available for the given day and time"""
        available = []
        
        if not time_range or '-' not in time_range:
            return available
            
        for pessoa in self.pessoas_data:
            horarios = pessoa.get('horarios', {}).get(day, [])
            
            # Check if person is available at this time
            for horario in horarios:
                try:
                    if self.time_ranges_overlap(horario, time_range):
                        available.append(pessoa)
                        break
                except ValueError:
                    # Skip invalid time ranges
                    continue
                    
        return available
        
    def time_ranges_overlap(self, range1, range2):
        """Check if two time ranges overlap"""
        try:
            start1, end1 = range1.split('-')
            start2, end2 = range2.split('-')
            
            # Convert to minutes since midnight
            start1 = self.time_to_minutes(start1)
            end1 = self.time_to_minutes(end1)
            start2 = self.time_to_minutes(start2)
            end2 = self.time_to_minutes(end2)
            
            return not (end1 <= start2 or end2 <= start1)
        except Exception as e:
            raise ValueError(f"Invalid time range format: {str(e)}")
        
    def create_balanced_pairs(self, people, designation_counts):
        """Create pairs of people following the rules and balancing designations"""
        if not people:
            return []
            
        # Sort people by number of designations (ascending)
        sorted_people = sorted(people, key=lambda p: designation_counts[p['nome']])
        
        pairs = []
        used = set()
        
        # First try to find a spouse pair among least designated people
        for person in sorted_people:
            if person['nome'] in used:
                continue
                
            if person.get('has_spouse'):
                spouse_name = person.get('spouse')
                spouse = next((p for p in sorted_people 
                             if p['nome'] == spouse_name 
                             and p['nome'] not in used), None)
                if spouse:
                    # Check if this pair has significantly more designations than others
                    avg_designations = sum(designation_counts.values()) / len(designation_counts)
                    pair_designations = (designation_counts[person['nome']] + 
                                       designation_counts[spouse['nome']]) / 2
                    
                    if pair_designations <= avg_designations + 2:  # Allow some variance
                        pairs.append((person, spouse))
                        used.add(person['nome'])
                        used.add(spouse['nome'])
                        return pairs
                    
        # If no suitable spouse pair found, try to pair same sex with balanced designations
        for i, person1 in enumerate(sorted_people):
            if person1['nome'] in used:
                continue
                
            # Find another person of the same sex with similar designation count
            for person2 in sorted_people[i+1:]:
                if (person2['nome'] not in used and 
                    person2['sexo'] == person1['sexo'] and
                    abs(designation_counts[person1['nome']] - 
                        designation_counts[person2['nome']]) <= 2):
                    pairs.append((person1, person2))
                    used.add(person1['nome'])
                    used.add(person2['nome'])
                    return pairs
                    
        # If no balanced pair found but we have one person, return the least designated person
        if sorted_people:
            pairs.append((sorted_people[0], None))
            used.add(sorted_people[0]['nome'])
            
        return pairs
        
    def create_schedule_pdf(self, filename, start_date, num_weeks):
        """Create the schedule PDF file"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        
        # Validate inputs
        if not self.carrinhos_data:
            raise ValueError("Não há carrinhos cadastrados")
            
        # Load configuration
        try:
            with open(self.data_files['config'], 'r', encoding='utf-8') as f:
                config = json.load(f)
            duration_minutes = config.get('duracao_padrao', 60)
        except FileNotFoundError:
            duration_minutes = 60
            
        # Initialize designation counters
        designation_counts = {pessoa['nome']: 0 for pessoa in self.pessoas_data}
            
        # Create document
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        cor_borda = colors.HexColor('#999898')
        cor_cabecalho = colors.HexColor('#d9d9d9')
        cor_titulo = colors.HexColor('#4a6da7')
        
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  
            spaceAfter=0,
            textColor=colors.white,  
            leading=20
        )
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=1,  
            spaceAfter=0,
            textColor=colors.white,  
            leading=5
        )
        
        dia_style = ParagraphStyle(
            'DayTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.black,
            alignment=1,  # Center alignment
            spaceAfter=0,
            spaceBefore=20
        )
        
        # Create title with colored background
        titulo = Paragraph("<b>Congregação Coqueiros</b>", titulo_style)
        titulo_table = Table([[titulo]], colWidths=[doc.width])
        titulo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cor_titulo),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(titulo_table)
        
        # Create subtitle with colored background
        subtitulo = Paragraph("<b>Escala de Carrinho</b>", subtitulo_style)
        subtitulo_table = Table([[subtitulo]], colWidths=[doc.width])
        subtitulo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cor_titulo),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        elements.append(subtitulo_table)
        elements.append(Spacer(1, 5))
        
        # Generate schedule for all days
        current_date = start_date
        for week in range(num_weeks):  # For each week
            for day in range(7):  # For each day of the week
                weekday = current_date.weekday()
                day_name = ['Segunda', 'Terça', 'Quarta', 'Quinta', 
                           'Sexta', 'Sábado', 'Domingo'][weekday]
                
                # Create data structure for this day
                day_data = []  # List of [horario, carrinho, ponto, pessoa1, pessoa2]
                
                # Track used cart times to prevent conflicts
                cart_times_used = {}  # Format: {cart_name: [(start_time, end_time)]}
                
                # For each cart
                for carrinho in self.carrinhos_data:
                    cart_name = carrinho['nome']
                    cart_times_used[cart_name] = []
                    
                    # Get points for this cart
                    pontos = [p for p in self.pontos_data if p['nome'] in carrinho['pontos']]
                    
                    # For each point
                    for ponto in pontos:
                        # Get available times for this day
                        horarios = ponto.get('horarios', {}).get(day_name, [])
                        
                        # Split time ranges according to duration_minutes
                        for horario in horarios:
                            time_slots = self.split_time_range(horario, duration_minutes)
                            
                            for time_slot in time_slots:
                                # Check if cart is already being used at this time
                                if self.is_cart_available(cart_name, time_slot, cart_times_used):
                                    # Find available people
                                    pessoas_disponiveis = self.find_available_people(
                                        day_name, time_slot)
                                    
                                    # Create pairs considering designation counts
                                    pares = self.create_balanced_pairs(pessoas_disponiveis, designation_counts)
                                    
                                    # If no pairs available
                                    if not pares:
                                        if pessoas_disponiveis:  # If there's one person available
                                            # Get the person with least designations
                                            pessoa = min(pessoas_disponiveis, 
                                                       key=lambda p: designation_counts[p['nome']])
                                            day_data.append([
                                                time_slot,
                                                cart_name,
                                                ponto['nome'],
                                                pessoa['nome'],
                                                '?'
                                            ])
                                            designation_counts[pessoa['nome']] += 1
                                        else:  # If no one is available
                                            day_data.append([
                                                time_slot,
                                                cart_name,
                                                ponto['nome'],
                                                '-',
                                                '-'
                                            ])
                                    else:
                                        # Add a row for each pair
                                        for pessoa1, pessoa2 in pares:
                                            day_data.append([
                                                time_slot,
                                                cart_name,
                                                ponto['nome'],
                                                pessoa1['nome'] if pessoa1 else '-',
                                                pessoa2['nome'] if pessoa2 else '?'
                                            ])
                                            # Update designation counts
                                            if pessoa1:
                                                designation_counts[pessoa1['nome']] += 1
                                            if pessoa2:
                                                designation_counts[pessoa2['nome']] += 1
                                            
                                    # Mark this time slot as used for this cart
                                    start_time, end_time = self.get_time_range_minutes(time_slot)
                                    cart_times_used[cart_name].append((start_time, end_time))
                
                # Sort day_data by cart name and then by time
                day_data.sort(key=lambda x: (x[1], x[0]))
                
                if day_data:  # Only create table if there are designations for this day
                    # Add day title
                    dia_titulo = Paragraph(f"<b>{day_name} - {current_date.strftime('%d/%m/%Y')}</b>", dia_style)
                    elements.append(dia_titulo)
                    elements.append(Spacer(1, 5))
                    
                    # Create table for this day
                    headers = ['Horário', 'Carrinho', 'Ponto', 'Pessoa 1', 'Pessoa 2']
                    table_data = [headers] + day_data
                    
                    # Create table
                    table = Table(table_data, colWidths=[2.5*cm, 3.5*cm, 7*cm, 3.5*cm, 3.5*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9d9d9')),  # Header background
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#999898')),  # Border color
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    
                    elements.append(table)
                
                current_date += timedelta(days=1)
        
        try:
            # Build document
            doc.build(elements)
        except Exception as e:
            raise Exception(f"Erro ao gerar o arquivo PDF: {str(e)}")

    def show_pessoa_dialog(self, pessoa=None):
        """Show dialog for creating/editing a person"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova Pessoa" if pessoa is None else "Editar Pessoa")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("600x600")  # Increased height
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main content
        content = ttk.Frame(dialog, padding="20")
        content.pack(fill='both', expand=True)
        
        # Basic info
        basic_frame = ttk.LabelFrame(content, text="Informações Básicas", padding=10)
        basic_frame.pack(fill='x', pady=5)
        
        # Nome
        nome_frame = ttk.Frame(basic_frame)
        nome_frame.pack(fill='x', pady=5)
        ttk.Label(nome_frame, text="Nome:").pack(side='left', padx=5)
        nome_var = tk.StringVar(value=pessoa['nome'] if pessoa else '')
        nome_entry = ttk.Entry(nome_frame, textvariable=nome_var)
        nome_entry.pack(side='left', fill='x', expand=True)
        
        # Sexo
        sexo_frame = ttk.Frame(basic_frame)
        sexo_frame.pack(fill='x', pady=5)
        ttk.Label(sexo_frame, text="Sexo:").pack(side='left', padx=5)
        sexo_var = tk.StringVar(value=pessoa['sexo'] if pessoa else '')
        ttk.Radiobutton(sexo_frame, text="Masculino", variable=sexo_var, 
                       value="M").pack(side='left', padx=5)
        ttk.Radiobutton(sexo_frame, text="Feminino", variable=sexo_var, 
                       value="F").pack(side='left', padx=5)
        
        # Spouse info
        spouse_frame = ttk.LabelFrame(content, text="Informações do Cônjuge", padding=10)
        spouse_frame.pack(fill='x', pady=5)
        
        has_spouse_var = tk.BooleanVar(value=pessoa.get('has_spouse', False) if pessoa else False)
        ttk.Checkbutton(spouse_frame, text="Possui cônjuge", 
                       variable=has_spouse_var).pack(side='left', padx=5)  # Aligned left
        
        spouse_select_frame = ttk.Frame(spouse_frame)
        spouse_var = tk.StringVar(value=pessoa.get('spouse', '') if pessoa else '')
        
        def toggle_spouse(*args):
            if has_spouse_var.get():
                spouse_select_frame.pack(fill='x', pady=5)
            else:
                spouse_select_frame.pack_forget()
                spouse_var.set('')
                
        has_spouse_var.trace('w', toggle_spouse)
        
        ttk.Label(spouse_select_frame, text="Selecione o cônjuge:").pack(side='left', padx=5)
        spouse_combo = ttk.Combobox(spouse_select_frame, textvariable=spouse_var)
        spouse_combo.pack(side='left', fill='x', expand=True, padx=5)
        
        # Update spouse list
        available_spouses = [p['nome'] for p in self.pessoas_data 
                           if p['nome'] != (pessoa['nome'] if pessoa else None)]
        spouse_combo['values'] = available_spouses
        
        # Schedule frame
        schedule_frame = ttk.LabelFrame(content, text="Disponibilidade", padding=10)
        schedule_frame.pack(fill='both', expand=True, pady=5)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(schedule_frame)
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create day frames
        day_frames = {}
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for day in days:
            day_frames[day] = DayScheduleFrame(scrollable_frame, day)
            day_frames[day].pack(fill='x', pady=2)
            
        # Load schedules if editing
        if pessoa:
            for day, frame in day_frames.items():
                times = pessoa.get('horarios', {}).get(day, [])
                if times:
                    frame.enabled_var.set(True)
                    frame.toggle_times()
                    for time_str, var in frame.time_vars.items():
                        var.set(time_str in times)
                        
        # Buttons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill='x', pady=10)
        
        def save():
            # Validate
            if not nome_var.get().strip():
                messagebox.showwarning("Aviso", "O nome é obrigatório")
                return
                
            if not sexo_var.get():
                messagebox.showwarning("Aviso", "Selecione o sexo")
                return
                
            if has_spouse_var.get() and not spouse_var.get():
                messagebox.showwarning("Aviso", "Selecione o cônjuge")
                return
                
            # Create person data
            new_pessoa = {
                'nome': nome_var.get().strip(),
                'sexo': sexo_var.get(),
                'has_spouse': has_spouse_var.get(),
                'horarios': {}
            }
            
            if has_spouse_var.get():
                new_pessoa['spouse'] = spouse_var.get()
                
            # Save schedules
            for day, frame in day_frames.items():
                times = frame.get_selected_times()
                if times:
                    new_pessoa['horarios'][day] = times
                    
            # Update or add person
            if pessoa:  # Editing
                idx = next((i for i, p in enumerate(self.pessoas_data) 
                          if p['nome'] == pessoa['nome']), None)
                if idx is not None:
                    self.pessoas_data[idx] = new_pessoa
            else:  # New person
                self.pessoas_data.append(new_pessoa)
                
            # Update spouse's record if needed
            if new_pessoa['has_spouse']:
                spouse_idx = next((i for i, p in enumerate(self.pessoas_data) 
                                 if p['nome'] == new_pessoa['spouse']), None)
                if spouse_idx is not None:
                    spouse_data = self.pessoas_data[spouse_idx].copy()
                    spouse_data['has_spouse'] = True
                    spouse_data['spouse'] = new_pessoa['nome']
                    self.pessoas_data[spouse_idx] = spouse_data
                    
            # Remove old spouse relationship if needed
            if pessoa and pessoa.get('has_spouse'):
                old_spouse = pessoa.get('spouse')
                if (old_spouse and 
                    (not new_pessoa['has_spouse'] or 
                     new_pessoa['spouse'] != old_spouse)):
                    old_spouse_idx = next((i for i, p in enumerate(self.pessoas_data) 
                                         if p['nome'] == old_spouse), None)
                    if old_spouse_idx is not None:
                        self.pessoas_data[old_spouse_idx]['has_spouse'] = False
                        self.pessoas_data[old_spouse_idx].pop('spouse', None)
                        
            self.save_pessoas_data()
            dialog.destroy()
            
        ttk.Button(btn_frame, text="Salvar", command=save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=dialog.destroy).pack(side='right')
        
        # Initial state
        toggle_spouse()
        
        # Cleanup on close
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
    def new_pessoa(self):
        """Create a new person"""
        self.show_pessoa_dialog()
        
    def edit_pessoa(self):
        """Edit selected person"""
        if not self.pessoas_listbox.curselection():
            messagebox.showwarning("Aviso", "Selecione uma pessoa para editar")
            return
            
        nome = self.pessoas_listbox.get(self.pessoas_listbox.curselection())
        pessoa = next((p for p in self.pessoas_data if p['nome'] == nome), None)
        if pessoa:
            self.show_pessoa_dialog(pessoa)
            
    def show_carrinho_dialog(self, carrinho=None):
        """Show dialog for creating/editing a cart"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Carrinho" if carrinho is None else "Editar Carrinho")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("600x600")  # Increased height
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main content
        content = ttk.Frame(dialog, padding="20")
        content.pack(fill='both', expand=True)
        
        # Basic info
        basic_frame = ttk.LabelFrame(content, text="Informações Básicas", padding=10)
        basic_frame.pack(fill='x', pady=5)
        
        # Nome
        nome_frame = ttk.Frame(basic_frame)
        nome_frame.pack(fill='x', pady=5)
        ttk.Label(nome_frame, text="Nome:").pack(side='left', padx=5)
        nome_var = tk.StringVar(value=carrinho['nome'] if carrinho else '')
        nome_entry = ttk.Entry(nome_frame, textvariable=nome_var)
        nome_entry.pack(side='left', fill='x', expand=True)
        
        # Points frame
        points_frame = ttk.LabelFrame(content, text="Pontos Vinculados", padding=10)
        points_frame.pack(fill='both', expand=True, pady=5)
        
        # Create points selection frame
        points_select_frame = ttk.Frame(points_frame)
        points_select_frame.pack(fill='x', pady=5)
        
        # Available points listbox
        available_frame = ttk.LabelFrame(points_frame, text="Pontos Disponíveis")
        available_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        available_listbox = tk.Listbox(available_frame, selectmode='extended')
        available_scrollbar = ttk.Scrollbar(available_frame, orient="vertical",
                                          command=available_listbox.yview)
        available_listbox.configure(yscrollcommand=available_scrollbar.set)
        
        available_listbox.pack(side='left', fill='both', expand=True)
        available_scrollbar.pack(side='left', fill='y')
        
        # Selected points listbox
        selected_frame = ttk.LabelFrame(points_frame, text="Pontos Selecionados")
        selected_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        selected_listbox = tk.Listbox(selected_frame, selectmode='extended')
        selected_scrollbar = ttk.Scrollbar(selected_frame, orient="vertical",
                                         command=selected_listbox.yview)
        selected_listbox.configure(yscrollcommand=selected_scrollbar.set)
        
        selected_listbox.pack(side='left', fill='both', expand=True)
        selected_scrollbar.pack(side='left', fill='y')
        
        # Buttons frame
        btn_frame = ttk.Frame(points_frame)
        btn_frame.pack(fill='x', pady=10)
        
        def add_points():
            selections = available_listbox.curselection()
            for i in reversed(selections):
                point = available_listbox.get(i)
                selected_listbox.insert(tk.END, point)
                available_listbox.delete(i)
                
        def remove_points():
            selections = selected_listbox.curselection()
            for i in reversed(selections):
                point = selected_listbox.get(i)
                available_listbox.insert(tk.END, point)
                selected_listbox.delete(i)
                
        ttk.Button(btn_frame, text="Adicionar >>",
                  command=add_points).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="<< Remover",
                  command=remove_points).pack(side='left')
        
        # Load points
        all_points = sorted([p['nome'] for p in self.pontos_data])
        selected_points = carrinho['pontos'] if carrinho else []
        
        for point in all_points:
            if point in selected_points:
                selected_listbox.insert(tk.END, point)
            else:
                available_listbox.insert(tk.END, point)
                
        # Dialog buttons
        dialog_btn_frame = ttk.Frame(content)
        dialog_btn_frame.pack(fill='x', pady=10)
        
        def save():
            # Validate
            if not nome_var.get().strip():
                messagebox.showwarning("Aviso", "O nome do carrinho é obrigatório")
                return
                
            pontos = list(selected_listbox.get(0, tk.END))
            if not pontos:
                messagebox.showwarning("Aviso", "Selecione pelo menos um ponto")
                return
                
            # Create cart data
            new_carrinho = {
                'nome': nome_var.get().strip(),
                'pontos': pontos
            }
            
            # Update or add cart
            if carrinho:  # Editing
                idx = next((i for i, c in enumerate(self.carrinhos_data) 
                          if c['nome'] == carrinho['nome']), None)
                if idx is not None:
                    self.carrinhos_data[idx] = new_carrinho
            else:  # New cart
                self.carrinhos_data.append(new_carrinho)
                
            self.save_carrinhos_data()
            dialog.destroy()
            
        ttk.Button(dialog_btn_frame, text="Salvar",
                  command=save).pack(side='right', padx=5)
        ttk.Button(dialog_btn_frame, text="Cancelar",
                  command=dialog.destroy).pack(side='right')
        
    def new_carrinho(self):
        """Create a new cart"""
        self.show_carrinho_dialog()
        
    def edit_carrinho(self):
        """Edit selected cart"""
        if not self.carrinhos_listbox.curselection():
            messagebox.showwarning("Aviso", "Selecione um carrinho para editar")
            return
            
        nome = self.carrinhos_listbox.get(self.carrinhos_listbox.curselection())
        carrinho = next((c for c in self.carrinhos_data if c['nome'] == nome), None)
        if carrinho:
            self.show_carrinho_dialog(carrinho)
            
    def show_ponto_dialog(self, ponto=None):
        """Show dialog for creating/editing a point"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Ponto" if ponto is None else "Editar Ponto")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("600x600")  # Increased height
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main content
        content = ttk.Frame(dialog, padding="20")
        content.pack(fill='both', expand=True)
        
        # Basic info
        basic_frame = ttk.LabelFrame(content, text="Informações Básicas", padding=10)
        basic_frame.pack(fill='x', pady=5)
        
        # Nome
        nome_frame = ttk.Frame(basic_frame)
        nome_frame.pack(fill='x', pady=5)
        ttk.Label(nome_frame, text="Nome:").pack(side='left', padx=5)
        nome_var = tk.StringVar(value=ponto['nome'] if ponto else '')
        nome_entry = ttk.Entry(nome_frame, textvariable=nome_var)
        nome_entry.pack(side='left', fill='x', expand=True)
        
        # Schedule frame
        schedule_frame = ttk.LabelFrame(content, text="Horários Disponíveis", padding=10)
        schedule_frame.pack(fill='both', expand=True, pady=5)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(schedule_frame)
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create day frames
        day_frames = {}
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for day in days:
            day_frames[day] = DayScheduleFrame(scrollable_frame, day)
            day_frames[day].pack(fill='x', pady=2)
            
        # Load schedules if editing
        if ponto:
            for day, frame in day_frames.items():
                times = ponto.get('horarios', {}).get(day, [])
                if times:
                    frame.enabled_var.set(True)
                    frame.toggle_times()
                    for time_str, var in frame.time_vars.items():
                        var.set(time_str in times)
                        
        # Buttons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill='x', pady=10)
        
        def save():
            # Validate
            if not nome_var.get().strip():
                messagebox.showwarning("Aviso", "O nome do ponto é obrigatório")
                return
                
            # Create point data
            new_ponto = {
                'nome': nome_var.get().strip(),
                'horarios': {}
            }
            
            # Save schedules
            for day, frame in day_frames.items():
                times = frame.get_selected_times()
                if times:
                    new_ponto['horarios'][day] = times
                    
            # Update or add point
            if ponto:  # Editing
                idx = next((i for i, p in enumerate(self.pontos_data) 
                          if p['nome'] == ponto['nome']), None)
                if idx is not None:
                    self.pontos_data[idx] = new_ponto
            else:  # New point
                self.pontos_data.append(new_ponto)
                
            self.save_pontos_data()
            dialog.destroy()
            
        ttk.Button(btn_frame, text="Salvar", command=save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=dialog.destroy).pack(side='right')
                  
        # Cleanup on close
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
    def new_ponto(self):
        """Create a new point"""
        self.show_ponto_dialog()
        
    def edit_ponto(self):
        """Edit selected point"""
        if not self.pontos_listbox.curselection():
            messagebox.showwarning("Aviso", "Selecione um ponto para editar")
            return
            
        nome = self.pontos_listbox.get(self.pontos_listbox.curselection())
        ponto = next((p for p in self.pontos_data if p['nome'] == nome), None)
        if ponto:
            self.show_ponto_dialog(ponto) 