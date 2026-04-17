import requests
from dsan.agent.agent import DSANAgent

agent = DSANAgent("client_1")

def send():
    payload = "transfer_funds"

    msg = agent.create_message({"action": payload})

    res = requests.post(
        "http://localhost:8000/receive",
        json=msg
    )

    print(res.json())

if __name__ == "__main__":
    send()
