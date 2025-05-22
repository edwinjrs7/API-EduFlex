import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .MotorRecomendaciones import MotorDeRecomendaciones

#creamos la clase del buscador de youtube en cual hereda de la clase padre MotorDeRecomendaciones
class RecomendadorCursosYoutube(MotorDeRecomendaciones):
    
    def __init__(self, aprendizaje, api_key = None):
        super().__init__(aprendizaje)
        
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY", "AIzaSyBYlWdnwinkG5HwZIOD1GWzKrSEmAE7xkA")
        
        if not self.api_key:
            return f'Advertencia: No se ha proporcionado una API Key para Youtube. Algunas funciones pueden no estar disponible.'
    
    # Metodo que realiza una consulta optimizada para youtube
    def construir_consulta(self, tema_curso):
        """
        Construye una consulta optimizada para YouTube basada en el tema del curso y estilo de aprendizaje.
        
        Args:
            tema_curso (str): Tema específico que el estudiante quiere aprender
            
        Returns:
            str: Consulta optimizada para búsqueda en YouTube
        """
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje,{})
        formato = np.random.choice(caracteristicas.get('format_preferences',['tutorial']))
        keywords = np.random.choice(caracteristicas.get('keywords',[]), 2,replace=False)
        
        # Construir consulta con las palabras claves
        consulta = f"{tema_curso} {formato} {' '.join(keywords)}"
        return consulta
    
    # Metodo que recomienda un Video de Youtube    
    def recomendar_contenido(self, tema_curso, max_results=5):
        """
        Este metodo se encarga de recomendar contenido de Youtube relacionados con un tema especifico, adaptados al tipo de aprendizaje.
        
        Args:
            tema_curso (str): Tema especíco sobre el estudiante quiere aprender
            max_results (int): Número máximo de resultados a devolver
            
        Returns:
            list: Lista de diccionarios con información de los videos recomendados
        """
        
        if not self.api_key:
            pass
        
        try:
            # Construir el servicio de YouTube
            youtube = build('youtube', 'v3', developerKey= self.api_key)
            
            # Construir la consulta optimizada para el estilo de aprendizaje
            consulta = self.construir_consulta(tema_curso)
            
            # Realizar la búsqueda
            request = youtube.search().list(
                q=consulta,
                part='snippet',
                type='video',
                videoDefinition='high',
                relevanceLanguage= 'es',
                maxResults=max_results*2
            )
            response = request.execute()
            
            # Procesar y filtrar los resultados
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                
                # Obtener detalles adicionales del video
                video_request = youtube.videos().list(
                    part='contentDetails,statistics',
                    id=video_id
                )
                
                video_response = video_request.execute()
                
                if video_response['items']:
                    video_details = video_response['items'][0]
                    
                    # Extraer duración vistas, me gusta, etc.
                    duration = video_details['contentDetails'].get('duration','PT0M0S')
                    view_count = int(video_details['statistics'].get('viewCount', 0))
                    like_count = int(video_details['statistics'].get('likeCount', 0))
                    
                    # Solo incluir si no está en el historial
                    if video_id not in self.historial_recomendaciones:
                        videos.append({
                            'id': video_id,
                            'title' : item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'thumbnail': item['snippet']['thumbnails']['high']['url'],
                            'channel_title': item['snippet']['channelTitle'],
                            'published_at': item['snippet']['publishedAt'],
                            'duration': duration,
                            'view_count': view_count,
                            'like_count': like_count,
                            'url': f"https://www.youtube.com/watch?v={video_id}"
                        })
                        
                        # Agregar al historial
                        self.historial_recomendaciones.append(video_id)

            # Realizar ranking final basado en relevancia para el estilo de aprendizaje 
            videos_rankeados = self.ranking(videos, tema_curso)
            
            return videos_rankeados[:max_results]            
        except HttpError as e:
            return f"No se encontraron Recursos"
        
    def ranking(self, videos, tema_curso):
        """
        Rankea los videos basándose en su relevancia para el estilo de aprendizaje y tema.
        
        Args:
            videos (list): Lista de videos a rankear
            tema_curso (str): Tema del curso
            
        Returns:
            list: Lista de videos rankeados
        """
        if not videos:
            return []
        
        # Obtener características del estilo de aprendizaje
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje, {})
        keywords = caracteristicas.get('keywords', [])
        
        # Crear corpus para TF-IDF
        corpus = [f"{v['title']} {v['description']}" for v in videos]
        corpus.append(" ".join(keywords + [tema_curso]))
        
        # Vectorizar y calcular similitud
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calcular similitud del coseno entre cada video y las keywords del estilo
        cosine_similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:])
        
        # Crear puntaje ponderado (similitud + estadísticas)
        for i, video in enumerate(videos):
            # Normalizar valores
            view_factor = min(video['view_count'] / 10000, 5)  # Max 5 puntos por vistas
            like_ratio = video['like_count'] / max(video['view_count'] * 0.01, 1)  # % de likes
            
            # Puntaje final ponderado
            videos[i]['score'] = (
                cosine_similarities[i][0] * 0.6 +  # Similitud de contenido (60%)
                view_factor * 0.2 +               # Popularidad (20%)
                like_ratio * 0.2                  # Calidad percibida (20%)
            )
        
        # Ordenar por puntaje
        return sorted(videos, key=lambda x: x['score'], reverse=True)
        
    def recomendar_planCompleto(self, tema_curso):
        """
        Recomienda un curso completo basado en el estilo de aprendizaje, combinando varios videos
        que cubren diferentes aspectos del tema.
        
        Args:
            tema_curso (str): Tema principal del curso
            
        Returns:
            dict: Información sobre el curso recomendado con lista de videos
        """
        # Determinar subtemas basados en el tema principal
        subtemas = self.generar_subtemas(tema_curso)
        
        # Obtener videos para cada subtema
        videos_por_subtema = {}
        for subtema in subtemas:
            videos = self.recomendar_contenido(f"{tema_curso} {subtema}", max_results= 2)
            if videos:
                videos_por_subtema[subtema] = videos
            
        curso = {
            'tema_principal': tema_curso,
            'estilo_aprendizaje': self.aprendizaje,
            'subtemas': videos_por_subtema,
            'recomendacion_general': self.generarConsejosPersonalizados()
        }
        
        return curso
    
    
            
        
        
        
        
    
        
    
