# DSAN Core

## O Kernel de Execução Verificável da DSAN Network

O `dsan-core` é uma implementação de referência dos mecanismos centrais para **execução digital verificável e governada** dentro da Decentralized Sovereign Agent Network (DSAN).

O projeto fornece mecanismos executáveis para:

* identidade criptográfica e assinaturas;
* representação canônica de eventos;
* validação de eventos;
* autorização baseada em políticas;
* processamento de decisões de execução;
* submissão de eventos assinados;
* persistência em ledger;
* replay determinístico;
* geração de raízes Merkle;
* reconstrução de estado;
* verificação de state roots;
* auditoria independente;
* sincronização de ledger.

O `dsan-core` é uma **implementação de mecanismos selecionados da DSAN**. Ele não constitui, isoladamente, a definição completa da arquitetura DSAN.

A definição arquitetural da DSAN é mantida pelo repositório **DSAN-Ecosystem** e por suas especificações arquiteturais associadas.

---

## 1. Relação com a Arquitetura DSAN

A DSAN é um framework arquitetural no qual a soberania pertence à entidade soberana e é manifestada operacionalmente por meio de mecanismos computacionais apropriados.

Dentro dessa arquitetura:

```text
Entidade Soberana
       │
       ▼
    Guardian
       │
 ┌─────┴─────┐
 ▼           ▼
GuardianOS   Totem
       │      │
       └──┬───┘
          ▼
      DSAN Core
          │
          ▼
     DSAN Network
```

Os componentes possuem responsabilidades distintas:

| Componente            | Responsabilidade principal                         |
| --------------------- | -------------------------------------------------- |
| Entidade Soberana     | Fonte da soberania                                 |
| Guardian              | Manifestação operacional da entidade soberana      |
| GuardianOS            | Ambiente computacional protegido do Guardian       |
| Totem                 | Âncora física opcional de soberania ou autorização |
| DSAN Core             | Mecanismos de execução e protocolos verificáveis   |
| DSAN Network          | Interação distribuída                              |
| Aplicações de Domínio | Utilização da DSAN em contextos específicos        |

O `dsan-core`, portanto, não deve ser interpretado como responsável por redefinir a ontologia do Guardian, GuardianOS, Totem ou das entidades soberanas.

---

## 2. O que este Repositório Implementa

A implementação atual concentra-se na **verificabilidade da execução digital**.

Seus principais mecanismos incluem:

### Identidade

Identidades criptográficas são utilizadas para atribuir eventos e verificar assinaturas.

### Eventos

Eventos relacionados à execução são representados de forma canônica, permitindo hashing, assinatura, armazenamento, replay e verificação.

### Autorização

As decisões de execução são avaliadas de acordo com políticas e condições de autorização aplicáveis.

Autorização é tratada como uma **decisão ou condição verificável para execução**, e não como a fonte da autoridade soberana.

### Ledger

Eventos validados podem ser registrados em uma estrutura de ledger orientada à preservação do histórico.

### Replay

O sistema permite reconstruir deterministicamente o estado a partir do histórico registrado de eventos.

### State Root

Um estado resultante pode ser representado por uma raiz criptograficamente derivada, permitindo que um observador independente verifique se um estado reconstruído corresponde ao estado esperado.

### Auditoria

O repositório inclui mecanismos para validação independente da integridade dos eventos, assinaturas, estrutura do ledger, resultados de replay e state roots.

---

## 3. Fluxo de Execução da Implementação de Referência

A implementação atual fornece um fluxo concreto de execução que pode ser representado como:

```text
Agente
  │
  ▼
Validação de Política
  │
  ▼
Consenso / Validação
  │
  ▼
Autorização
  │
  ├───────────────┐
  │               │
  ▼               ▼
Execução        Rejeição
  │
  ▼
Ledger
  │
  ▼
Replay Determinístico
  │
  ▼
Estado
  │
  ▼
State Root
  │
  ▼
Auditoria Independente
```

Esse diagrama descreve a **implementação de referência atual**.

Ele não deve ser interpretado como um pipeline obrigatório para toda implantação DSAN.

Diferentes implantações podem utilizar diferentes mecanismos de autorização, modelos de confiança, ambientes de execução ou restrições de governança.

---

## 4. Autorização Física e o Totem

A implementação atual do `dsan-core` inclui suporte a um **gate de autorização por Totem** em determinados fluxos de execução.

Esse é um mecanismo de implementação.

Ele não significa que toda operação DSAN exija um Totem físico.

O modelo arquitetural distingue:

```text
Autoridade Soberana
        ≠
Autorização
        ≠
Execução
```

e:

```text
Totem
        ≠
Guardian
        ≠
GuardianOS
        ≠
Entidade Soberana
```

O Totem pode fornecer uma âncora física ou participar da autorização quando isso for exigido pela política ou pelo contexto de execução aplicável.

A implementação atual do Core demonstra, portanto, uma forma concreta de autorização física sem transformar essa forma específica em requisito universal da arquitetura DSAN.

