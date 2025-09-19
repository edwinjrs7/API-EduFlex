from abc import ABC, abstractmethod
from openai import OpenAI
import json



class MotorDeRecomendaciones(ABC):
    
    def __init__(self, aprendizaje):
        
        #se recibe el tipo de aprendizaje que arrojo el modelo de inteligencia artificial
        self.aprendizaje = aprendizaje
        
        #Mapeo de estilos de aprendizaje a palabras clave y caracteristicas de búsqueda
        self.caracteristcas_aprendizaje = {
            'Visual': {
                'keywords': ['', 'diagramas', 'gráficos', 'mapas mentales'],
                'topic_preferences': ['animación', 'visualización', 'mapa conceptual'],
                'format_preferences': ['video tutorial', 'curso', 'guia paso a paso']
            },
            
            'Reading/Writing': {
                'keywords': ['documentación', 'artículos', 'manual', 'introducción a'],
                'topic_preferences': ['explicación detallada', 'notas de estudio'],
                'format_preferences': ['artículo', 'guía escrita', 'documento PDF']
            },
            'Kinesthetic': {
                'keywords': ['ejercicios prácticos', 'tutorial interactivo', 'aprendizaje práctico'],
                'topic_preferences': ['proyectos', 'demos', 'workshops'],
                'format_preferences': ['proyecto paso a paso', 'hands-on tutorial']
            },
            'Auditory': {
                
                'keywords': ['explicación', 'entrevista', 'conversación', 'episodio'],
                'format_preferences': ['podcast', 'audio', 'episodio'],

                'topic_preferences': [
                    'entrevistas', 'episodios educativos', 'explicaciones orales',
                    'audiolibros', 'historias educativas', 'diálogos', 'lecturas en voz alta'
                ],
                'format_preferences': [
                    'audiolibro', 'episodio', 'entrevista', 'lección hablada', 'contenido en audio'
                ]
            }

        }
        
        # Historial de recomendaciones para evitar repeticiones 
        self.historial_recomendaciones = []
        
        
        
        
            
        
        
        
        
    #Metodos Abstractos que aplicaran polimorfismo a la hora de usarse en las clases de los motores 
    @abstractmethod
    def recomendar_contenido(self, tema_curso):
        pass
    
    @abstractmethod
    def construir_consulta(self, tema_curso):
        pass
    
    @abstractmethod
    def recomendar_planCompleto(self, tema_curso):
        pass
    
    @abstractmethod
    def ranking(self,contenido, tema_curso):
        pass
    
   
    
    #Metodo que genera subtemas
    def generar_subtemas(self, tema_curso):
        """
        Esta función genera subtemas relevantes para un curso completo sobre el tema principal.
        
        Args:
            tema_curso (str): Tema principal del curso
        
        Returns:
            list: Lista de subtemas recomendados
        """
        
        #subtemas generales que funcionan para la mayoria de temas
        subtemas_genericos = [
            "introducción",
            "conceptos básicos",
            "fundamentos",
            "técnicas avanzdas",
            "aplicaciones prácticas",
            "ejercicios",
            "ejemplos",
            "casos de estudio"
        ]
        
        subtemas_especiales = []
        
        #palabras clave de tecnología y programación
        if any(palabra in tema_curso.lower() for palabra in ["programación", "código", "python", "javascript","java","php","web","desarrollo"]):
            subtemas_especiales =[
                "instalación",
                "sintaxis básica",
                "estructuras de datos",
                "algoritmos",
                "patrones de diseños",
                "proyectos prácticos"
            ]
        # Palabras clave de idiomas    
        elif any(palabra in tema_curso.lower() for palabra in ["inglés", "español", "francés", "idioma", "lengua"]):
            subtemas_especiales = [
                "vocabulario básico",
                "gramática",
                "conversación",
                "pronunciación",
                "lectura",
                "escritura"
            ]
        
        # Palabras clave de matemáticas o ciencias
        elif any(palabra in tema_curso.lower() for palabra in ["matemáticas", "física", "química", "biología", "cálculo"]):
            subtemas_especiales = [
                "fórmulas básicas",
                "teoría fundamental",
                "resolución de problemas",
                "aplicaciones prácticas",
                "ejercicios resueltos"
            ]
            
        # Se devuelven los subtemas especiales si existen o lo subtemas generales
        return subtemas_especiales or subtemas_genericos
    
    # Metodo que genera consejos personalizados
    def generarConsejosPersonalizados(self):
        """
        Genera una recomendación personalizado según el estilo de aprendizaje.
        
        Returns: 
          str: Consejos personalizados
        """
        
        # consejos personalizados
        consejos = {
            'Visual': "Para aprovechar al máximo estos videos, toma capturas de pantalla de los diagramas importantes, crea tus propios mapas mentales y busca recursos adicionales con gráficos. Pausa el video cuando aparezcan elementos visuales importantes para analizarlos en detalle.",
            
            'Reading/Writing': "Te recomendamos tomar notas detalladas sobre estos libros. Ten en cuenta las palabras clave y considera investigarlos más a fondo. Después, escribe resúmenes con tus propias palabras y busca artículos complementarios sobre cada tema.",
            
            'Kinesthetic': "Para maximizar tu aprendizaje, intenta seguir los ejemplos prácticos al mismo tiempo que los ves. Haz pausas para practicar cada concepto antes de continuar. Es importante que apliques lo aprendido en proyectos propios después de cada video.",
            
            'Auditory': "Estos videos tienen explicaciones verbales claras. Considera escucharlos primero sin mirar la pantalla, centrado en el audio. También puedes grabar tu propia voz repitiendo conceptos clave para reforzar el aprendizaje."
        }
        
        return consejos.get(self.aprendizaje,
                           "Toma notas y practica activamente lo que aprendas en estos videos.")
    
    
    
        
        
    
    
        