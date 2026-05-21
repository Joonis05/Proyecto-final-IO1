import numpy as np

class OptimizerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        # Enlazamos el controlador con la vista
        self.view.set_controller(self)

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.view.mainloop()

    def solve(self):
        """Obtiene datos de la vista, llama al modelo y actualiza la vista."""
        try:
            # 1. Obtener entradas desde la Vista
            c, A, b, tipos, maximizar, metodo = self.view.get_inputs()

            # 2. Validaciones básicas
            if np.any(b < 0):
                self.view.display_warning(
                    "RHS negativo",
                    "Uno o más RHS son negativos.\n"
                    "Multiplique esa restricción por -1 e invierta el tipo.")
                return

            if metodo == "Simplex":
                if any(t != "<=" for t in tipos):
                    self.view.display_warning(
                        "Simplex Normal",
                        "El Simplex normal solo admite restricciones ≤.\n"
                        "Cambie a Gran M para usar ≥ o =.")
                    return
                # 3. Llamar al Modelo
                estado, valor, x, pasos = self.model.simplex_normal(c, A, b, maximizar)
            else:
                # 3. Llamar al Modelo
                estado, valor, x, pasos = self.model.gran_m(c, A, b, tipos, maximizar)

            # 4. Actualizar la Vista
            self.view.display_result(estado, valor, x, pasos, metodo)

        except ValueError:
            self.view.display_error(
                "Error de entrada",
                "Verifique que todos los campos contengan números válidos.")
        except Exception as ex:
            self.view.display_error("Error", str(ex))
