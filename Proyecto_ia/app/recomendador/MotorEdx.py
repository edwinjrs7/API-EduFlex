from .MotorRecomendaciones import MotorDeRecomendaciones 
import requests
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import time


        
        