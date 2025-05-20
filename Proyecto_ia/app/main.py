from .ModeloEstudiante import ModeloPerfilEstudiantil

from .recomendador.MotorYoutube import RecomendadorCursosYoutube
from .recomendador.MotorBooks import RecomendadorDeLibros
from .recomendador.MotorSpotify import MotorSpotify
from fastapi import FastAPI


app = FastAPI()

file = 'app/student_performance_large_dataset.csv'
Modelo_estudiante = ModeloPerfilEstudiantil(file)
X_train, X_test, y_train, y_test = Modelo_estudiante.preprocess_data()
Modelo_estudiante.train(X_train, y_train)
Modelo_estudiante.evaluate(X_test, y_test)

@app.get("/plan_completo")
def obtener_plan():
    estilo_aprendizaje = Modelo_estudiante.predict_from_answers()
    if estilo_aprendizaje == "Visual":
        youtube = RecomendadorCursosYoutube(estilo_aprendizaje)
        plan_visual = youtube.recomendar_planCompleto('python para principiantes')
        print(plan_visual)
        return plan_visual
    elif estilo_aprendizaje == 'Reading/Writing':
        books = RecomendadorDeLibros(estilo_aprendizaje)
        plan_teorico = books.recomendar_planCompleto('python')
        print(plan_teorico)
        return plan_teorico
    else:
        spotify = MotorSpotify(estilo_aprendizaje)
        plan_auditivo = spotify.recomendar_planCompleto('ingles')
        print(plan_auditivo)
        return plan_auditivo


