import requests
import numpy as np
from .MotorRecomendaciones import MotorDeRecomendaciones
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecomendadorDeLibros(MotorDeRecomendaciones):
    
    def __init__(self, aprendizaje):
        super().__init__(aprendizaje)
        
        self.api = 'https://www.googleapis.com/books/v1/volumes'
        
    def construir_consulta(self, tema_curso):
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje, {})
        formato = np.random.choice(caracteristicas.get('format_preferences', ['lecture']))
        keywords = np.random.choice(caracteristicas.get('keywords',[]),2,replace=False)
        
        consulta = f"{tema_curso} {formato} {' '.join(keywords)}"
        
        return consulta
    
    def recomendar_contenido(self, tema_curso, max_results = 5):
        
        # Se construye la Consulta
        consulta = self.construir_consulta(tema_curso)
        url = self.api
        params ={
            "q": consulta,
            # "filter": "free-ebooks",
            "printType": "books",
            "langRestrict": "es",
            'maxResults': max_results*2
        }
        
        response = requests.get(url,params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        # Procesar y filtrar los resultados
        libros = []
        for item in data.get('items',[]):
            libro_id = item['id']
            info = item['volumeInfo']
            
            # Obtenemos los datos de los libros
            title = info.get('title', '')
            description = info.get('description', '')
            authors = info.get('authors', [])
            rating = info.get('averageRating', 0)
            ratings_count = info.get('ratingsCount', 0)
            thumbnail = info.get('imageLinks', {}).get('thumbnail', '')
            preview_link = info.get('previewLink', '')
            
            # Solo incluimos si no está en el historial
            if libro_id not in self.historial_recomendaciones:
                libros.append({
                    'id': libro_id,
                    'title': title,
                    'description': description,
                    'authors': authors,
                    'rating': rating,
                    'ratings_count': ratings_count,
                    'thumbnail': thumbnail,
                    'url': preview_link
                })
                
            # Agregamos al historial
            self.historial_recomendaciones.append(libro_id)
        
        libros_rankeados = self.ranking(libros, tema_curso)
        
        # retornamos la recomendación
        return libros_rankeados[:max_results]
            
    def ranking(self, libros, tema_curso):
        
        if not libros:
            return []
        
        # Obtenemos caracteristicas del estilo de aprendizaje 
        caracteristicas = self.caracteristcas_aprendizaje.get(self.aprendizaje, {})
        keywords = caracteristicas.get('keywords', [])
        
        #creamos corpus TF-IDF
        corpus = [f"{lb['title']} {lb['description']}" for lb in libros ]
        corpus.append(" ".join(keywords + [tema_curso]))
        
        # Vectorizar y calcular similitud
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculamos la similitud del coseno entre cada libro y las keywords del estilo 
        cosine_similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:])     
        
        #crear puntaje ponderado (similitud + estadísticas)
        for i, libro in enumerate(libros):
            rating = libro.get('rating', 0)
            rating_count = libro.get('ratings_count', 0)
            
            #normalizamos valores
            rating_factor =  rating / 5
            count_factor = min(rating_count /50 , 1) 
            
            libros[i]['score'] = (
                cosine_similarities[i][0] * 0.6 +
                rating_factor * 0.2 +
                count_factor * 0.2
            )
        
        return sorted(libros, key=lambda x: x['score'], reverse=True)  
    
    def recomendar_planCompleto(self, tema_curso):
        
        # Determinar subtemas basados en el tema principal
        subtemas = self.generar_subtemas(tema_curso)
        
        # Obtener libros para cada subtema
        libro_por_subtema = {}
        for subtema in subtemas:
            libros = self.recomendar_contenido(f"{tema_curso} {subtema}", max_results=1)    
            if libros:
                libro_por_subtema[subtema] = libros
         
        # EStructurar el curso completo       
        curso = {
            'tema_principal': tema_curso,
            'estilo_aprendizaje': self.aprendizaje,
            'subtemas': libro_por_subtema,
            'recomendacion_general': self.generarConsejosPersonalizados()
        }
        
        return curso
                    