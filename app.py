from fastapi import FastAPI  #for bringing fastapi class in my python program
app = FastAPI()

#Fastapi uses decorators
@app.get("/") #endpoint 1
def get_home():
    return {
            "message":"CloudOps Application",
            "version":"1.0.0"
           }

@app.get("/health") #endpoint 2
def get_health():
    return {"status":"Healthy"}

@app.get("/version") #endpoint 3
def get_version():
    return {"version":"1.0.0"}