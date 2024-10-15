from fastapi import FastAPI
import frontend
app = FastAPI()
frontend.init(app)