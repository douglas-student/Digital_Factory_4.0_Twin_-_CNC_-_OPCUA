import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk
import json
import os
import shutil  # Agrupado com outras bibliotecas padrão
import subprocess
import sys
import threading
import time

from PIL import Image, ImageTk

# Define os comandos de terminal mais comuns (para Linux e Windows)
TERMINAL_COMMANDS = {
    "Auto-Detect (OS Default)": "default",
    "Windows CMD (cmd /k)": "cmd",
    "Linux: Konsole": "konsole",
    "Linux: Gnome-Terminal": "gnome-terminal",
    "Linux: XTerm": "xterm",
}

class DockerManagerGUI:
    """
    Interface Gráfica Tkinter para gerenciamento de contêineres Docker e execução de scripts do projeto.
    Utiliza threads para manter a responsividade da GUI durante a execução de subprocessos.
    """
    CONTAINER_HEIGHT = 300
    IMAGE_FILENAME = "gui-header-tkinter-app.png"
    CONFIG_FILE = ".terminal_config.json"

    def __init__(self, master):
        self.master = master
        master.title("Gerenciador Docker - Projeto Integrador 6")
        
        try:
            master.state('zoomed') 
        except tk.TclError:
            master.attributes('-fullscreen', True) 

        # CORREÇÃO CRÍTICA: Usa rowconfigure/columnconfigure na raiz (master)
        # O Tkinter usa esta sintaxe, sem o prefixo 'grid_', para o widget Tkapp.
        master.rowconfigure(0, weight=1) 
        master.columnconfigure(0, weight=1) 
        
        self.main_frame = tk.Frame(master)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configuração do grid interno do self.main_frame
        self.main_frame.grid_rowconfigure(0, weight=0) # Linha 0: Área 1 (Imagem)
        self.main_frame.grid_rowconfigure(1, weight=0) # Linha 1: Novo Título Separado
        self.main_frame.grid_rowconfigure(2, weight=0) # Linha 2: Área 2 (Botões)
        self.main_frame.grid_rowconfigure(3, weight=1) # Linha 3: Área 3 (Terminal)
        
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        self.terminal_choice = tk.StringVar() 
        self._load_configuration()
        
        self.create_widgets()
        self.update_container_list_periodically()
        
        master.bind('<Configure>', self.handle_resize)

    def _load_configuration(self):
        """Carrega a configuração do terminal salvo anteriormente."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                try:
                    config = json.load(f)
                    self.terminal_choice.set(config.get('terminal', 'Auto-Detect (OS Default)'))
                except json.JSONDecodeError:
                    self.terminal_choice.set('Auto-Detect (OS Default)')
        else:
            self.terminal_choice.set('Auto-Detect (OS Default)')
            
    def save_configuration(self):
        """Salva a configuração atual do terminal."""
        config = {'terminal': self.terminal_choice.get()}
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def handle_resize(self, event):
        """Lida com o redimensionamento da imagem na Área 1 para 100% de largura."""
        if event.widget == self.master:
            self.master.after(100, lambda: self.update_image_display(self.master.winfo_width()))

    def update_image_display(self, target_width):
        """Redimensiona a imagem para a largura total do container e a recorta na altura fixa."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "static", self.IMAGE_FILENAME)
            original_image = Image.open(image_path)
            
            width, height = original_image.size
            ratio = target_width / width
            new_height = int(height * ratio)

            resized_image = original_image.resize((target_width, new_height), Image.LANCZOS)
            
            cropped_image = resized_image.crop((0, 0, target_width, self.CONTAINER_HEIGHT))

            self.tk_image = ImageTk.PhotoImage(cropped_image)
            self.img_label.config(image=self.tk_image)
            self.img_label.image = self.tk_image 
            
        except FileNotFoundError:
            self.img_label.config(text="[Imagem não encontrada]")
        except Exception:
            self.img_label.config(text="[Erro ao processar imagem]")

    def create_widgets(self):
        """Inicializa todos os componentes visuais da GUI."""
        # --- Área 1: Figura (100% largura, 300px altura fixa) ---
        self.frame_figure = tk.Frame(self.main_frame, bg="#343a40", height=self.CONTAINER_HEIGHT)
        self.frame_figure.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5, padx=5)
        self.frame_figure.grid_propagate(False) # Mantém a altura fixa

        # Canvas para segurar o Label da imagem e garantir o posicionamento
        self.canvas_image = tk.Canvas(self.frame_figure, bg="#343a40", bd=0, highlightthickness=0)
        self.canvas_image.pack(fill=tk.BOTH, expand=True)
        
        # O Label da imagem deve usar a cor de fundo do Canvas
        self.img_label = tk.Label(self.canvas_image, bg="#343a40")
        self.canvas_image.create_window(0, 0, window=self.img_label, anchor=tk.NW)

        # Atualiza a imagem inicial (será ajustada pelo resize handler)
        self.master.after(100, lambda: self.update_image_display(self.master.winfo_width()))
        
        # --- Linha de Título Separada ---
        self.frame_title = tk.Frame(self.main_frame, bg="#000000") # Fundo preto
        self.frame_title.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        
        tk.Label(self.frame_title, 
                 text="PAINEL DE GERENCIAMENTO DOCKER", 
                 fg="white", 
                 bg="#000000",
                 font=("Arial", 14, "bold")).pack(pady=5) # Centraliza o título com padding

        # --- Área 2: Botões de Controle e Configuração (Fluido) ---
        self.frame_buttons = tk.Frame(self.main_frame, bd=2, relief="groove", padx=10, pady=10)
        self.frame_buttons.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.frame_buttons.grid_columnconfigure(0, weight=1)
        self.frame_buttons.grid_columnconfigure(1, weight=1)
        self.frame_buttons.grid_columnconfigure(2, weight=1)
        self.frame_buttons.grid_columnconfigure(3, weight=1)

        # Combobox de Seleção de Terminal
        tk.Label(self.frame_buttons, text="Terminal:", anchor="w").grid(row=0, column=3, padx=5, pady=2, sticky="w")
        self.terminal_select = ttk.Combobox(self.frame_buttons, 
                                            textvariable=self.terminal_choice, 
                                            values=list(TERMINAL_COMMANDS.keys()), 
                                            state="readonly",
                                            font=("Arial", 10))
        self.terminal_select.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.terminal_select.bind("<<ComboboxSelected>>", lambda e: self.save_configuration())
        
        # Botões de Ação
        self.btn_start = tk.Button(self.frame_buttons, text="Iniciar Projeto", command=lambda: self.run_script("starter_project.py", new_terminal=True), bg="#28a745", fg="white", font=("Arial", 12, "bold"))
        self.btn_start.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_update = tk.Button(self.frame_buttons, text="Atualizar Web", command=lambda: self.run_script("update_webinterface.py", new_terminal=True), bg="#007bff", fg="white", font=("Arial", 12, "bold"))
        self.btn_update.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # CORREÇÃO: Remove args=['y'] para permitir o input manual no terminal
        self.btn_stop = tk.Button(self.frame_buttons, text="Parar Tudo", command=lambda: self.run_script("stopper_project.py", new_terminal=True), bg="#dc3545", fg="white", font=("Arial", 12, "bold"))
        self.btn_stop.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.status_label = tk.Label(self.frame_buttons, text="Status: Pronto", bd=1, relief="sunken", anchor="w", padx=5)
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")


        # --- Área 3: Terminal (Log de Status Simples) ---
        self.frame_terminal = tk.Frame(self.main_frame, bd=2, relief="groove", padx=5, pady=5)
        self.frame_terminal.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        self.frame_terminal.grid_rowconfigure(0, weight=1)
        self.frame_terminal.grid_columnconfigure(0, weight=1)

        # Usamos ScrolledText apenas como exibidor de log e status
        self.terminal_output = scrolledtext.ScrolledText(self.frame_terminal, wrap=tk.WORD, bg="black", fg="lime", font=("Consolas", 10))
        self.terminal_output.grid(row=0, column=0, sticky="nsew")
        self.terminal_output.insert(tk.END, ">>> Log de Status (Execução nos terminais do sistema) <<<\n")
        self.terminal_output.config(state=tk.DISABLED)

        # --- Área 4: Lista de Contêineres (Fluida, lateral) ---
        self.frame_containers = tk.Frame(self.main_frame, bd=2, relief="groove", padx=5, pady=5)
        self.frame_containers.grid(row=2, column=1, rowspan=2, sticky="nsew", padx=5, pady=5) 
        self.frame_containers.grid_rowconfigure(1, weight=1) 
        self.frame_containers.grid_columnconfigure(0, weight=1)

        tk.Label(self.frame_containers, text="Contêineres em Execução", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)
        
        self.container_list_area = scrolledtext.ScrolledText(self.frame_containers, wrap=tk.WORD, height=10, font=("Arial", 10), state=tk.DISABLED)
        self.container_list_area.grid(row=1, column=0, sticky="nsew")
        
    def run_script(self, script_name, args=None, new_terminal=False):
        """Executa um script Python, abrindo um novo terminal do sistema e liberando a GUI imediatamente."""
        
        # 1. Loga o início da execução
        self.terminal_output.config(state=tk.NORMAL)
        # Ajusta a mensagem de log para mostrar os argumentos apenas se existirem
        arg_str = ' '.join(args) if args else ''
        self.terminal_output.insert(tk.END, f"$ Abrindo terminal para: python {script_name} {arg_str}...\n")
        self.terminal_output.config(state=tk.DISABLED)
        
        # 2. Inicia o terminal externo em uma thread separada para evitar qualquer bloqueio
        threading.Thread(target=self._execute_external_script_and_finish, args=(script_name, args)).start()

        # 3. Atualiza o status visual
        self.status_label.config(text=f"Status: Executando {script_name} em novo terminal...")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_update.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)

    import shutil # Certifique-se de que esta linha está no topo do seu arquivo

