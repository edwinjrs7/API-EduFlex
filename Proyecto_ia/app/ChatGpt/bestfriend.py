from openai import OpenAI
import json
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