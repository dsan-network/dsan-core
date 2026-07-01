# DSAN-core
> Também disponível em inglês: [README.md](README.md)

**DSAN-core** é o núcleo de execução e verificação da Rede DSAN. Ele fornece execução governada de eventos, persistência de ledger, replay determinístico, verificação de `state_root` e auditabilidade local para fluxos de execução distribuída.

No estágio atual, o DSAN-core não está posicionado como uma blockchain de produção ou uma rede BFT completa. Em vez disso, trata-se de um núcleo experimental de governança de execução, focado em processamento verificável de ações, reconstrução reproduzível do estado e design de ledger orientado à auditoria.

## O que o DSAN-core faz

Atualmente, o DSAN-core suporta:

- Criação de eventos assinados por agentes DSAN.
- Hashing canônico de eventos.
- Admissão de eventos baseada em políticas.
- Votação majoritária entre pares.
- Autorização de execução por Totem.
- Persistência local de ledger.
- Cálculo de Merkle root sobre os hashes do ledger.
- Replay determinístico para derivação de estado.
- Geração e verificação de `state_root`.
- Auditoria local independente por replay.
- Sincronização de ledger com validação estrutural.

## Arquitetura atual

O núcleo atual está organizado em cinco camadas lógicas.

## Nó auditor

O DSAN-core agora inclui um papel dedicado de **Nó Auditor**, separado do nó executor.

O Nó Auditor:
- busca `/ledger`, `/state`, `/root` e `/state_root` de um nó alvo,
- valida a estrutura do ledger,
- verifica hashes canônicos dos eventos,
- checa a continuidade de `prev_hash`,
- verifica assinaturas dos validadores,
- recalcula o Merkle root,
- faz replay do ledger localmente para recomputar `state_root`,
- compara os resultados locais com os compromissos publicados pelo nó remoto.

Isso cria uma separação entre:
- **nó executor**, que valida, executa e persiste eventos;
- **nó auditor**, que verifica de forma independente a integridade histórica e a consistência do estado derivado.

No estágio atualmente validado, o Nó Auditor confirmou com sucesso:
- validade estrutural do ledger,
- consistência do Merkle root,
- consistência do state root,
- concordância do replay independente com o nó executor.

### Camada de agentes

Os agentes criam eventos assinados contendo:
- `sender`
- `payload`
- `nonce`
- `prev_hash`

Cada evento é serializado de forma canônica, assinado com Ed25519 e transformado em hash antes do envio.

### Camada de nó

Um nó DSAN:
- recebe eventos candidatos,
- verifica a assinatura do remetente,
- checa replay e continuidade da cadeia,
- avalia regras de política,
- coleta votos locais e de pares,
- exige autorização do Totem,
- executa a ação,
- assina o hash do evento como validador,
- adiciona o pacote final ao ledger.

### Camada de ledger

Cada pacote persistido pode conter:
- `event`
- `hash`
- `validators`
- `result`
- `state_root`

O ledger atua ao mesmo tempo como histórico de execução e como substrato para replay.

### Camada de replay

O motor de replay reconstrói o estado a partir do histórico do ledger, aplicando todos os eventos em sequência. Isso produz um `state_root` determinístico, que pode ser verificado independentemente.

### Camada de auditoria

Um auditor pode:
- buscar o ledger,
- recomputar o estado localmente,
- comparar o `state_root` recomputado com o `state_root` publicado pelo nó,
- verificar se o histórico de execução e o estado publicado estão consistentes.

## Fluxo de execução

O fluxo atual de execução é:

1. O agente cria um evento assinado.
2. O nó recebe o evento.
3. O nó valida hash, assinatura, nonce e continuidade da cadeia.
4. O nó aplica as verificações de política.
5. O nó coleta votos locais e de pares.
6. O nó solicita autorização do Totem.
7. O nó executa o evento.
8. O nó calcula o `state_root` resultante.
9. O nó coleta assinaturas dos validadores.
10. O nó adiciona o pacote ao ledger.
11. O nó expõe ledger, Merkle root e state root para verificação.

## Propriedades verificadas

No estágio recuperado atual, o DSAN-core demonstra:

- **Hash canônico de eventos**
- **Histórico de ledger reproduzível**
- **Verificação de estado derivado**
- **Normalização de `state_root` por entrada**
- **Checagem de consistência do state root**
- **Auditabilidade local independente**

Isso significa que um terceiro pode recomputar o estado final derivado do histórico do ledger, em vez de confiar apenas na resposta de execução ao vivo do nó.

