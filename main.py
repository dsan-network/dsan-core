import uvicorn

if __name__ == "__main__":
    uvicorn.run("dsan.network.node:app", host="0.0.0.0", port=8000)
