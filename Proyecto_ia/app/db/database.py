from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends

DATABASE_URL= "mysql+pymysql://root:nJRutLeFpvvcoEXKGCDeyiRGTgTIiesJ@turntable.proxy.rlwy.net:35137/railway"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
    nombre = Column(String, index=True)
    apellido = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    edad = Column(Integer, nullable=True)
    
class PrediccionEstilo(Base):
    __tablename__ = "predicciones_estilo"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"))
    estilo_aprendizaje = Column(String (50))
    respuesta = Column(Text)
    
Base.metadata.create_all(bind=engine)