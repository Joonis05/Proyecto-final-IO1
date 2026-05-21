from model import OptimizerModel
from view import OptimizerView
from controller import OptimizerController

if __name__ == "__main__":
    # Inicialización de la arquitectura MVC
    model = OptimizerModel()
    view = OptimizerView()
    controller = OptimizerController(model, view)
    
    # Iniciar la aplicación
    controller.run()
