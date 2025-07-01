from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    return {"message": "Test works!"}

@app.get("/me")
async def read_users_me():
    return {"username": "test_user", "role": "test", "district": "Test"}

print("FastAPI app defined with /test and /me endpoints")  # Debug