---

## 5. Verificabilidade

Um dos objetivos centrais do `dsan-core` é que o histórico de execução não dependa exclusivamente da confiança no componente que originalmente realizou a execução.

A implementação fornece uma cadeia de verificação:

```text
Evento Assinado
     │
     ▼
Representação Canônica
     │
     ▼
Hash
     │
     ▼
Ledger
     │
     ▼
Replay
     │
     ▼
Estado Reconstruído
     │
     ▼
State Root
     │
     ▼
Verificação Independente
```

Isso permite que um auditor independente reconstrua e verifique partes relevantes do estado sem depender exclusivamente da confiabilidade do executor original.

---

## 6. Auditoria Independente

O repositório inclui um modelo orientado à verificação independente.

Um auditor pode avaliar, de acordo com os mecanismos implementados neste repositório:

* estrutura dos eventos;
* assinaturas criptográficas;
* hashes dos eventos;
* integridade do ledger;
* informações dos validadores;
* raízes Merkle;
* replay determinístico;
* estado reconstruído;
* state roots.

O auditor não constitui uma fonte adicional de soberania.

Sua função é **verificação e produção de evidências**.

---

## 7. Replay Determinístico

O replay determinístico constitui uma propriedade importante da implementação de referência.

Dado o mesmo histórico válido de eventos e as mesmas regras determinísticas aplicáveis, diferentes nós devem ser capazes de reconstruir estados equivalentes.

Conceitualmente:

```text
Histórico de Eventos
        │
        ▼
      Replay
        │
        ▼
     Estado S
        │
        ▼
    State Root
```

Isso fornece uma base para:

* reprodutibilidade;
* auditoria;
* verificação de integridade;
* comparação de estados;
* recuperação;
* sincronização.

---

## 8. Modelo de Segurança

O `dsan-core` utiliza mecanismos criptográficos para fornecer verificabilidade e integridade.

Esses mecanismos podem incluir:

* assinaturas de chave pública;
* hashing de eventos;
* serialização canônica;
* representações autenticadas de estado;
* estruturas Merkle;
* replay determinístico;
* verificação independente.

A verificação criptográfica, por si só, não estabelece que uma ação seja legítima.

A legitimidade depende, conforme o contexto, de:

* identidade;
* contexto;
* política;
* autorização;
* estado;
* delegação;
* relações de confiança;
* regras de governança.

Portanto:

> **Validade criptográfica constitui evidência de integridade e atribuição; ela não é equivalente à autorização ou à soberania.**

---

## 9. Consenso

A implementação atual contém mecanismos de validação entre pares e aprovação baseada em maioria.

Esses mecanismos fazem parte da implementação de referência atual.

Eles não devem ser interpretados como uma afirmação de que a DSAN exige um único algoritmo universal de consenso.

Uma implantação específica pode utilizar:

* validação entre pares;
* mecanismos baseados em quórum;
* validação centralizada;
* validação federada;
* autorização específica da aplicação;
* outros mecanismos apropriados.

O requisito arquitetural não é um algoritmo específico de consenso.

O requisito é que as decisões e transições de estado relevantes permaneçam **adequadamente verificáveis e governadas**.

---

## 10. Operação Offline e Local

O Core pode operar utilizando estado e informações disponíveis localmente.

Entretanto:

> **operação offline não significa autonomia irrestrita.**

Uma implementação deve preservar as restrições aplicáveis de:

* autorização;
* delegação;
* expiração;
* revogação;
* estado.

Isso deve permanecer válido mesmo quando não houver conectividade contínua com a rede.

Quando a conectividade for restaurada, a sincronização não deve automaticamente ressuscitar uma autoridade que tenha expirado ou sido revogada.

O comportamento offline é, portanto, uma questão de implementação e política, e não uma regra universal de autorização.

---

## 11. Escopo dos Protocolos

Os protocolos implementados neste repositório descrevem mecanismos utilizados pelo `dsan-core`.

Eles incluem mecanismos relacionados a:

* submissão de eventos;
* validação;
* operações de ledger;
* sincronização;
* replay;
* reconstrução de estado;
* auditoria.

Esses protocolos devem ser entendidos como **protocolos de nível de implementação**.

Eles não constituem a especificação arquitetural completa da DSAN.

Os conceitos e invariantes arquiteturais são mantidos separadamente na documentação do DSAN-Ecosystem.

---

## 12. Status Experimental e de Referência

Salvo indicação explícita em contrário, este repositório deve ser considerado uma **implementação de referência e experimental**.

Destina-se a:

* pesquisa;
* validação arquitetural;
* experimentação de protocolos;
* experimentos de interoperabilidade;
* educação;
* desenvolvimento de aplicações específicas de domínio.

A existência de uma implementação funcional não implica:

* prontidão para produção;
* certificação formal;
* conformidade regulatória;
* certificação de segurança.

As propriedades de segurança devem ser avaliadas com base em modelos de ameaça explícitos e evidências da implementação.

---

## 13. Estrutura do Repositório

