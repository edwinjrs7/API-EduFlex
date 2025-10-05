from openai import OpenAI, RateLimitError
import json
from ..db.database import Estudiante, MemoriaFlexi, get_db
from ..config.config import API_KEYS
from ..key_master.key_master import KeyMaster
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import  HTTPException 


ApiKeyMaster = KeyMaster(API_KEYS) 
client = ApiKeyMaster.ObtenerCLiente()


def organizador_de_cursos(curso_creado):
    prompt = f"""
    Eres un experto en educación online. 
    A continuación te paso un curso en formato JSON:

    {json.dumps(curso_creado, indent=2, ensure_ascii=False)}

    Tu tarea:
    - Filtra y organiza el contenido en un formato estructurado y coherente.
    - Elimina contenido duplicado, irrelevante o que no aporte valor.
    - Respeta los módulos o subtemas (Instalación, sintaxis básica, estructuras de datos, algoritmos, patrones de diseño).
    - Devuélvelo en **exactamente el mismo formato JSON**.
    """
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages= [
            {"role": "system","content": "Eres un asistente experto en la organización de cursos online."},
            {"role":"user", "content": prompt}
        ],
        response_format= {"type":"json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def flexi(db: Session, session_id: str ,mensaje: str, temperatura=0.7, max_tokens=1024):
    try:
    
        new_msg = MemoriaFlexi(
            session_id = session_id,
            estudiante_id = None,
            role = "user",
            content = mensaje
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        
        historial = db.execute(
            select(MemoriaFlexi).where(MemoriaFlexi.session_id == session_id)
        ).scalars().all()
        
        mensajes = [{"role": "system","content": "Eres Flexi, un asistente amigable y servicial que ayuda a los estudiantes con sus dudas académicas. Responde de manera clara y concisa."}]
        for msg in historial:
            mensajes.append({"role": msg.role, "content": msg.content})
        
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages= mensajes, 
            temperature= temperatura,
            max_tokens= max_tokens
        )
        
        respuesta_flexi = response.choices[0].message.content
        
        new_msg = MemoriaFlexi(
            session_id = session_id,
            estudiante = None,
            role = "assistant",
            content = respuesta_flexi
        )
        
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        
        return respuesta_flexi
    except RateLimitError:
        ApiKeyMaster.cambioDeKey()
        try:
            flexi(db, session_id, mensaje, temperatura, max_tokens)
        except Exception as e:
            raise HTTPException(status_code = 429, detail="Se ha Exedido el limite de peticiones a Flexi. Por favor, intenta más tarde.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, intenta más tarde.")   
        