# ... (outras classes e métodos) ...

    def _execute_external_script_and_finish(self, script_name, args=None):
        """Inicia o processo externo e chama a função de conclusão imediatamente após o Popen."""
        
        # 1. Tenta obter o comando completo e verifica a existência do executável
        try:
            full_command = self.get_terminal_command_with_args(script_name, args)
            
            # CRÍTICO: Verifica se o EXECUTÁVEL principal existe ANTES de chamar Popen
            executable_path = shutil.which(full_command[0])
            if not executable_path:
                raise FileNotFoundError(f"O executável '{full_command[0]}' não foi encontrado no PATH.")

        except FileNotFoundError as e:
            error_msg = f"ERRO: Terminal não encontrado: {e}. Verifique sua seleção ou instale o programa."
            self.master.after(0, self.update_terminal_output, error_msg, error=True)
            self.master.after(0, self.script_finished, 1)
            return
        except Exception as e:
            error_msg = f"ERRO na construção do comando: {e}"
            self.master.after(0, self.update_terminal_output, error_msg, error=True)
            self.master.after(0, self.script_finished, 1)
            return

        # 2. Tenta iniciar o processo
        try:
            # Inicia o processo no sistema
            subprocess.Popen(full_command, close_fds=True)
            
            # Chama o método de conclusão imediatamente para liberar os botões
            self.master.after(100, self.script_finished, 0, script_name) # Código 0 = Sucesso

        # 3. Trata exceções do Popen (se o terminal existir mas falhar ao ser executado)
        except Exception as e:
            # Tratamento para falhas no subprocess.Popen
            error_msg = f"ERRO ao iniciar terminal: {e} (Comando: {full_command[0]})"
            self.master.after(0, self.update_terminal_output, error_msg, error=True)
            self.master.after(0, self.script_finished, 1)


    def get_terminal_command_with_args(self, script_name, args=None):
        """Retorna o comando completo com argumentos incluídos na string de execução do terminal."""
        terminal_key = self.terminal_choice.get()
        terminal_type = TERMINAL_COMMANDS.get(terminal_key, "default")

        arg_str = ' '.join(args) if args else ''
        python_command = f'python3 {script_name} {arg_str}'
        
        if terminal_type == 'cmd':
            return ['start', 'cmd', '/k', 'python', script_name, *args]

        elif terminal_type == 'konsole':
            return ['konsole', '-e', f'bash -c "{python_command}; exec bash"']
            
        elif terminal_type == 'gnome-terminal':
            return ['gnome-terminal', '--', 'bash', '-c', f'{python_command}; exec bash']

        elif terminal_type == 'xterm':
             # Tenta encontrar 'xterm'.
            return ['xterm', '-e', f'bash -c "{python_command}; exec bash"']

        else: # Default ou Auto-Detect (para Linux/macOS)
            if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
                 # Tenta executar via bash -c (o mais compatível)
                return ['/bin/bash', '-c', f'{python_command}; read -p "Pressione ENTER para fechar..."']
            else:
                 # Fallback para sistemas Windows/Outros
                return [sys.executable, script_name, *args]
        
    def get_terminal_command(self, script_name):
        # Este método não é mais necessário, mas será mantido vazio para evitar quebras
        pass

    def script_finished(self, return_code, script_name="Script Externo"):
        """Finaliza a execução do script e restaura o estado da GUI."""
        
        # 1. Loga a conclusão
        final_message = "SUCESSO: Terminal externo iniciado e botões liberados." if return_code == 0 else "ERRO: Falha ao iniciar terminal externo."
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, f"\n{final_message}\n")
        self.terminal_output.config(state=tk.DISABLED)
        
        # 2. Restaura o status e libera botões
        self.status_label.config(text=f"Status: Pronto (Última Ação: {script_name})")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_update.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL)
        self.update_container_list() # Atualiza a lista imediatamente

    # --- Métodos de Execução e Docker (Ajustado para usar a escolha do usuário) ---
    def run_script(self, script_name, args=None, new_terminal=False):
        """Executa um script Python, abrindo um novo terminal do sistema e liberando a GUI imediatamente."""
        
        # 1. Loga o início da execução
        self.terminal_output.config(state=tk.NORMAL)
        # Ajusta a mensagem de log para mostrar os argumentos apenas se existirem
        arg_str = ' '.join(args) if args else ''
        self.terminal_output.insert(tk.END, f"$ Abrindo terminal para: python {script_name} {arg_str}...\n")
        self.terminal_output.config(state=tk.DISABLED)
        
        # 2. Inicia o terminal externo em uma thread separada para evitar qualquer bloqueio
        threading.Thread(target=self._execute_external_script_and_finish, args=(script_name, args)).start()

        # 3. Atualiza o status visual
        self.status_label.config(text=f"Status: Executando {script_name} em novo terminal...")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_update.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)

    import shutil # Novo import necessário para verificar a existência de programas

