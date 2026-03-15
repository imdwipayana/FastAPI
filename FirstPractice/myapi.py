from fastapi import FastAPI

app = FastAPI()

# End Point (URL)

@app.get("/")
def root():
    return {"message":"Welcome to your Introduction to Fast API"}