## Estrutura do repositório

O repositório está atualmente organizado em torno do núcleo de execução do DSAN-core e de suas ferramentas de validação e suporte.

```text
dsan-core/
├── README.md
├── README.pt-BR.md
├── CHANGELOG.md
├── LICENSE
├── RELEASE_CHECKLIST.md
├── KNOWN_ISSUES.md
├── clisend.py
├── cliaudit.py
├── migrate_state_roots.py
├── ledger_node1.json
├── dsan/
├── api/
├── cli/
├── docs/
└── data/
```

Áreas principais:
- `dsan/` contém a lógica central de execução, replay, auditoria, rede, política e Totem.
- `clisend.py` e `cliaudit.py` fornecem fluxos auxiliares locais para envio e auditoria.
- `migrate_state_roots.py` é usado para normalizar entradas históricas do ledger.
- `ledger_node1.json` é o ledger local principal usado nas validações e verificações por replay.
- `docs/`, `api/`, `cli/` e `data/` são diretórios de apoio para documentação, suporte de interface, utilitários de linha de comando e artefatos locais de dados.

## Início rápido

### 1. Subir um nó local

```bash
python -m dsan.network.node node1 5001
```

Isso inicia um nó DSAN local em `127.0.0.1:5001`.

### 2. Verificar endpoints básicos

```bash
curl http://127.0.0.1:5001/state
curl http://127.0.0.1:5001/root
curl http://127.0.0.1:5001/state_root
curl http://127.0.0.1:5001/ledger
```

### 3. Enviar um evento

Exemplo de `clisend.py`:

```python
import requests
from dsan.agent.agent import DSANAgent

NODE_URL = "http://127.0.0.1:5001"

agent = DSANAgent("alice")

state = requests.get(f"{NODE_URL}/state").json()
prev_hash = state["last_hash"]

packet = agent.create_event(
    {
        "type": "transfer",
        "from": "alice",
        "to": "bob",
        "amount": 10
    },
    prev_hash
)

response = requests.post(f"{NODE_URL}/receive", json=packet)

print("status:", response.status_code)
print("body:", response.json())
```

Execute:

```bash
python clisend.py
```

### 4. Auditar o nó de forma independente

Exemplo de `cliaudit.py`:

```python
import requests
from dsan.core.replay import replay_ledger

NODE_URL = "http://127.0.0.1:5001"

ledger = requests.get(f"{NODE_URL}/ledger").json()
root_info = requests.get(f"{NODE_URL}/root").json()
state_info = requests.get(f"{NODE_URL}/state_root").json()
state_meta = requests.get(f"{NODE_URL}/state").json()

replayed_state_root = replay_ledger(ledger)
node_state_root = state_info["state_root"]

print("=== RELATÓRIO DE AUDITORIA DSAN ===")
print("ledger_size:", state_meta["ledger_size"])
print("last_hash:", state_meta["last_hash"])
print("merkle_root:", root_info["root"])
print("node_state_root:", node_state_root)
print("replayed_state_root:", replayed_state_root)

if ledger:
    last_entry = ledger[-1]
    packet_state_root = last_entry.get("state_root")
    print("packet_state_root:", packet_state_root)

    if packet_state_root is None:
        print("packet_state_root_check: AUSENTE")
    elif packet_state_root == replayed_state_root:
        print("packet_state_root_check: OK")
    else:
        print("packet_state_root_check: DIVERGENTE")
else:
    print("packet_state_root: LEDGER_VAZIO")

if node_state_root == replayed_state_root:
    print("audit_result: CONSISTENTE")
else:
    print("audit_result: DIVERGENTE")
```

Execute:

```bash
python cliaudit.py
```

### 5. Executar o nó auditor

Inicie o serviço de auditoria:

```bash
python -m dsan.auditor.node
```

Em outro terminal, audite um nó executor em execução:

```bash
curl "http://127.0.0.1:5010/audit?target=http://127.0.0.1:5001"
```

Uma resposta bem-sucedida deve incluir:

- `structure_valid: true`
- `merkle_root_match: true`
- `state_root_match: true`
- `audit_result: CONSISTENT`

Isso confirma que o ledger remoto, o Merkle root e o estado derivado podem ser verificados independentemente.

### 6. Teste manual fim a fim com Totem

Este fluxo valida o envio do evento, a execução com gate do Totem, a persistência no ledger e a verificação independente pelo auditor.

#### Subir o nó executor

```bash
python -m dsan.network.node node1 5001
```

