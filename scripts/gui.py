import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)

SCRIPTS = {
    'PNG':               'recuperar_png.py',
    'JPG / Fotos':       'recuperar_jpg.py',
    'Videos':            'recuperar_videos.py',
    'Documentos PDF/Word': 'recuperar_docs.py',
    'Musica MP3':        'recuperar_mp3.py',
    'Vectores / HTML':   'recuperar_vectores_html.py',
    'Excel / PowerPoint':'recuperar_excel.py',
    'Fotos RAW':         'recuperar_raw.py',
    'ZIP / RAR / 7Z':    'recuperar_zip.py',
    'Carpetas (MFT v2)': 'recuperar_carpetas_v2.py',
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Recuperador de Archivos')
        self.geometry('750x600')
        self.resizable(True, True)
        self.configure(bg='#1e1e2e')
        self.corriendo = False
        self._build()

    def _build(self):
        # Titulo
        tk.Label(self, text='RECUPERADOR DE ARCHIVOS',
                 font=('Consolas', 16, 'bold'),
                 fg='#cdd6f4', bg='#1e1e2e').pack(pady=(16, 4))
        tk.Label(self, text='Selecciona que tipos de archivo recuperar',
                 font=('Consolas', 10),
                 fg='#a6adc8', bg='#1e1e2e').pack()

        # Checkboxes
        frame_checks = tk.Frame(self, bg='#1e1e2e')
        frame_checks.pack(padx=20, pady=10, fill='x')
        self.vars = {}
        col = 0
        for i, nombre in enumerate(SCRIPTS):
            var = tk.BooleanVar(value=True)
            self.vars[nombre] = var
            cb = tk.Checkbutton(frame_checks, text=nombre, variable=var,
                                fg='#cdd6f4', bg='#1e1e2e',
                                selectcolor='#313244',
                                activeforeground='#89b4fa',
                                activebackground='#1e1e2e',
                                font=('Consolas', 10))
            cb.grid(row=i // 2, column=i % 2, sticky='w', padx=10, pady=2)

        # Disco origen
        frame_disco = tk.Frame(self, bg='#1e1e2e')
        frame_disco.pack(padx=20, pady=(8, 0), fill='x')
        tk.Label(frame_disco, text='Disco a escanear:',
                 fg='#a6adc8', bg='#1e1e2e',
                 font=('Consolas', 10)).pack(side='left')
        self.disco_var = tk.StringVar(value=r'\\.\C:')
        tk.Entry(frame_disco, textvariable=self.disco_var, width=18,
                 bg='#313244', fg='#cdd6f4',
                 insertbackground='white',
                 font=('Consolas', 10)).pack(side='left', padx=8)

        # Carpeta destino
        frame_dest = tk.Frame(self, bg='#1e1e2e')
        frame_dest.pack(padx=20, pady=6, fill='x')
        tk.Label(frame_dest, text='Carpeta destino:  ',
                 fg='#a6adc8', bg='#1e1e2e',
                 font=('Consolas', 10)).pack(side='left')
        self.dest_var = tk.StringVar(value=r'D:\omnibook 2026 nano')
        tk.Entry(frame_dest, textvariable=self.dest_var, width=35,
                 bg='#313244', fg='#cdd6f4',
                 insertbackground='white',
                 font=('Consolas', 10)).pack(side='left', padx=8)
        tk.Button(frame_dest, text='...', command=self._elegir_destino,
                  bg='#45475a', fg='#cdd6f4',
                  font=('Consolas', 10)).pack(side='left')

        # Botones
        frame_btn = tk.Frame(self, bg='#1e1e2e')
        frame_btn.pack(pady=10)
        self.btn_start = tk.Button(frame_btn, text='  INICIAR RECUPERACION  ',
                                   command=self._iniciar,
                                   bg='#89b4fa', fg='#1e1e2e',
                                   font=('Consolas', 12, 'bold'),
                                   relief='flat', padx=10, pady=6)
        self.btn_start.pack(side='left', padx=8)
        self.btn_stop = tk.Button(frame_btn, text='  DETENER  ',
                                  command=self._detener,
                                  bg='#f38ba8', fg='#1e1e2e',
                                  font=('Consolas', 12, 'bold'),
                                  relief='flat', padx=10, pady=6,
                                  state='disabled')
        self.btn_stop.pack(side='left', padx=8)

        # Barra de progreso
        self.progreso_label = tk.Label(self, text='',
                                       fg='#a6adc8', bg='#1e1e2e',
                                       font=('Consolas', 9))
        self.progreso_label.pack()
        self.progress = ttk.Progressbar(self, mode='indeterminate', length=700)
        self.progress.pack(padx=20, pady=(0, 8))

        # Log
        self.log = scrolledtext.ScrolledText(self, height=14,
                                             bg='#181825', fg='#a6e3a1',
                                             insertbackground='white',
                                             font=('Consolas', 9),
                                             state='disabled')
        self.log.pack(padx=20, pady=(0, 16), fill='both', expand=True)

    def _elegir_destino(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.dest_var.set(carpeta)

    def _log(self, texto):
        self.log.configure(state='normal')
        self.log.insert('end', texto + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def _actualizar_config(self):
        config_path = os.path.join(_dir, 'config.py')
        disco = self.disco_var.get()
        base  = self.dest_var.get()
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(f"DISCO = r'{disco}'\n")
            f.write(f"BASE  = r'{base}'\n\n")
            f.write(f"OUTPUT_PNG      = BASE + r'\\PNGs_recuperados'\n")
            f.write(f"OUTPUT_JPG      = BASE + r'\\JPGs_recuperados'\n")
            f.write(f"OUTPUT_VIDEOS   = BASE + r'\\Videos_recuperados'\n")
            f.write(f"OUTPUT_DOCS     = BASE + r'\\Documentos_recuperados'\n")
            f.write(f"OUTPUT_MUSICA   = BASE + r'\\Musica_recuperada'\n")
            f.write(f"OUTPUT_VECTORES = BASE + r'\\Vectores_HTML_recuperados'\n")
            f.write(f"OUTPUT_EXCEL    = BASE + r'\\Excel_PowerPoint_recuperados'\n")
            f.write(f"OUTPUT_RAW      = BASE + r'\\Fotos_RAW_recuperadas'\n")
            f.write(f"OUTPUT_ZIP      = BASE + r'\\Comprimidos_recuperados'\n")
            f.write(f"OUTPUT_CARPETAS = BASE + r'\\Carpetas_recuperadas'\n")
            f.write(f"OUTPUT_CARPETAS_V2 = BASE + r'\\Carpetas_v2'\n")

    def _iniciar(self):
        seleccionados = [n for n, v in self.vars.items() if v.get()]
        if not seleccionados:
            self._log('[!] Selecciona al menos un tipo de archivo.')
            return
        self.corriendo = True
        self.btn_start.configure(state='disabled')
        self.btn_stop.configure(state='normal')
        self.progress.start(10)
        self._actualizar_config()
        threading.Thread(target=self._correr, args=(seleccionados,), daemon=True).start()

    def _correr(self, seleccionados):
        total = len(seleccionados)
        for i, nombre in enumerate(seleccionados):
            if not self.corriendo:
                break
            script = SCRIPTS[nombre]
            ruta   = os.path.join(_dir, script)
            self.after(0, self.progreso_label.configure,
                       {'text': f'[{i+1}/{total}] {nombre}...'})
            self._log(f'\n{"="*50}')
            self._log(f'[{i+1}/{total}] {nombre}')
            self._log('='*50)

            try:
                proc = subprocess.Popen(
                    [sys.executable, ruta],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                self.proc = proc
                for linea in proc.stdout:
                    if not self.corriendo:
                        proc.terminate()
                        break
                    self.after(0, self._log, linea.rstrip())
                proc.wait()
            except Exception as e:
                self.after(0, self._log, f'Error: {e}')

        self.after(0, self._finalizar)

    def _detener(self):
        self.corriendo = False
        try:
            self.proc.terminate()
        except Exception:
            pass

    def _finalizar(self):
        self.corriendo = False
        self.progress.stop()
        self.btn_start.configure(state='normal')
        self.btn_stop.configure(state='disabled')
        self.progreso_label.configure(text='Listo.')
        self._log('\n[✓] Proceso finalizado.')


if __name__ == '__main__':
    app = App()
    app.mainloop()
