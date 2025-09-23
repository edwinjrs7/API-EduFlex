from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, String, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends

DATABASE_URL= "mysql+pymysql://root:NbclgnjdjTtVEfRTqVIxlkrlmiItOYfY@interchange.proxy.rlwy.net:39042/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Estudiante(Base):
    __tablename__ = "estudiantes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    apellido = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    edad = Column(Integer, nullable=True)
    
    predicciones = relationship("PrediccionEstilo", back_populates="estudiante")
    
class PrediccionEstilo(Base):
    __tablename__ = "predicciones_estilo"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"))
    estilo_aprendizaje = Column(String(50))
    respuesta = Column(Text)
    
    estudiante = relationship("Estudiante", back_populates="predicciones")
    recursos = relationship("RecursosRecomendados", back_populates="prediccion")
    
class RecursosRecomendados(Base):
    __tablename__ = "recursos_recomendados"
    id= Column(Integer, primary_key=True, index=True)
    prediccion_id = Column(Integer, ForeignKey("predicciones_estilo.id"))
    recursos = Column(JSON)
    
    prediccion = relationship("PrediccionEstilo", back_populates="recursos")
    
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)   
