from openai import OpenAI
import json
from ..db.database import Estudiante, MemoriaFlexi, get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
api_key = "AIzaSyCGU7h1m3Hmi2ozEm1dGmGU2XIcpBtPOPY"
base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
client = OpenAI(api_key = api_key, base_url= base_url)


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