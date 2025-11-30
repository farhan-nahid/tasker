import uvicorn
from src.configs.app_vars import PORT

def main():
    uvicorn.run("src.app:app", host="0.0.0.0", port=PORT, reload=True)


if __name__ == "__main__":
    main()
