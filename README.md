# 🛡️ DSAN Core

### Decentralized Sovereign Agent Network — Core Implementation

![License](https://img.shields.io/badge/license-Apache%202.0-blue)

---

## 🧠 Overview

**DSAN Core** is the reference implementation of the **DSAN (Decentralized Sovereign Agent Network)** protocol.

It provides the foundational building blocks required to create **sovereign digital agents** capable of:

* cryptographic identity
* authenticated communication
* controlled execution
* hybrid (cloud/off-cloud) operation

This repository focuses on **core primitives and architecture**, not full applications.

---

## 🎯 Purpose

The goal of DSAN Core is to:

* validate the DSAN protocol in practice
* provide a minimal and auditable implementation
* establish a foundation for sovereign execution systems

---

## 🧱 Architecture

```text
dsan-core/
├── dsan/
│   ├── crypto/
│   │   ├── identity.py
│   │   ├── handshake.py
│   │
│   ├── agent/
│   │   ├── agent.py
│   │
│   ├── network/
│   │   ├── node.py
│   │   ├── transport.py
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

* Ed25519-based identity
* message signing

### ✔ Secure Key Exchange

* X25519 Diffie-Hellman
* HKDF key derivation

### ✔ Authenticated Messaging

* signed payloads
* integrity validation

### ✔ Minimal Network Layer

* TCP communication
* structured transport

---

## 🌐 Execution Context Layer (ECL)

DSAN introduces an **Execution Context Layer (ECL)** that defines how and where agents operate.

### 🟢 On-Cloud Mode

* connected execution
* integration with external systems
* scalable and interoperable

### 🔴 Off-Cloud Mode

* fully local execution
* no external dependencies
* resilient to network failure or censorship

### 🟡 Hybrid Mode

* dynamic switching between contexts
* local sovereignty with optional synchronization

> DSAN is not cloud-dependent.
> It is **cloud-adaptive**.

---

## 🧬 Totem Layer (TL)

The **Totem Layer** represents the physical or hardware-bound component of the DSAN architecture.

It is responsible for anchoring digital execution to **real-world control**.

### Core Functions

* 🔐 Identity anchoring (non-exportable control)
* 🧍 Human or physical validation (gesture, biometrics, presence)
* ⚡ Execution authorization
* 🧱 Off-cloud operational capability

> The Totem is not optional.
> It is the mechanism that prevents purely virtual capture of the system.

---

## ⚙️ Conceptual Flow

1. Agent identity is created (cryptographic layer)
2. Totem validates authorization (physical layer)
3. Execution context is determined (ECL)
4. Action is executed (local or networked)

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

## ⚠️ Current Limitations

This is a **reference implementation**, not production-ready.

Missing components include:

* signature verification at node level
* encrypted transport (E2EE)
* persistent identity (Totem-backed storage)
* full Totem integration
* Execution Policy Layer (EPL)
* distributed coordination

---

## 🧠 Roadmap

* [ ] Signature verification
* [ ] End-to-end encryption
* [ ] Totem integration (hardware layer)
* [ ] Execution Policy Layer (EPL)
* [ ] Hybrid execution logic
* [ ] Multi-node communication

---

## 🌐 DSAN Ecosystem

This repository is part of the DSAN Network.

Core protocol:
👉 https://github.com/dsan-network/dsan-ecosystem

---

## ⚖️ License

This project is licensed under the Apache License 2.0.

---

## ⚠️ Intellectual Property Notice

This repository provides a **reference implementation** of the DSAN protocol.

Certain components are intentionally not included, including:

* Execution Policy Layer (EPL)
* applied systems (e.g., RadSecure, DSAN-DREX)
* production deployment strategies

These may be subject to intellectual property protection.

---

## 🤝 Contributing

Contributions are welcome in:

* cryptography
* distributed systems
* secure networking
* protocol engineering

---

## 📬 Contact

Alessandro Turok da Silva Collares
DSAN Network

---

## 🧩 Vision

> To establish a foundational infrastructure where digital agents operate with cryptographic sovereignty, physical authorization, and adaptive execution across cloud and non-cloud environments.

