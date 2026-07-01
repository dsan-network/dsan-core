import subprocess
import time
import requests

print("🚀 Iniciando demo DSAN...")

# sobe nodes corretamente
node1 = subprocess.Popen(["python", "-m", "dsan.network.node", "node1", "5001"])
node2 = subprocess.Popen(["python", "-m", "dsan.network.node", "node2", "5002"])

# espera subir de verdade
time.sleep(2)

def wait_node(port):
    for _ in range(10):
        try:
            requests.get(f"http://127.0.0.1:{port}")
            return True
        except:
            time.sleep(0.5)
    return False

if not wait_node(5001):
    print("❌ node1 não subiu")
if not wait_node(5002):
    print("❌ node2 não subiu")

print("\n📨 Enviando mensagem legítima...")
subprocess.run(["python", "-m", "cli.send"])

print("\n⚠️ Testando ataques...")
subprocess.run(["python", "-m", "cli.attack"])

print("\n🛑 Encerrando nodes...")
node1.terminate()
node2.terminate()

print("✅ Demo finalizada")