O repositório é organizado em torno de preocupações de implementação:

```text
dsan-core/
├── api/
├── cli/
├── docs/
├── dsan/
│   ├── agent/
│   ├── auditor/
│   ├── core/
│   ├── crypto/
│   ├── epl/
│   ├── network/
│   └── totem/
├── ledgers/
├── tests/
├── README.md
├── README.pt-BR.md
└── requirements.txt
```

A estrutura interna poderá evoluir conforme a implementação amadureça.

As responsabilidades arquiteturais não devem ser inferidas exclusivamente a partir dos nomes dos diretórios.

---

## 14. Relação com os Outros Repositórios DSAN

O `dsan-core` constitui um componente de um ecossistema maior.

| Repositório                  | Papel                                                                   |
| ---------------------------- | ----------------------------------------------------------------------- |
| `DSAN-Ecosystem`             | Arquitetura, princípios, governança e documentação pública              |
| `dsan-core`                  | Kernel de execução verificável e mecanismos de referência               |
| `dsan-guardian` / GuardianOS | Ambiente computacional do Guardian e implementação física de referência |
| `DSAN-simulator`             | Simulação, experimentação e educação                                    |
| `DSAN-DREX-ENTERPRISE`       | Aplicação empresarial/de domínio                                        |
| `radsecure-framework`        | Aplicação de domínio em saúde                                           |

Os repositórios devem permanecer compreensíveis de forma independente, preservando simultaneamente a coerência arquitetural.

---

## 15. Limites Arquiteturais

As seguintes distinções são preservadas intencionalmente:

```text
Entidade         ≠ Guardian
Guardian         ≠ GuardianOS
GuardianOS       ≠ Totem
Totem            ≠ GuardianRing
Identidade       ≠ Presença
Presença         ≠ Intenção
Intenção         ≠ Autoridade
Autoridade       ≠ Autorização
Autorização      ≠ Execução
Execução         ≠ Evidência
Evidência        ≠ Autoridade
```

Essas distinções impedem que detalhes de implementação sejam silenciosamente transformados em definições arquiteturais.

---

## 16. Princípio de Projeto

O princípio central deste repositório é:

> **A execução deve ser atribuível, governada, reprodutível e verificável de forma independente.**

O Core concentra-se, portanto, em mecanismos capazes de responder perguntas como:

* Quem originou determinado evento?
* O evento é criptograficamente válido?
* O evento possui estrutura válida?
* Quais condições de autorização eram aplicáveis?
* A execução resultante foi registrada?
* O estado resultante pode ser reconstruído?
* Outro participante pode verificar independentemente esse estado?
* As evidências podem ser auditadas posteriormente?

---

## 17. Não Objetivos

O `dsan-core` não pretende:

* definir a soberania;
* substituir a especificação arquitetural DSAN;
* exigir um Totem físico para toda operação;
* definir todas as possíveis implementações do Guardian;
* definir universalmente o hardware do GuardianOS;
* prescrever uma única topologia de rede;
* prescrever um único mecanismo de consenso;
* funcionar como uma blockchain de propósito geral;
* afirmar garantias universais de segurança;
* substituir a governança específica de um domínio;
* substituir requisitos legais ou regulatórios aplicáveis.

---

## 18. Direção de Desenvolvimento

O desenvolvimento futuro poderá ampliar o Core em direção a:

* modelos de autorização mais ricos;
* classes de autorização contextual;
* tratamento explícito de delegação;
* semântica mais robusta de revogação;
* mecanismos de recuperação;
* esquemas interoperáveis de eventos;
* sincronização aprimorada;
* ferramentas de verificação independente;
* integração com Guardian e GuardianOS;
* mecanismos configuráveis de autorização física;
* testes formais de protocolos;
* validação baseada em modelos de ameaça mais rigorosos.

A implementação deve evoluir sem alterar as distinções arquiteturais fundamentais definidas pelo DSAN-Ecosystem.

---

## 19. Relação com a Arquitetura DSAN

A relação pode ser resumida da seguinte forma:

```text
DSAN-Ecosystem
      │
      │ definição arquitetural
      ▼
   DSAN Core
      │
      │ implementação
      ├── Identidade
      ├── Eventos
      ├── Autorização
      ├── Ledger
      ├── Replay
      ├── Estado
      ├── State Root
      └── Auditoria
```

O Core implementa mecanismos.

O Ecosystem define o contexto arquitetural no qual esses mecanismos adquirem significado.

---

## 20. Licença

Consulte o arquivo `LICENSE` para conhecer os termos de licenciamento aplicáveis a este repositório.

---

## 21. Princípio Final

O `dsan-core` existe para demonstrar que a execução governada pode ser representada por meio de mecanismos computacionais verificáveis.

Seu objetivo não é tornar a tecnologia soberana.

Seu objetivo é fornecer mecanismos por meio dos quais execução, autorização, estado e evidência possam ser representados e verificados independentemente dentro da arquitetura DSAN.

**DSAN — Sovereignty by Architecture.**
