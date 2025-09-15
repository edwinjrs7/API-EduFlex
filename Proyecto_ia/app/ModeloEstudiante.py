import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score
from typing import List

class ModeloPerfilEstudiantil:
    
    def __init__(self, filename, data_modelpath="modelStudent.pk"):
        self.filename = filename
        self.data_modelpath = data_modelpath
        self.model = RandomForestClassifier(max_depth= 10, min_samples_split=10,random_state=420,n_estimators=400)  # Árbol de decisión
        self.answers = {'Visual': 0, 'Reading/Writing': 1, 'Kinesthetic': 2, 'Auditory': 3}
        self.questions = [
    {
        "text": "¿Qué método prefieres para aprender algo nuevo?",
        "options": ["Ver un video explicativo", "Leer un manual o guía", "Hacerlo tú mismo", "Escuchar una explicación"],
        "mapping": {
            "Ver un video explicativo": 0,
            "Leer un manual o guía": 1,
            "Hacerlo tú mismo": 2,
            "Escuchar una explicación": 3
        }
    },
    {
        "text": "¿Qué te resulta más útil al repasar una clase?",
        "options": ["Esquemas, diagramas o imágenes", "Apuntes escritos o resúmenes", "Repetir la práctica o ejercicios", "Escuchar audios o explicaciones orales"],
        "mapping": {
            "Esquemas, diagramas o imágenes": 0,
            "Apuntes escritos o resúmenes": 1,
            "Repetir la práctica o ejercicios": 2,
            "Escuchar audios o explicaciones orales": 3
        }
    },
    {
        "text": "¿Qué haces primero cuando no entiendes algo?",
        "options": ["Busco un gráfico o video", "Releo mis apuntes o un libro", "Pruebo hacerlo por mí mismo", "Le pido a alguien que me lo explique"],
        "mapping": {
            "Busco un gráfico o video": 0,
            "Releo mis apuntes o un libro": 1,
            "Pruebo hacerlo por mí mismo": 2,
            "Le pido a alguien que me lo explique": 3
        }
    },
    {
        "text": "¿Cómo prefieres estudiar para un examen?",
        "options": ["Mirando mapas mentales o videos", "Releyendo y subrayando el texto", "Haciendo ejercicios o prácticas", "Explicando en voz alta o escuchando"],
        "mapping": {
            "Mirando mapas mentales o videos": 0,
            "Releyendo y subrayando el texto": 1,
            "Haciendo ejercicios o prácticas": 2,
            "Explicando en voz alta o escuchando": 3
        }
    },
    {
        "text": "¿Qué herramienta usarías en una presentación?",
        "options": ["Infografías o imágenes", "Diapositivas con texto", "Demostraciones prácticas", "Grabación de audio o narración"],
        "mapping": {
            "Infografías o imágenes": 0,
            "Diapositivas con texto": 1,
            "Demostraciones prácticas": 2,
            "Grabación de audio o narración": 3
        }
    }
]

        
    
    def preprocess_data(self):
       
       #se carga el archivo 
       df = pd.read_csv(self.filename)
       
       #Seleccionamos las Columnas que queremos usar y eliminamos los valores nulos
       df['Use_of_Educational_Tech'] = df['Use_of_Educational_Tech'].map({'Yes': 0, 'No': 1})
       df['Final_Grade'] = df['Final_Grade'].map({'A': 0, 'B': 1, 'C': 2, 'D': 3})

       selected_columns = ['Study_Hours_per_Week', 'Use_of_Educational_Tech','Online_Courses_Completed','Preferred_Learning_Style','Final_Grade']
       df = df[selected_columns].dropna()
       
       #mapear estilo de aprendizaje 
       df['Preferred_Learning_Style'] = df['Preferred_Learning_Style'].map(self.answers)
       
       # Separar características y etiqueta
       X = df[['Study_Hours_per_Week', 'Use_of_Educational_Tech', 'Online_Courses_Completed','Final_Grade']]
       y = df['Preferred_Learning_Style']
       
       #entrenamiento con datos sinteticos
       df_sint = pd.read_csv('app/synthetic_dataset.csv')
       df_sint = df_sint[selected_columns].dropna()
       df_sint['Preferred_Learning_Style'] = df_sint['Preferred_Learning_Style'].map(self.answers)
       df_sint['Use_of_Educational_Tech'] = df_sint['Use_of_Educational_Tech'].map({'Yes': 0, 'No': 1})
       
       df_total = pd.concat([df, df_sint], ignore_index=True)

       X = df_total[['Study_Hours_per_Week', 'Use_of_Educational_Tech', 'Online_Courses_Completed','Final_Grade']]
       y = df_total['Preferred_Learning_Style']

       # Dividir en entrenamiento y prueba
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
       
       print(df_total['Preferred_Learning_Style'].value_counts())
       return X_train, X_test, y_train, y_test
   
    def ask_questions(self, user_choices: List[int]):
        if len(user_choices) != len(self.questions):
            raise ValueError(f"Se esperaban {len(self.questions)} respuestas, pero se recibieron {len(user_choices)}.")
        answers =[]
        
            
        for idx, (q, choice) in enumerate(zip(self.questions, user_choices)):
                
            if not 1 <= choice <= 4:
                raise ValueError(f"La opción {choice} no es válida para la pregunta {idx + 1}. Debe estar entre 1 y 4.") 
            selected = q["options"][choice - 1]
            answers.append(q["mapping"][selected])
        return answers
    
    def linking_answers(self, answers):
        #respuestas Obtenidas
        visual = answers.count(0)
        teorico = answers.count(1)
        practico = answers.count(2)
        auditivo = answers.count(3)
        
        #relacionamos las respuestas 
        study_hours = 5 + (practico * 10) + (teorico * 2)
        study_hours = min(study_hours, 49) #mas horas de estudio = más practico
        
        tech_use = 1 if visual + auditivo >= 1 else 0
        
        base_courses = 3
        courses_completed = base_courses + (teorico * 3) + (visual * 2) # los que les gusta la teoria tienden a terminar mas cursos
        courses_completed = min(base_courses + (teorico * 3) + (visual * 2), 20)
        
        final_grade = 60 + (practico * 5) + (visual * 2) + (teorico * 3)
        final_grade = min(final_grade, 100)

        
        return study_hours, tech_use, courses_completed, final_grade
    
    
        
    def predict_from_answers(self, user_choices: List[int])-> str:
        
        user_answers = self.ask_questions(user_choices)
        study_hours , tech_use, courses_completed, final_grade = self.linking_answers(user_answers)
        # Organizar las características en el mismo orden que en el entrenamiento
        input_data = pd.DataFrame([[study_hours, tech_use, courses_completed, final_grade]],
                                columns=['Study_Hours_per_Week', 'Use_of_Educational_Tech', 'Online_Courses_Completed','Final_Grade'])

        prediction = self.model.predict(input_data)[0]

        reverse_answers = {v: k for k, v in self.answers.items()}
        return reverse_answers.get(prediction, "Desconocido")


    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        print(f"Precisión del modelo: {accuracy_score(y_test, y_pred):.2f}")
        print(confusion_matrix(y_test, y_pred))
        print(classification_report(y_test, y_pred, target_names=["Visual", "Reading/Writing", "Kinesthetic", "Auditory"]))


    def save_model(self):
        joblib.dump(self.model, self.data_modelpath)

    def load_model(self):
        self.model = joblib.load(self.data_modelpath)

# modelo = ModeloPerfilEstudiantil("app/student_performance_large_dataset.csv")

# X_train, X_test, y_train, y_test = modelo.preprocess_data()
# modelo.train(X_train, y_train)
# modelo.evaluate(X_test, y_test)
# # Recoger respuestas del usuario
# modelo.save_model()


# resultado = modelo.predict_from_answers()
# print(f"\n➡️  Tu estilo de aprendizaje principal es: {resultado}")




       

    
    


