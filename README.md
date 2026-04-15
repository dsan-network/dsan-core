# 🛡️ DSAN Core

### Decentralized Sovereign Agent Network — Core Implementation

![License](https://img.shields.io/badge/license-Apache%202.0-blue)

---

## 🧠 Overview

**DSAN Core** is the reference implementation of the **DSAN (Decentralized Sovereign Agent Network)** protocol.

It provides the foundational building blocks required to create **sovereign digital agents** capable of:

* cryptographic identity
* authenticated communication
* secure message exchange
* execution-ready infrastructure

This repository focuses on **engineering primitives**, not full applications.

---

## 🎯 Purpose

The goal of DSAN Core is to:

* validate the DSAN protocol in practice
* provide a minimal, auditable implementation
* serve as a foundation for higher-level systems

It is intentionally **modular, minimal, and extensible**.

---

## 🧱 Architecture

```
dsan-core/
├── dsan/
│   ├── crypto/
│   │   ├── identity.py        # Ed25519 identity
│   │   ├── handshake.py       # X25519 + HKDF
│   │
│   ├── agent/
│   │   ├── agent.py           # Sovereign agent abstraction
│   │
│   ├── network/
│   │   ├── node.py            # TCP node
│   │   ├── transport.py       # Message transport
│
├── examples/
├── tests/
├── main.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🔐 Core Capabilities

### ✔ Cryptographic Identity

* Ed25519-based deterministic identity
* message signing and verification

### ✔ Secure Key Exchange

* X25519 Diffie-Hellman
* HKDF-based key derivation

### ✔ Authenticated Messaging

* signed payloads
* integrity validation

### ✔ Network Layer (Minimal)

* TCP-based communication
* structured message transport

---

The Totem Layer represents the physical or hardware-bound component of the DSAN architecture.

It is responsible for:

- anchoring identity to a physical entity  
- enforcing execution authorization  
- enabling off-cloud operation  
- preventing unauthorized key usage  

The Totem is not a peripheral component — it is a foundational element for sovereignty.

---

DSAN supports multiple execution contexts:

- **Off-Cloud Mode**: Fully local, sovereign execution with no external dependencies  
- **On-Cloud Mode**: Connected execution enabling interoperability and scalability  
- **Hybrid Mode**: Adaptive execution balancing sovereignty and connectivity  

This design ensures resilience, flexibility, and control across different operational environments.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/dsan-network/dsan-core.git
cd dsan-core
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run a node

```bash
python dsan/network/node.py
```

---

### 4. Send a message

```bash
python main.py
```

---

## 🧪 Example Flow

1. A DSAN Agent is instantiated
2. A message is signed using Ed25519
3. The payload is transmitted over TCP
4. The receiving node processes the message

---

## ⚠️ Current Limitations

This is a **reference implementation**, not production-ready.

Missing components include:

* full signature verification on node
* encrypted transport (E2EE)
* persistent identity (Totem model)
* Execution Policy Layer (EPL)
* distributed consensus or coordination

---

## 🧠 Roadmap

* [ ] Signature verification at node level
* [ ] End-to-end encryption (secure channels)
* [ ] Deterministic identity persistence
* [ ] EPL (Execution Policy Layer) integration
* [ ] Multi-node network support
* [ ] API layer (REST / gRPC)

---

## 🌐 DSAN Ecosystem

This repository is part of the DSAN Network.

Core protocol and architecture:
👉 https://github.com/dsan-network/dsan-ecosystem

---

## ⚖️ License

This project is licensed under the Apache License 2.0.

You are free to use, modify, and distribute this software, provided that proper attribution is maintained.

---

## ⚠️ Intellectual Property Notice

This repository contains a **reference implementation** of the DSAN protocol.

Certain aspects of the DSAN architecture, including:

* execution models (EPL)
* applied systems (e.g., RadSecure, DSAN-DREX)
* deployment strategies

may be subject to intellectual property protection and are **not fully disclosed** here.

---

## 🤝 Contributing

Contributions are welcome, particularly in:

* cryptography
* distributed systems
* secure networking
* protocol design

Please open issues or pull requests.

---

## 📬 Contact

**Alessandro Turok da Silva Collares**
Specialist in Radiological Protection
DSAN Network

---

## 🧩 Vision

> To establish a foundational infrastructure where digital agents operate with cryptographic sovereignty, traceability, and controlled execution.
