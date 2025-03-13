import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  
    host = "0.0.0.0"  
    reload = os.getenv("ENV") != "production"  

    uvicorn.run("api:app", host=host, port=port, reload=reload)