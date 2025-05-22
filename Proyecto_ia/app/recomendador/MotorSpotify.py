import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .MotorRecomendaciones import MotorDeRecomendaciones


class MotorSpotify(MotorDeRecomendaciones):
    def __init__(self, aprendizaje):
        super().__init__(aprendizaje)
        
        # Keys para obtener el token de la api de spotify 
        self.clientID = 'f68eeb5fc6d9486da032ef909d89b988'
        self.secretClientID = '6605efc09d1a411cade408a01721a58e'
        self.accessToken = self.obtenerTokenAcceso()
       
    def obtenerTokenAcceso(self):
        
        # url de la api de acceso
        url = 'https://accounts.spotify.com/api/token'
        
        # Headers & data
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type':'client_credentials',
                'client_id': self.clientID,
                'client_secret': self.secretClientID}
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()['access_token'] 
    
    def construir_consulta(self, tema_curso):
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje,{})
        formato = np.random.choice(caracteristicas.get('format_preferences', ['audiolibro']))
        keyword = np.random.choice(caracteristicas.get('keywords',[]),2,replace=False)
        
        consulta = f"{tema_curso} {formato} {' '.join(keyword)}"
        
        return consulta
    
    def recomendar_contenido(self, tema_curso, max_results=5):
        consulta = self.construir_consulta(tema_curso)
        url = 'https://api.spotify.com/v1/search'
        
        params = {
            "q": consulta,
            "type": "episode",
            "limit": max_results * 2,
            "market": "ES"
        }
        headers = {
            "Authorization": f"Bearer {self.accessToken}"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"⚠️ Error: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        items = data.get('episodes', {}).get('items', [])
        
        episodios = []
        
        for item in items:
            episode_id = item['id']
            name = item.get('name', '')
            description = item.get('description', '')
            podcast_url = item.get('external_urls', {}).get('spotify', '')
            thumbnail = item.get('images', [{}])[0].get('url', '')
            show_name = item.get('show', {}).get('name', '')
            
            if episode_id not in self.historial_recomendaciones:
                episodios.append({
                    'id': episode_id,
                    'title': name,
                    'description': description,
                    'show': show_name,
                    'url': podcast_url,
                    'thumbnail': thumbnail,
                    'media_type': "episode"
                })
                self.historial_recomendaciones.append(episode_id)
        
        episodios_rankeados = self.ranking(episodios, tema_curso)
        return episodios_rankeados[:max_results]

            
    def ranking(self, audios, tema_curso):
        
        if not audios:
            return []
        
        # Obtenemos caracteristicas del estilo de aprendizaje
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje,{})
        keywords = caracteristicas.get('keywords',[])
        
        #creamos corpus TF-IDF
        corpus = [f"{ad['title']} {ad['description']}" for ad in audios]
        corpus.append(" ".join(keywords + [tema_curso]))
        
        # Vectorizar y calcular similitud
        vectorizer = TfidfVectorizer  (stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculamos la similitud del coseno entre cada audio y las keywords del estilo
        cosine_similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:]) 
        
        # Creamos un puntaje ponderado ( similitud + estadisticas)
        for i, audio in enumerate(audios):
            popularity = audio.get('popularity', 0) / 100
            duration_min = audio.get('duration_ms', 0) / 60000
            dur_factor = 1 if 10 <= duration_min <= 60 else 0.5  # rango ideal

            # Score final ponderado
            audio['score'] = (
                cosine_similarities[i][0] * 0.6 +   # similitud semántica
                popularity * 0.25 +                 # popularidad normalizada
                dur_factor * 0.15                   # duración adecuada
            )
             
        return sorted(audios, key=lambda x: x['score'], reverse=True)
    
    def recomendar_planCompleto(self, tema_curso):
        
        #Determinar subtemas basados en el tema principal 
        subtemas = self.generar_subtemas(tema_curso)
        
        # Obtener libros para cada subtema
        audio_por_subtema = {}
        for subtema in subtemas:
            audios = self.recomendar_contenido(f"{tema_curso} {subtema}", max_results=2)
            if audios:
                audio_por_subtema[subtema] = audios
                
        curso = {
            'tema_principal': tema_curso,
            'estilo_aprendizaje': self.aprendizaje,
            'subtemas': audio_por_subtema,
            'recomendacion_general': self.generarConsejosPersonalizados()
        }
            
        return curso