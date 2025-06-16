from fastapi import FastAPI



app = FastAPI()

@app.get("")
def First():
    return {"message":"Task Manager is running"}