#### Subir o nó auditor

```bash
python -m dsan.auditor.node
```

#### Gerar um evento assinado

Crie `send_event.py`:

```python
import json
import time
import hashlib
import requests
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def hash_event(event):
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()

state = requests.get("http://127.0.0.1:5001/state", timeout=2).json()
prev_hash = state["last_hash"]

event = {
    "nonce": str(int(time.time() * 1000)),
    "payload": {"msg": "transfer_funds"},
    "prev_hash": prev_hash,
    "sender": "alice"
}

sender_sk = ed25519.Ed25519PrivateKey.generate()
sender_pk = sender_sk.public_key()

packet = {
    "event": event,
    "hash": hash_event(event),
    "signature": sender_sk.sign(canonical_json(event).encode()).hex(),
    "sender_sig_pub": sender_pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()
}

with open("event.json", "w", encoding="utf-8") as f:
    json.dump(packet, f, ensure_ascii=False, indent=2)

print("event.json gerado")
print("prev_hash =", prev_hash)
print("new_hash =", packet["hash"])
print("nonce =", packet["event"]["nonce"])
```

Execute:

```bash
python send_event.py
cat event.json
```

#### Enviar o evento

```bash
curl -X POST http://127.0.0.1:5001/receive -H "Content-Type: application/json" -d @event.json
```

#### Autorizar no Totem

Quando o terminal do nó executor mostrar:

```bash
🔐 Totem gesture (ex: 120):
```

digite:

```bash
120
```

#### Validar estado do nó e resultado da auditoria

```bash
curl http://127.0.0.1:5001/state
curl http://127.0.0.1:5001/ledger
curl "http://127.0.0.1:5010/audit?target=http://127.0.0.1:5001"
```

Resultado esperado:
- `ledger_size` aumenta em 1,
- `last_hash` muda,
- o novo pacote aparece em `/ledger`,
- o auditor retorna `audit_result: CONSISTENT`.

> Observação: o endpoint correto de ingestão é `/receive`. O POST só conclui depois que a sequência gestual correta é digitada no terminal do nó executor. Reenviar o mesmo `event.json` pode retornar `{"status":"duplicate"}`.

### 7. Normalizar entradas antigas do ledger

Se entradas antigas do ledger ainda não tiverem `state_root`, use `migrate_state_roots.py` para normalizar os pacotes históricos.

Execute:

```bash
python migrate_state_roots.py ledger_node1.json
```

Isso recalcula os valores progressivos de `state_root` e atualiza entradas legadas.

## Status atual

Este repositório reflete um **núcleo de execução recuperado e estabilizado**, evoluído além do estágio original de simulador.

As propriedades validadas no branch recuperado incluem:

- inicialização do nó e disponibilidade de endpoints,
- carregamento do ledger persistido,
- envio e execução de eventos,
- replay determinístico,
- consistência de `state_root`,
- normalização histórica do ledger,
- auditoria local bem-sucedida com resultado `CONSISTENTE`,
- inicialização do Nó Auditor dedicado,
- auditoria remota independente,
- verificação de assinaturas dos validadores no auditor,
- recomputação e comparação do Merkle root,
- resultado bem-sucedido do auditor com `CONSISTENTE`.

## Limitações

O DSAN-core continua experimental e possui limitações importantes:

- sem consenso BFT,
- sem motor de consenso assíncrono,
- sem governança persistente de identidade de validadores,
- sem modelo finalizado de membership,
- a autorização do Totem é interativa e atualmente presa ao terminal,
- a semântica da política ainda está evoluindo,
- a auditoria é local e orientada a desenvolvedor, ainda não um verificador isolado de produção.

## Direção de desenvolvimento

Os próximos passos mais lógicos são:

- modo dedicado de nó auditor,
- modelo persistente de identidade de validadores,
- validação de sync mais estrita sobre o histórico normalizado,
- definições formais de política EPL / JSON,
- separação mais clara entre execução e estado,
- documentação em nível de protocolo,
- caminho de integração com os serviços mais amplos da Rede DSAN.

## Posicionamento

O DSAN-core deve ser entendido como um **núcleo de execução verificável**, e não apenas como um protótipo de blockchain.

Seu propósito central é tornar a execução governada:
- reproduzível,
- derivável a partir do estado,
- auditável externamente,
- estruturalmente verificável.

## Aviso

Este projeto está em evolução arquitetural ativa. Interfaces, estrutura dos pacotes e lógica de verificação podem mudar conforme o núcleo se estabiliza.