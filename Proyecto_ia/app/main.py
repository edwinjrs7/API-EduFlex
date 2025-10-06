from .ModeloEstudiante import ModeloPerfilEstudiantil
from sqlalchemy.orm import Session
from .recomendador.MotorYoutube import RecomendadorCursosYoutube
from .recomendador.MotorBooks import RecomendadorDeLibros
from .recomendador.MotorSpotify import MotorSpotify
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException 
from .db import database
from .db.database import Estudiante, PrediccionEstilo,RecursosRecomendados, get_db
from .db.funciones_db import guardarRecursos
from .ChatGpt.bestfriend import flexi
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EstudianteRegistro(BaseModel):
    id: int
    nombre:str
    apellido: str
    email: str
    edad: int 
    contraseña: str

class EstudianteLogin(BaseModel):
    nombre: str
    contraseña: str
    

# -------- Registro --------
@app.post("/registro")
def registrar_estudiante(data: EstudianteRegistro, db: Session = Depends(get_db)):
    estudiante = Estudiante(
        id=data.id,
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        edad=data.edad,
        contraseña=data.contraseña   # ⚠️ en un sistema real deberías hashear la contraseña

    )

    db.add(estudiante)
    try:
        db.commit()
        db.refresh(estudiante)
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nombre ya está registrado")

    return {"message": "Registro exitoso", "id": estudiante.id}

# -------- Login --------

@app.post("/login_estudiante")
def login_estudiante(data: EstudianteLogin, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.nombre == data.nombre).first()

    if not estudiante or estudiante.contraseña != data.contraseña:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"message": "Login exitoso", "id": estudiante.id, "nombre": estudiante.nombre}


file = 'Proyecto_ia/app/student_performance_large_dataset.csv'

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
        estudiante_id = db.query(Estudiante).order_by(Estudiante.id.desc()).first().id,
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
        guardarRecursos(db,plan_visual)
        
        return plan_visual
    elif estilo_aprendizaje == 'Reading/Writing':
        books = RecomendadorDeLibros(estilo_aprendizaje)
        plan_teorico = books.recomendar_planCompleto('python')
        print(plan_teorico)
        guardarRecursos(db,plan_teorico)
        return plan_teorico
    elif estilo_aprendizaje == 'Auditory':
        spotify = MotorSpotify(estilo_aprendizaje)
        plan_auditivo = spotify.recomendar_planCompleto('python')
        print(plan_auditivo)
        guardarRecursos(db, plan_auditivo)
        return plan_auditivo
    else:
        return f'No se pudo determinar un estilo de aprendizaje'
    
    
class MensajeEntrada(BaseModel):
    session_id: Optional[str] = None
    mensaje: str

class MensajeRespuesta(BaseModel):
    session_id: str
    mensaje: str
    
@app.post("/flexi", response_model=MensajeRespuesta)
async def conversa_con_flexi(mensaje_entrada: MensajeEntrada, db: Session = Depends(get_db)):
    
    if not mensaje_entrada.session_id:
        import uuid
        mensaje_entrada.session_id = str(uuid.uuid4())
        
    respuesta_flexi = flexi(db, mensaje_entrada.session_id, mensaje_entrada.mensaje)

    return {"session_id": mensaje_entrada.session_id, "mensaje": respuesta_flexi}
    
        
        

    


