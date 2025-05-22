from .ModeloEstudiante import ModeloPerfilEstudiantil

from .recomendador.MotorYoutube import RecomendadorCursosYoutube
from .recomendador.MotorBooks import RecomendadorDeLibros
from .recomendador.MotorSpotify import MotorSpotify
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file = 'app/student_performance_large_dataset.csv'
Modelo_estudiante = ModeloPerfilEstudiantil(file)
X_train, X_test, y_train, y_test = Modelo_estudiante.preprocess_data()
Modelo_estudiante.train(X_train, y_train)
Modelo_estudiante.evaluate(X_test, y_test)
Modelo_estudiante.save_model()

# Entrada
class RespuestasUsuario(BaseModel):
    respuestas : List[int]

# Salida
class ResultadoEstilo(BaseModel):
    estilo_aprendizaje: str
   
ultimo_estilo_predicho =None
 
@app.post("/predecir_estilo", response_model=ResultadoEstilo)
def predecir_estilo(respuestas_usuario : RespuestasUsuario):
    global ultimo_estilo_predicho
    estilo = Modelo_estudiante.predict_from_answers(respuestas_usuario.respuestas)
    ultimo_estilo_predicho = estilo
    return {"estilo_aprendizaje": ultimo_estilo_predicho}

@app.get("/plan_completo")
def obtener_plan():
    if not ultimo_estilo_predicho:
        return {"error": "Primero debes enviar respuestas al endpoint /predecir_estilo"}
    estilo_aprendizaje = ultimo_estilo_predicho
    if estilo_aprendizaje in ('Visual','Kinesthetic'):
        youtube = RecomendadorCursosYoutube(estilo_aprendizaje)
        plan_visual = youtube.recomendar_planCompleto('python')
        print(plan_visual)
        return plan_visual
    elif estilo_aprendizaje == 'Reading/Writing':
        books = RecomendadorDeLibros(estilo_aprendizaje)
        plan_teorico = books.recomendar_planCompleto('python')
        print(plan_teorico)
        return plan_teorico
    elif estilo_aprendizaje == 'Auditory':
        spotify = MotorSpotify(estilo_aprendizaje)
        plan_auditivo = spotify.recomendar_planCompleto('python')
        print(plan_auditivo)
        return plan_auditivo
    else:
        return f'No se pudo determinar un estilo de aprendizaje'
       


