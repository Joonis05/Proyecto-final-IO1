import numpy as np


class OptimizerModel:

    @staticmethod
    def simplex_normal(c, A, b, maximize=True):
        """Resuelve PL con restricciones ≤ (holguras como base inicial)."""
        pasos = []
        m, n = A.shape

        if np.any(b < 0):
            raise ValueError(
                "simplex_normal requiere RHS ≥ 0. "
                "Use Gran M para RHS negativo o restricciones ≥ / =."
            )

        tableau = np.zeros((m + 1, n + m + 1))
        tableau[:m, :n]    = A
        tableau[:m, n:n+m] = np.eye(m)
        tableau[:m, -1]    = b
        obj = c if maximize else -c
        tableau[m, :n] = -obj

        base = list(range(n, n + m))
        col_names = ([f"x{i+1}" for i in range(n)] +
                     [f"s{i+1}" for i in range(m)] + ["RHS"])

        # c_full para display: coeficientes originales + 0 para holguras
        c_display = np.zeros(n + m)
        c_display[:n] = c

        pasos.append(OptimizerModel._fmt_tableau(
            tableau, base, col_names, 0, c_full=c_display))

        for it in range(200):
            row_obj = tableau[m, :-1]
            if np.all(row_obj >= -1e-9):
                break
            
            col_p = int(np.argmin(row_obj))
            ratios = [tableau[i, -1] / tableau[i, col_p]
                      if tableau[i, col_p] > 1e-9 else np.inf
                      for i in range(m)]
            
            if all(r == np.inf for r in ratios):
                return "no acotado", None, None, pasos
            
            row_p = int(np.argmin(ratios))
            
            # Guardamos info del pivote en el paso ANTERIOR antes de transformar
            pasos[-1]["pivot"] = (row_p, col_p) 
            
            base[row_p] = col_p
            tableau[row_p] /= tableau[row_p, col_p]
            for i in range(m + 1):
                if i != row_p:
                    tableau[i] -= tableau[i, col_p] * tableau[row_p]
            
            pasos.append(OptimizerModel._fmt_tableau(
                tableau, base, col_names, it + 1, c_full=c_display))
        else:
            return "no acotado", None, None, pasos

        x = np.zeros(n + m)
        for i, bi in enumerate(base):
            x[bi] = tableau[i, -1]
        valor = tableau[m, -1] if maximize else -tableau[m, -1]
        return "optimo", valor, x[:n], pasos

    @staticmethod
    def gran_m(c, A, b, tipos, maximize=True, M=1e6):
        """Resuelve PL con método de la Gran M. Tipos: '<=', '>=', '='."""
        pasos = []
        m, n = A.shape

        # Manejar RHS negativos: multiplicar fila por -1 e invertir tipo
        for i in range(m):
            if b[i] < 0:
                A[i] = -A[i]
                b[i] = -b[i]
                if tipos[i] == "<=":
                    tipos[i] = ">="
                elif tipos[i] == ">=":
                    tipos[i] = "<="

        n_s = sum(1 for t in tipos if t in ("<=", ">="))
        n_a = sum(1 for t in tipos if t in (">=", "="))

        cols = n + n_s + n_a + 1
        T = np.zeros((m + 1, cols))
        T[:m, :n] = A

        s_idx = n
        a_idx = n + n_s
        base = []
        artificiales = []

        for i, tipo in enumerate(tipos):
            if tipo == "<=":
                T[i, s_idx] = 1
                base.append(s_idx)
                s_idx += 1
            elif tipo == ">=":
                T[i, s_idx] = -1
                s_idx += 1
                T[i, a_idx] = 1
                base.append(a_idx)
                artificiales.append(a_idx)
                a_idx += 1
            elif tipo == "=":
                T[i, a_idx] = 1
                base.append(a_idx)
                artificiales.append(a_idx)
                a_idx += 1
        T[:m, -1] = b

        obj = np.zeros(cols - 1)
        obj[:n] = c if maximize else -c
        for ai in artificiales:
            obj[ai] = -M
        T[m, :-1] = -obj

        # Eliminar artificiales de la fila objetivo (pivoteo inicial correcto)
        for i, bi in enumerate(base):
            if bi in artificiales:
                T[m] -= M * T[i]

        # c_full para display: cj originales + penalidad simbólica en artificiales
        c_display = np.zeros(cols - 1)
        c_display[:n] = c
        penalty = M if not maximize else -M      # +M para minimizar, -M para maximizar
        for ai in artificiales:
            c_display[ai] = penalty

        col_names = ([f"x{i+1}" for i in range(n)] +
                     [f"s{i+1}" for i in range(n_s)] +
                     [f"A{i+1}" for i in range(n_a)] + ["RHS"])

        pasos.append(OptimizerModel._fmt_tableau(
            T, base, col_names, 0, artificiales, c_display))

        for it in range(200):
            row_obj = T[m, :-1]
            if np.all(row_obj >= -1e-9):
                break
            
            col_p = int(np.argmin(row_obj))
            ratios = [T[i, -1] / T[i, col_p]
                      if T[i, col_p] > 1e-9 else np.inf
                      for i in range(m)]
            
            if all(r == np.inf for r in ratios):
                return "no acotado", None, None, pasos
            
            row_p = int(np.argmin(ratios))
            
            # Guardamos info del pivote en el paso ANTERIOR
            pasos[-1]["pivot"] = (row_p, col_p)

            base[row_p] = col_p
            T[row_p] /= T[row_p, col_p]
            for i in range(m + 1):
                if i != row_p:
                    T[i] -= T[i, col_p] * T[row_p]
            
            pasos.append(OptimizerModel._fmt_tableau(
                T, base, col_names, it + 1, artificiales, c_display))
        else:
            return "no acotado", None, None, pasos

        for ai in artificiales:
            for i, bi in enumerate(base):
                if bi == ai and abs(T[i, -1]) > 1e-6:
                    return "no factible", None, None, pasos

        x = np.zeros(n + n_s + n_a)
        for i, bi in enumerate(base):
            x[bi] = T[i, -1]
        valor = T[m, -1] if maximize else -T[m, -1]
        return "optimo", valor, x[:n], pasos

    @staticmethod
    def _fmt_tableau(T, base, col_names, it, artificiales=None, c_full=None):
        """
        Retorna el diccionario de un tableau para la Vista.

        Claves del dict:
          it        – número de iteración
          cols      – ["Vb", "Cb", "x1", ..., "RHS"]
          rows      – filas de datos (sin fila Z):
                      cada fila = [nombre_base, cb_val, a_i1, ..., a_in, bi]
          c_header  – [cj de cada columna de variable, sin RHS]
          zj        – [Zj de cada columna, incluida RHS]
          cj_zj     – [Cj-Zj de columnas de variable, None para RHS]
        """
        artificiales = artificiales or []
        m      = T.shape[0] - 1
        n_vars = T.shape[1] - 1        # columnas sin RHS

        # --- Cb: coeficiente objetivo de cada variable básica ---
        cb_vals = []
        for bi in base:
            val = float(c_full[bi]) if (c_full is not None and bi < len(c_full)) else 0.0
            cb_vals.append(val)

        # --- Zj = Σ(Cb_i · T[i, j])  para cada columna j (incluye RHS) ---
        zj = []
        for j in range(n_vars + 1):
            zj_j = sum(cb_vals[i] * float(T[i, j]) for i in range(m))
            zj.append(zj_j)

        # --- Cj − Zj  (None en columna RHS) ---
        cj_zj = []
        for j in range(n_vars):
            cj = float(c_full[j]) if (c_full is not None and j < len(c_full)) else 0.0
            cj_zj.append(cj - zj[j])
        cj_zj.append(None)      # RHS no tiene Cj-Zj

        # --- Fila de encabezado cj (solo columnas de variable, sin RHS) ---
        c_header = []
        if c_full is not None:
            c_header = [float(c_full[j]) for j in range(n_vars)]

        # --- Filas de datos ---
        rows = []
        for i in range(m):
            b_name = col_names[base[i]] if base[i] < len(col_names) - 1 else "?"
            if base[i] in artificiales:
                b_name += "(A)"
            row_data = [b_name, float(cb_vals[i])] + [float(v) for v in T[i, :]]
            rows.append(row_data)

        return {
            "it":       it,
            "cols":     ["Vb", "Cb"] + col_names,   # col_names ya incluye "RHS"
            "rows":     rows,
            "c_header": c_header,
            "zj":       zj,
            "cj_zj":    cj_zj,
            "pivot":    None  # Se llenará en el bucle principal si hay iteración siguiente
        }