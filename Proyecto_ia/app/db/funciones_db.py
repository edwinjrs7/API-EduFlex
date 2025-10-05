
from .database import Estudiante, PrediccionEstilo, RecursosRecomendados, get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def guardarRecursos(db : Session = Depends(get_db), recursos=None):
    
    guardar_recursos = RecursosRecomendados(
        prediccion_id = db.query(PrediccionEstilo).order_by(PrediccionEstilo.id.desc()).first().id,
        recursos = recursos
    )
    
    db.add(guardar_recursos)
    db.commit()
    db.refresh(guardar_recursos)
    
    return recursos
    