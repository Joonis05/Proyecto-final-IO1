import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from config import C, FONT_TITLE, FONT_SUB, FONT_NORMAL, FONT_MONO, FONT_MONO_B, FONT_LABEL, FONT_BIG_VAL
from fractions import Fraction

class OptimizerView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Optimizador — Simplex & Gran M  |  IO-I (MVC)")
        self.geometry("1300x850")
        self.configure(bg=C["bg_dark"])
        self.resizable(True, True)
        
        self.controller = None

        self.entries_c = []
        self.entries_A = []
        self.entries_b = []
        self.combos_t  = []
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TCombobox', fieldbackground=C["bg_dark"], background=C["accent1"], foreground=C["text_main"])
        
        # Treeview styling
        self.style.configure('Treeview', 
                             background=C["bg_mid"], 
                             foreground=C["text_main"], 
                             fieldbackground=C["bg_mid"],
                             rowheight=32,
                             font=FONT_NORMAL)
        self.style.configure('Treeview.Heading', 
                             background=C["bg_panel"], 
                             foreground=C["accent3"], 
                             font=FONT_MONO_B)
        self.style.map('Treeview', background=[('selected', C["highlight"])])

        # Scrollbar styling
        self.style.configure('TScrollbar', 
                             gripcount=0,
                             background=C["bg_panel"], 
                             troughcolor=C["bg_dark"], 
                             bordercolor=C["bg_dark"], 
                             arrowcolor=C["text_dim"],
                             lightcolor=C["bg_panel"],
                             darkcolor=C["bg_panel"],
                             relief="flat")
        
        self.style.map('TScrollbar', 
                       background=[('active', C["accent1"]), ('pressed', C["accent2"])])

        self._build_ui()

    def set_controller(self, controller):
        self.controller = controller

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=C["header_bg"], height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⬡  OPTIMIZADOR  —  Simplex & Gran M",
                 font=FONT_TITLE, bg=C["header_bg"],
                 fg=C["accent2"]).pack(side="left", padx=26, pady=16)
        tk.Label(hdr, text="Investigación de Operaciones I",
                 font=FONT_NORMAL, bg=C["header_bg"],
                 fg=C["text_dim"]).pack(side="right", padx=26)

        # Body
        body = tk.Frame(self, bg=C["bg_dark"])
        body.pack(fill="both", expand=True, padx=12, pady=12)

        # Dos columnas responsivas: izquierda 40 % — derecha 60 %
        body.columnconfigure(0, weight=40, minsize=340)
        body.columnconfigure(1, weight=60, minsize=340)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=C["bg_panel"], highlightthickness=1,
                        highlightbackground=C["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right = tk.Frame(body, bg=C["bg_mid"], highlightthickness=1,
                         highlightbackground=C["border"])
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    def _build_left(self, parent):
        # Título de sección
        tk.Label(parent, text="CONFIGURACIÓN",
                 font=FONT_LABEL, bg=C["bg_panel"],
                 fg=C["accent3"]).pack(anchor="w", padx=20, pady=(20, 4))
        
        tk.Label(parent, text="Defina su Problema",
                 font=FONT_SUB, bg=C["bg_panel"],
                 fg=C["text_main"]).pack(anchor="w", padx=20, pady=(0, 16))

        # Card de Dimensiones
        dim_card = tk.Frame(parent, bg=C["bg_mid"], highlightthickness=1, highlightbackground=C["border"])
        dim_card.pack(fill="x", padx=16, pady=4)
        
        dim = tk.Frame(dim_card, bg=C["bg_mid"])
        dim.pack(fill="x", padx=12, pady=12)

        tk.Label(dim, text="VARIABLES", font=FONT_LABEL,
                 bg=C["bg_mid"], fg=C["text_dim"]).grid(row=0, column=0, sticky="w", pady=4)
        self.n_var = tk.IntVar(value=2)
        tk.Spinbox(dim, from_=2, to=8, textvariable=self.n_var, width=5, font=FONT_NORMAL,
                   bg=C["bg_dark"], fg=C["text_main"], relief="flat",
                   insertbackground=C["text_main"],
                   buttonbackground=C["accent1"]).grid(row=0, column=1, padx=(12, 0), pady=4)

        tk.Label(dim, text="RESTRICCIONES", font=FONT_LABEL,
                 bg=C["bg_mid"], fg=C["text_dim"]).grid(row=1, column=0, sticky="w", pady=4)
        self.n_res = tk.IntVar(value=2)
        tk.Spinbox(dim, from_=1, to=8, textvariable=self.n_res, width=5, font=FONT_NORMAL,
                   bg=C["bg_dark"], fg=C["text_main"], relief="flat",
                   insertbackground=C["text_main"],
                   buttonbackground=C["accent1"]).grid(row=1, column=1, padx=(12, 0), pady=4)

        tk.Button(dim, text="GENERAR ESTRUCTURA", command=self._generar_tabla,
                  bg=C["accent1"], fg=C["text_main"], font=FONT_LABEL,
                  relief="flat", cursor="hand2", activebackground=C["accent2"],
                  padx=12, pady=8).grid(row=0, column=2, rowspan=2, padx=(20, 0), sticky="ns")

        # Card de Opciones
        opt_card = tk.Frame(parent, bg=C["bg_panel"])
        opt_card.pack(fill="x", padx=16, pady=10)

        # Objetivo
        obj_fr = tk.Frame(opt_card, bg=C["bg_panel"])
        obj_fr.pack(fill="x", pady=4)
        tk.Label(obj_fr, text="OBJETIVO:", font=FONT_LABEL, width=10, anchor="w",
                 bg=C["bg_panel"], fg=C["text_dim"]).pack(side="left")
        self.tipo_obj = tk.StringVar(value="Maximizar")
        for txt in ("Maximizar", "Minimizar"):
            tk.Radiobutton(obj_fr, text=txt, variable=self.tipo_obj, value=txt, font=FONT_NORMAL,
                           bg=C["bg_panel"], fg=C["text_main"],
                           selectcolor=C["accent1"],
                           activebackground=C["bg_panel"]).pack(side="left", padx=8)

        # Método
        met_fr = tk.Frame(opt_card, bg=C["bg_panel"])
        met_fr.pack(fill="x", pady=4)
        tk.Label(met_fr, text="MÉTODO:", font=FONT_LABEL, width=10, anchor="w",
                 bg=C["bg_panel"], fg=C["text_dim"]).pack(side="left")
        self.metodo = tk.StringVar(value="Simplex")
        for txt in ("Simplex", "Gran M"):
            tk.Radiobutton(met_fr, text=txt, variable=self.metodo, value=txt, font=FONT_NORMAL,
                           bg=C["bg_panel"], fg=C["text_main"],
                           selectcolor=C["accent1"],
                           activebackground=C["bg_panel"]).pack(side="left", padx=8)

        # Fracciones toggle
        extra_fr = tk.Frame(opt_card, bg=C["bg_panel"])
        extra_fr.pack(fill="x", pady=4)
        self.show_fractions = tk.BooleanVar(value=False)
        tk.Checkbutton(extra_fr, text="Visualización en Fracciones (Exacto)", variable=self.show_fractions,
                       font=FONT_NORMAL, bg=C["bg_panel"], fg=C["accent3"],
                       selectcolor=C["bg_dark"], activebackground=C["bg_panel"]).pack(side="left", padx=(0,0))

        # Botones Resolver + Limpiar lado a lado
        btn_bar = tk.Frame(parent, bg=C["bg_panel"])
        btn_bar.pack(fill="x", side="bottom", padx=16, pady=14)
        btn_bar.columnconfigure(0, weight=3)
        btn_bar.columnconfigure(1, weight=2)

        tk.Button(btn_bar, text="▶  RESOLVER PROBLEMA", command=self._on_solve_clicked,
                  bg=C["accent1"], fg=C["text_main"],
                  font=("Segoe UI Variable Text", 11, "bold"),
                  relief="flat", cursor="hand2",
                  activebackground=C["accent2"],
                  pady=12).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        tk.Button(btn_bar, text="🗑  LIMPIAR", command=self._limpiar,
                  bg=C["bg_panel"], fg=C["text_dim"],
                  font=("Segoe UI Variable Text", 11, "bold"),
                  relief="flat", cursor="hand2",
                  activebackground=C["bg_mid"],
                  pady=12).grid(row=0, column=1, sticky="ew")

        # Tabla scrollable
        outer = tk.Frame(parent, bg=C["bg_panel"])
        outer.pack(fill="both", expand=True, side="top", padx=12, pady=12)

        canvas = tk.Canvas(outer, bg=C["bg_panel"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical",   command=canvas.yview)
        hsb = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.table_frame = tk.Frame(canvas, bg=C["bg_panel"])
        self._table_win_id = canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.table_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))

        # Soporte para rueda del ratón
        self._bind_mouse_wheel(canvas, self.table_frame)

        self._generar_tabla()

    def _build_right(self, parent):
        tk.Label(parent, text="RESULTADOS",
                 font=FONT_LABEL, bg=C["bg_mid"],
                 fg=C["accent3"]).pack(anchor="w", padx=20, pady=(20, 4))
        
        tk.Label(parent, text="Resumen del Óptimo",
                 font=FONT_SUB, bg=C["bg_mid"],
                 fg=C["text_main"]).pack(anchor="w", padx=20, pady=(0, 16))

        # Dashboard de Resultados
        dash = tk.Frame(parent, bg=C["bg_mid"])
        dash.pack(fill="x", padx=16, pady=(0, 20))
        
        # Estado Card
        est_c = tk.Frame(dash, bg=C["bg_panel"], highlightthickness=1, highlightbackground=C["border"])
        est_c.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(est_c, text="ESTADO ACTUAL", font=FONT_LABEL, bg=C["bg_panel"], fg=C["text_dim"]).pack(pady=(10, 2))
        self.lbl_estado = tk.Label(est_c, text="—", font=FONT_SUB, bg=C["bg_panel"], fg=C["text_main"])
        self.lbl_estado.pack(pady=(0, 10))

        # Valor Card
        val_c = tk.Frame(dash, bg=C["bg_panel"], highlightthickness=1, highlightbackground=C["border"])
        val_c.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(val_c, text="VALOR Z ÓPTIMO", font=FONT_LABEL, bg=C["bg_panel"], fg=C["text_dim"]).pack(pady=(10, 2))
        self.lbl_valor = tk.Label(val_c, text="—", font=FONT_BIG_VAL, bg=C["bg_panel"], fg=C["success"])
        self.lbl_valor.pack(pady=(0, 10))

        # Variables Card
        var_c = tk.Frame(parent, bg=C["bg_mid"], highlightthickness=1, highlightbackground=C["border"])
        var_c.pack(fill="x", padx=16, pady=(0, 20))
        tk.Label(var_c, text="VARIABLES DE DECISIÓN", font=FONT_LABEL, bg=C["bg_mid"], fg=C["text_dim"]).pack(anchor="w", padx=14, pady=(10, 2))
        self.lbl_vars = tk.Label(var_c, text="—", font=FONT_MONO, bg=C["bg_mid"], fg=C["accent3"], justify="left", wraplength=700)
        self.lbl_vars.pack(anchor="w", padx=14, pady=(0, 14))

        tk.Label(parent, text="ITERACIONES DEL TABLEAU",
                 font=FONT_LABEL, bg=C["bg_mid"],
                 fg=C["text_dim"]).pack(anchor="w", padx=20, pady=(10, 0))

        # Contenedor scrollable para Treeviews
        self.iter_canvas = tk.Canvas(parent, bg=C["bg_dark"], highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.iter_canvas.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.iter_canvas.xview)
        self.iter_canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.iter_frame = tk.Frame(self.iter_canvas, bg=C["bg_dark"])
        self.iter_canvas.create_window((0, 0), window=self.iter_frame, anchor="nw")
        
        def _on_iter_frame_config(e):
            self.iter_canvas.configure(scrollregion=self.iter_canvas.bbox("all"))
        self.iter_frame.bind("<Configure>", _on_iter_frame_config)

        hsb.pack(side="bottom", fill="x", padx=14)
        vsb.pack(side="right", fill="y", pady=4)
        self.iter_canvas.pack(side="left", fill="both", expand=True, padx=14, pady=(4, 14))

        # Soporte para rueda del ratón
        self._bind_mouse_wheel(self.iter_canvas, self.iter_frame)

    def _generar_tabla(self):
        for w in self.table_frame.winfo_children():
            w.destroy()
        self.entries_c.clear()
        self.entries_A.clear()
        self.entries_b.clear()
        self.combos_t.clear()

        n = self.n_var.get()
        m = self.n_res.get()
        tf = self.table_frame

        # Header de Función Objetivo
        tk.Label(tf, text="FUNCIÓN OBJETIVO (Z)", font=FONT_LABEL,
                 bg=C["bg_panel"], fg=C["accent4"]).grid(
            row=0, column=0, columnspan=n + 3, pady=(10, 15), sticky="w")

        for j in range(n):
            tk.Label(tf, text=f"x{j+1}", font=FONT_MONO_B,
                     bg=C["bg_dark"], fg=C["accent3"],
                     width=8, pady=8).grid(row=1, column=j + 1, padx=4)

        tk.Label(tf, text="MAX Z =", font=FONT_LABEL,
                 bg=C["bg_panel"], fg=C["text_main"]).grid(row=2, column=0, padx=10)
        
        row_c = []
        for j in range(n):
            e = tk.Entry(tf, width=8, font=FONT_MONO,
                         bg=C["bg_mid"], fg=C["success"],
                         insertbackground=C["text_main"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=C["border"])
            e.insert(0, "1")
            e.grid(row=2, column=j + 1, padx=4, pady=8, ipady=5)
            row_c.append(e)
        self.entries_c = row_c

        # Header de Restricciones
        tk.Label(tf, text="RESTRICCIONES", font=FONT_LABEL,
                 bg=C["bg_panel"], fg=C["accent4"]).grid(
            row=3, column=0, columnspan=n + 3, pady=(25, 15), sticky="w")

        tk.Label(tf, text="TIPO", font=FONT_LABEL,
                 bg=C["bg_panel"], fg=C["text_dim"],
                 width=6).grid(row=4, column=n + 1, padx=4)
        tk.Label(tf, text="RHS", font=FONT_LABEL,
                 bg=C["bg_panel"], fg=C["text_dim"],
                 width=8).grid(row=4, column=n + 2, padx=4)

        for i in range(m):
            bg = C["row_even"] if i % 2 == 0 else C["row_odd"]
            tk.Label(tf, text=f"R{i+1}", font=FONT_MONO_B,
                     bg=C["bg_dark"], fg=C["text_dim"],
                     width=5, pady=6).grid(row=5 + i, column=0, padx=8)

            row_A = []
            for j in range(n):
                e = tk.Entry(tf, width=8, font=FONT_MONO,
                             bg=bg, fg=C["text_main"],
                             insertbackground=C["text_main"],
                             relief="flat", highlightthickness=1,
                             highlightbackground=C["border"])
                e.insert(0, "1")
                e.grid(row=5 + i, column=j + 1, padx=4, pady=6, ipady=5)
                row_A.append(e)
            self.entries_A.append(row_A)

            tipo_var = tk.StringVar(value="<=")
            cmb = ttk.Combobox(tf, textvariable=tipo_var,
                               values=["<=", ">=", "="], width=4, font=FONT_MONO,
                               state="readonly")
            cmb.grid(row=5 + i, column=n + 1, padx=8)
            self.combos_t.append(cmb)

            eb = tk.Entry(tf, width=8, font=FONT_MONO,
                          bg=bg, fg=C["success"],
                          insertbackground=C["text_main"],
                          relief="flat", highlightthickness=1,
                          highlightbackground=C["border"])
            eb.insert(0, "10")
            eb.grid(row=5 + i, column=n + 2, padx=4, pady=6, ipady=5)
            self.entries_b.append(eb)

    def _on_solve_clicked(self):
        if self.controller:
            self.controller.solve()

    def _limpiar(self):
        """Borra el contenido de todos los Entry y reinicia el panel de resultados."""
        # Limpiar función objetivo
        for e in self.entries_c:
            e.delete(0, tk.END)

        # Limpiar restricciones
        for row in self.entries_A:
            for e in row:
                e.delete(0, tk.END)

        # Limpiar RHS
        for e in self.entries_b:
            e.delete(0, tk.END)

        # Reiniciar panel de resultados
        self.lbl_estado.configure(text="—", fg=C["text_main"])
        self.lbl_valor.configure(text="—", fg=C["success"])
        self.lbl_vars.configure(text="—", fg=C["accent4"])

        # Limpiar iteraciones del tableau
        for w in self.iter_frame.winfo_children():
            w.destroy()

    def _parse_val(self, s):
        """Permite ingresar '1/2' o '0.5'."""
        try:
            return float(Fraction(s.strip()))
        except:
            return 0.0

    def get_inputs(self):
        n = self.n_var.get()
        m = self.n_res.get()
        
        c = np.array([self._parse_val(self.entries_c[j].get()) for j in range(n)])
        A = np.array([[self._parse_val(self.entries_A[i][j].get())
                       for j in range(n)] for i in range(m)])
        b = np.array([self._parse_val(self.entries_b[i].get()) for i in range(m)])
        tipos = [self.combos_t[i].get() for i in range(m)]
        maximizar = self.tipo_obj.get() == "Maximizar"
        metodo = self.metodo.get()
        
        return c, A, b, tipos, maximizar, metodo

    # ------------------------------------------------------------------
    # Formato de valores con M simbólica
    # ------------------------------------------------------------------
    def _fmt_M(self, val, M=1e6):
        """
        Formatea un número mostrando M simbólicamente cuando corresponde.
        Ejemplos:
          1e6       → "M"
         -1e6       → "-M"
          11e6      → "11M"
          8 - 11e6  → "8-11M"
          10 - 13e6 → "10-13M"
          250e6     → "250M"
          3.5       → "3.5"
        """
        if val is None:
            return ""
        tol = 1e-3
        if abs(val) < tol:
            return "0"

        b_float = val / M
        b_int   = round(b_float)

        if abs(b_int) >= 1 and abs(b_float - b_int) < tol:
            # El valor tiene componente M
            a     = val - b_int * M
            a_int = round(a)
            abs_b = abs(b_int)
            m_str = "M" if abs_b == 1 else f"{abs_b}M"

            if abs(a_int) < 1:               # parte constante ≈ 0
                return m_str if b_int > 0 else f"-{m_str}"
            else:                             # parte mixta: a ± kM
                if b_int > 0:
                    return f"{a_int}+{m_str}"
                else:
                    return f"{a_int}-{m_str}"

        # Número regular — hasta 2 decimales sin ceros finales
        if self.show_fractions.get():
            f = Fraction(val).limit_denominator(1000)
            if f.denominator == 1: return str(f.numerator)
            return f"{f.numerator}/{f.denominator}"

        if val == int(val):
            return str(int(val))
        s = f"{val:.2f}".rstrip("0").rstrip(".")
        return "0" if (not s or s in ("-", "-0")) else s

    def _bind_mouse_wheel(self, canvas, widget):
        """Asocia el evento de la rueda del ratón al canvas mediante hover en el widget."""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Cuando el ratón entra en el área, activamos el scroll global para ese canvas
        widget.bind("<Enter>", lambda _: widget.bind_all("<MouseWheel>", _on_mousewheel))
        # Cuando sale, lo desactivamos para no interferir con otros paneles
        widget.bind("<Leave>", lambda _: widget.unbind_all("<MouseWheel>"))

    # ------------------------------------------------------------------
    # Tabla clásica de simplex (una por iteración)
    # ------------------------------------------------------------------
    def _render_tableau(self, parent, paso):
        """Renderiza un tableau al estilo libro: Vb | Cb | vars | RHS + Zj / Cj-Zj."""
        cols      = paso["cols"]          # ["Vb","Cb","x1",...,"RHS"]
        data_rows = paso["rows"]          # [vb, cb, a_i1, ..., bi]
        c_header  = paso.get("c_header", [])
        zj        = paso.get("zj",   [])
        cj_zj     = paso.get("cj_zj", [])

        # Número total de filas: cj + datos + Zj + Cj-Zj
        total_rows = 1 + len(data_rows) + 2

        tv = ttk.Treeview(parent, columns=cols, show="headings", height=total_rows)

        # --- Anchos de columna ---
        tv.column("Vb", width=68,  minwidth=60,  anchor="center")
        tv.column("Cb", width=80,  minwidth=70,  anchor="center")
        for col in cols[2:]:
            tv.column(col, width=90, minwidth=70, anchor="center")

        for col in cols:
            tv.heading(col, text=col)

        # --- Fila cj (encabezado objetivo) ---
        cj_row = ["cj →", ""] + [self._fmt_M(v) for v in c_header] + [""]
        tv.insert("", "end", values=cj_row, tags=("row_cj",))

        # --- Filas de datos ---
        pivot_info = paso.get("pivot") # (row_idx, col_idx_en_tableau)
        
        for idx, r in enumerate(data_rows):
            vb   = r[0]
            cb   = self._fmt_M(r[1])
            
            # Formatear valores de la fila, resaltando el elemento pivote si corresponde
            vals_fmt = []
            for j, v in enumerate(r[2:]):
                val_s = self._fmt_M(v)
                # j es el índice en r[2:], que corresponde a las columnas del tableau a partir de la 3ra
                if pivot_info and pivot_info[0] == idx and pivot_info[1] == j:
                    val_s = f"[{val_s}]" # Resaltado visual del elemento pivote
                vals_fmt.append(val_s)
            
            tags = []
            if idx % 2 == 0: tags.append("row_even")
            else: tags.append("row_odd")
            
            if pivot_info and pivot_info[0] == idx:
                tags.append("row_pivot")
            
            tv.insert("", "end", values=[vb, cb] + vals_fmt, tags=tuple(tags))

        # --- Fila Zj ---
        zj_row = ["Zj", ""] + [self._fmt_M(v) for v in zj]
        tv.insert("", "end", values=zj_row, tags=("row_zj",))

        # --- Fila Cj − Zj ---
        cj_zj_fmt = [self._fmt_M(v) for v in cj_zj]
        cjzj_row = ["Cj-Zj", ""] + cj_zj_fmt
        tv.insert("", "end", values=cjzj_row, tags=("row_cjzj",))

        # --- Estilos de filas ---
        tv.tag_configure("row_cj",    background=C["accent1"],  foreground=C["text_main"])
        tv.tag_configure("row_even",  background=C["row_even"], foreground=C["text_main"])
        tv.tag_configure("row_odd",   background=C["row_odd"],  foreground=C["text_main"])
        tv.tag_configure("row_pivot", background=C["teal"],     foreground=C["text_main"])
        tv.tag_configure("row_zj",    background=C["bg_panel"], foreground=C["success"])
        tv.tag_configure("row_cjzj",  background=C["bg_panel"], foreground=C["cyan"])

        tv.pack(anchor="w", pady=(0, 4))
        
        # --- Texto explicativo del pivote ---
        if pivot_info:
            row_idx, col_idx = pivot_info
            v_entra = cols[col_idx + 2] # +2 por Vb y Cb
            v_sale  = vb_names[row_idx] if 'vb_names' in locals() else data_rows[row_idx][0]
            lbl = tk.Label(parent, text=f"➡ Entra: {v_entra}  |  ⬅ Sale: {v_sale}  |  ⭐ Elemento Pivote resaltado con [ ]",
                           font=("Segoe UI", 10, "italic"), bg=parent.cget("bg"), fg=C["accent3"])
            lbl.pack(anchor="w", pady=(0, 4))

    # ------------------------------------------------------------------
    # Mostrar resultados completos
    # ------------------------------------------------------------------
    def display_result(self, estado, valor, x, pasos, metodo):
        # Limpiar frame iteraciones
        for w in self.iter_frame.winfo_children():
            w.destroy()

        # --- Panel de resumen ---
        if estado == "optimo":
            self.lbl_estado.configure(text="✔  ÓPTIMO", fg=C["success"])
            val_str = self._fmt_M(valor)
            self.lbl_valor.configure(text=val_str)
            
            vars_fmt = []
            for i, v in enumerate(x):
                s = self._fmt_M(v)
                vars_fmt.append(f"x{i+1} = {s}")
            self.lbl_vars.configure(text="  ".join(vars_fmt))
        elif estado == "no factible":
            self.lbl_estado.configure(text="✘  NO FACTIBLE", fg=C["error"])
            self.lbl_valor.configure(text="—")
            self.lbl_vars.configure(text="El problema NO tiene solución factible.")
        else:
            self.lbl_estado.configure(text="∞  NO ACOTADO", fg=C["error"])
            self.lbl_valor.configure(text="—")
            self.lbl_vars.configure(text="El problema NO está acotado.")

        # --- Renderizar cada iteración ---
        for paso in pasos:
            wrapper = tk.Frame(
                self.iter_frame,
                bg=C["bg_mid"],
                highlightthickness=1,
                highlightbackground=C["border"],
                padx=10, pady=8
            )
            wrapper.pack(fill="x", pady=8, padx=10)

            tk.Label(
                wrapper,
                text=f" Iteración {paso['it']}",
                font=FONT_SUB,
                bg=C["bg_mid"],
                fg=C["cyan"]
            ).pack(anchor="w", pady=(0, 6))

            self._render_tableau(wrapper, paso)

    def display_warning(self, title, msg):
        messagebox.showwarning(title, msg)

    def display_error(self, title, msg):
        messagebox.showerror(title, msg)