import os
import json
import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .MotorRecomendaciones import MotorDeRecomendaciones

class MotorFreeCodeCamp(MotorDeRecomendaciones):
    
    def __init__(self, aprendizaje):
        super().__init__(aprendizaje)
        
       # Listado de JSONs traducidos al español (bloques principales)
        self.fcc_blocks = [
            "01-responsive-web-design",
            "02-javascript-algorithms-and-data-structures",
            "03-front-end-development-libraries",
            "04-data-visualization",
            "05-apis-and-microservices",
            "06-quality-assurance",
            "07-scientific-computing-with-python",
            "08-data-analysis-with-python",
            "09-information-security",
        ]
        self.base_url = (
            "https://raw.githubusercontent.com/freeCodeCamp/freeCodeCamp/main/"
            "curriculum/challenges/espanol/{}.json"
        )
        
    # descargar bloques para el json
    def download_block(self, block_name) -> list[dict]:
        url = self.base_url.format(block_name)
        
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("challenges", [])
        except Exception as exc:
            print(f' Error descargando {block_name}')
        return []


    def get_all_challenges(self) -> list[dict]:
        retos: list[dict] = []
        for blk in self.fcc_blocks:
            retos.extend(self.download_block(blk))
        return retos
    
    def construir_consulta(self, tema_curso):
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje, {})
        formato = np.random.choice(caracteristicas.get("format_preferences",["tutorial"]))
        keywords = np.random.choice(caracteristicas.get("keywords", []), size=min(2, len(caracteristicas.get("keywords",[]))), replace=False)
        return f"{tema_curso} {formato} {' '.join(keywords)}"   
    
    def recomendar_contenido(self, tema_curso, max_results= 5):
        retos = self.get_all_challenges()
        if not retos:
            return []
        
        recursos = []
        for ch in retos:
            recursos_id = ch.get("id", "")
            if recursos_id in self.historial_recomendaciones:
                continue
            
            recursos.append({
                "id": recursos_id,
                "title": ch.get("title", ""),
                "description": ch.get("description", ""),
                "url": f"https://www.freecodecamp.org/espanol/learn/{recursos_id}",
                "interactive": True,
            }) 
            
            self.historial_recomendaciones.append(recursos_id)
        
        ejercicios_rankeados = self.ranking(recursos, tema_curso)
            
        return ejercicios_rankeados[:max_results]
    
    def ranking(self, recursos, tema_curso):
        
        if not recursos:
            return []
        
        keywords = self.caracteristcas_aprendizaje.get(self.aprendizaje, {}).get("keywords", [])
        corpus = [f"{r['title']} {r['description']}" for r in recursos]
        corpus.append(" ".join(keywords + [tema_curso]))
        
        vect = TfidfVectorizer(stop_words="english")
        matriz = vect.fit_transform(corpus)
        sims = cosine_similarity(matriz[:-1], matriz[-1:])

        for i, rec in enumerate(recursos):
            rec["score"] = sims[i][0] + 0.1  # bonus fijo por ser interactivo

        return sorted(recursos, key=lambda r: r["score"], reverse=True)
        
    def recomendar_planCompleto(self, tema_curso, max_results= 5):
        subtemas = self.generar_subtemas(tema_curso)
        recursos_por_subtema = {}
        for sub in subtemas:
            recursos = self.recomendar_contenido(f"{tema_curso} {sub}", max_results=2)
            if recursos:
                recursos_por_subtema[sub] = recursos

        curso = {
            "tema_principal": tema_curso,
            "estilo_aprendizaje": self.aprendizaje,
            "subtemas": recursos_por_subtema,
            "recomendacion_general": self.generarConsejosPersonalizados(),
        }   
        
        return curso     
        