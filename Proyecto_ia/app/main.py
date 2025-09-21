from .ModeloEstudiante import ModeloPerfilEstudiantil
from sqlalchemy.orm import Session
from .recomendador.MotorYoutube import RecomendadorCursosYoutube
from .recomendador.MotorBooks import RecomendadorDeLibros
from .recomendador.MotorSpotify import MotorSpotify
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from .db import database
from .db.database import Estudiante, PrediccionEstilo,RecursosRecomendados, get_db
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
def predecir_estilo(respuestas_usuario : RespuestasUsuario,db: Session = Depends(get_db)):
    global ultimo_estilo_predicho
    estilo = Modelo_estudiante.predict_from_answers(respuestas_usuario.respuestas)
    ultimo_estilo_predicho = estilo
    
    nueva_pred = database.PrediccionEstilo(
        estudiante_id = None,
        estilo_aprendizaje = estilo,
        respuesta = json.dumps(respuestas_usuario.respuestas)
        
    )
    
    db.add(nueva_pred)
    db.commit()
    db.refresh(nueva_pred)
    
    return {"estilo_aprendizaje": ultimo_estilo_predicho}

@app.get("/plan_completo")
def obtener_plan(db: Session = Depends(get_db)):
    if not ultimo_estilo_predicho:
        return {"error": "Primero debes enviar respuestas al endpoint /predecir_estilo"}
    estilo_aprendizaje = ultimo_estilo_predicho
    if estilo_aprendizaje in ('Visual','Kinesthetic'):
        youtube = RecomendadorCursosYoutube(estilo_aprendizaje)
        plan_visual = youtube.recomendar_planCompleto('python')
        print(plan_visual)
        guardar_recursos = database.RecursosRecomendados(
            prediccion_id = db.query(PrediccionEstilo).order_by(PrediccionEstilo.id.desc()).first().id,
            recursos = plan_visual
        )
        
        db.add(guardar_recursos)
        db.commit()
        db.refresh(guardar_recursos)
        
        return plan_visual
    elif estilo_aprendizaje == 'Reading/Writing':
        books = RecomendadorDeLibros(estilo_aprendizaje)
        plan_teorico = books.recomendar_planCompleto('python')
        print(plan_teorico)
        guardar_recursos = database.RecursosRecomendados(
            prediccion_id = db.query(PrediccionEstilo).order_by(PrediccionEstilo.id.desc()).first().id,
            recursos = plan_teorico
        )
        
        db.add(guardar_recursos)
        db.commit()
        db.refresh(guardar_recursos)
        
        return plan_teorico
    elif estilo_aprendizaje == 'Auditory':
        spotify = MotorSpotify(estilo_aprendizaje)
        plan_auditivo = spotify.recomendar_planCompleto('python')
        print(plan_auditivo)
        guardar_recursos = database.RecursosRecomendados(
            prediccion_id = db.query(PrediccionEstilo).order_by(PrediccionEstilo.id.desc()).first().id,
            recursos = plan_auditivo
        )
        
        db.add(guardar_recursos)
        db.commit()
        db.refresh(guardar_recursos)
        return plan_auditivo
    else:
        return f'No se pudo determinar un estilo de aprendizaje'
    
    