# ... (outros imports e classes) ...

    def _execute_external_script_and_finish(self, script_name, args=None):
        """Inicia o processo externo e chama a função de conclusão imediatamente após o Popen."""
        
        terminal_key = self.terminal_choice.get()
        
        # 1. Pré-verificação do executável
        if terminal_key not in ["Auto-Detect (OS Default)", "Windows CMD (cmd /k)"]:
            terminal_exec = TERMINAL_COMMANDS[terminal_key]
            # Usa shutil.which para verificar se o executável existe no PATH
            if not shutil.which(terminal_exec):
                error_msg = f"ERRO: O executável do terminal '{terminal_exec}' não foi encontrado no seu sistema. Selecione outra opção ou instale o programa."
                self.master.after(0, self.update_terminal_output, error_msg, error=True)
                self.master.after(0, self.script_finished, 1)
                return
        
        # 2. Tenta obter o comando completo
        try:
            full_command = self.get_terminal_command_with_args(script_name, args)
        except Exception as e:
            error_msg = f"ERRO na construção do comando: {e}"
            self.master.after(0, self.update_terminal_output, error_msg, error=True)
            self.master.after(0, self.script_finished, 1)
            return

        # 3. Inicia o processo
        try:
            subprocess.Popen(full_command, close_fds=True)
            
            # Chama o método de conclusão imediatamente para liberar os botões
            self.master.after(100, self.script_finished, 0, script_name) # Código 0 = Sucesso

        # 4. Trata exceções (incluindo o caso onde o executável do terminal falha ao iniciar)
        except FileNotFoundError as e:
            error_msg = f"ERRO: Executável principal não encontrado. {e.strerror} (Comando: {full_command[0]})"
            self.master.after(0, self.update_terminal_output, error_msg, error=True)
            self.master.after(0, self.script_finished, 1)
        except Exception as e:
            # Tratamento genérico para falhas inesperadas no Popen
            error_msg = f"ERRO inesperado ao iniciar processo: {e} (Comando: {full_command[0]})"
            self.master.after(0, self.update_terminal_output, error_msg, error=True)
            self.master.after(0, self.script_finished, 1)


    def get_terminal_command_with_args(self, script_name, args=None):
        """Retorna o comando completo com argumentos incluídos na string de execução do terminal."""
        terminal_key = self.terminal_choice.get()
        terminal_type = TERMINAL_COMMANDS.get(terminal_key, "default")

        arg_str = ' '.join(args) if args else ''
        python_command = f'python3 {script_name} {arg_str}'
        
        if terminal_type == 'cmd':
            return ['start', 'cmd', '/k', 'python', script_name, *args]

        elif terminal_type == 'konsole':
            return ['konsole', '-e', f'bash -c "{python_command}; exec bash"']
            
        elif terminal_type == 'gnome-terminal':
            return ['gnome-terminal', '--', 'bash', '-c', f'{python_command}; exec bash']

        elif terminal_type == 'xterm':
             # Xterm usa -e para o comando
            return ['xterm', '-e', f'bash -c "{python_command}; exec bash"']

        else: # Default ou Auto-Detect (para Linux/macOS)
            if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
                 # Tenta executar via bash -c (o mais compatível)
                return ['/bin/bash', '-c', f'{python_command}; read -p "Pressione ENTER para fechar..."']
            else:
                 # Retorna o comando base para o subprocess
                return [sys.executable, script_name, *args]


    def script_finished(self, return_code, script_name="Script Externo"):
        """Finaliza a execução do script e restaura o estado da GUI."""
        
        # 1. Loga a conclusão
        final_message = "SUCESSO: Terminal externo iniciado e botões liberados." if return_code == 0 else "ERRO: Falha ao iniciar terminal externo."
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, f"\n{final_message}\n")
        self.terminal_output.config(state=tk.DISABLED)
        
        # 2. Restaura o status e libera botões
        self.status_label.config(text=f"Status: Pronto (Última Ação: {script_name})")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_update.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL)
        self.update_container_list() # Atualiza a lista imediatamente

    def get_docker_status(self):
        """Executa 'docker ps -a' e retorna a lista formatada de contêineres."""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.Names}}|{{.Status}}'],
                capture_output=True, text=True, check=True
            )
            linhas = result.stdout.strip().split('\n')
            
            status_list_str = ""
            if not linhas or (len(linhas) == 1 and not linhas[0]):
                status_list_str = "Nenhum contêiner Docker encontrado."
            else:
                for linha in linhas:
                    if not linha: continue
                    try:
                        name, status = linha.split('|', 1)
                        if 'Up' in status or 'running' in status.lower():
                            emoji = '🟢'
                        elif 'Exited' in status or 'dead' in status.lower():
                            emoji = '🔴'
                        else:
                            emoji = '🟡'
                        
                        status_list_str += f"{emoji} {name} ({status})\n"
                    except ValueError:
                        status_list_str += f"❓ {linha} (Status desconhecido)\n"
            return status_list_str
        except FileNotFoundError:
            return "ERRO: Comando 'docker' não encontrado. Instale o Docker."
        except subprocess.CalledProcessError as e:
            return f"ERRO ao executar 'docker ps -a': {e.stderr}"
        except Exception as e:
            return f"ERRO inesperado ao verificar Docker: {e}"

    def update_container_list(self):
        """Atualiza a Área 4 com o status dos contêineres Docker."""
        status_text = self.get_docker_status()
        self.container_list_area.config(state=tk.NORMAL)
        self.container_list_area.delete(1.0, tk.END)
        self.container_list_area.insert(tk.END, status_text)
        self.container_list_area.config(state=tk.DISABLED)

    def update_container_list_periodically(self):
        """Atualiza a lista de contêineres periodicamente (a cada 5 segundos)."""
        self.update_container_list()
        self.master.after(5000, self.update_container_list_periodically)


# --- Bloco principal de execução (Mantido) ---
if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        messagebox.showerror("Erro de Dependência", "A biblioteca PIL/Pillow não está instalada. Por favor, execute: pip install Pillow")
        sys.exit(1)
        
    root = tk.Tk()
    gui = DockerManagerGUI(root)
    root.mainloop()