# Serviço Over-the-Top para Entrega de Multimédia
**ESR – Engenharia de Serviços em Rede (MEI, UMinho)**  
Ano letivo **2025/2026**

---

## 📌 Descrição do Projeto

Este repositório contém a implementação de um **serviço de _streaming_ multimédia Over-the-Top (OTT)** desenvolvido no âmbito da unidade curricular **Engenharia de Serviços em Rede (ESR)** do Mestrado em Engenharia Informática da Universidade do Minho.

O sistema assenta numa **rede _overlay_ aplicacional descentralizada**, construída sobre uma infraestrutura IP, e tem como objetivo a **entrega eficiente de conteúdos multimédia em tempo real** (vídeo) a múltiplos clientes, privilegiando **baixa latência**, **adaptação dinâmica a falhas** e **uso eficiente da largura de banda**.

A solução utiliza **UDP** como protocolo de transporte base, complementado com **mecanismos aplicacionais de controlo e fiabilidade**, incluindo:
- construção dinâmica de rotas por _stream_;
- deteção de falhas através de _heartbeats_;
- retransmissões seletivas com NACKs;
- _multicast_ aplicacional no _overlay_;
- troca suave de rotas (_graceful switch_).

---

## 🏗️ Arquitetura Geral

A arquitetura do sistema é composta por três tipos principais de entidades:

- **Servidor de Streaming**
  - Fonte dos conteúdos multimédia
  - Inicia o processo de anúncio e construção de rotas
  - Envia pacotes RTP encapsulados sobre UDP

- **Nós de Transporte (_Overlay Nodes_)**
  - Reencaminham pacotes de dados e mensagens de controlo
  - Mantêm tabelas de encaminhamento por _stream_
  - Adaptam-se dinamicamente a falhas e variações da rede

- **Clientes**
  - Solicitam e controlam sessões de _streaming_ (PLAY, PAUSE, TEARDOWN)
  - Recebem, descodificam e apresentam os conteúdos multimédia
  - Participam nos mecanismos de deteção e recuperação de perdas

Os testes e validação do sistema foram realizados recorrendo ao **emulador CORE**, utilizando diferentes topologias de rede.

---

## ⚙️ Tecnologias Utilizadas

- **Linguagem:** Python 3  
- **Transporte:** UDP  
- **Multimédia:** RTP (encapsulamento dos dados)  
- **Emulação de Rede:** CORE  
- **Interface Gráfica (Cliente):** Tkinter  
- **Comunicação Fiável (Controlo):** ACK / NACK ao nível da aplicação  

---

## 🧪 Testes

O projeto inclui:

- **Testes unitários** aos principais módulos (protocolos, _streaming_ e controlo fiável);
- **Testes de integração** entre servidor, nós intermédios e clientes;
- **Testes globais** em topologias emuladas no **CORE**.

Os testes validam o correto funcionamento do sistema em cenários com perdas, falhas de nós e múltiplos clientes ativos.

---

## 👥 Autores

Projeto desenvolvido por:

- **Fernando Pires**  
  GitHub: [ferjpires](https://github.com/ferjpires)

- **Pedro Teixeira**  
  GitHub: [PedroTe010](https://github.com/PedroTe010)

- **Sara Silva**  
  GitHub: [sarasilv-a](https://github.com/sarasilv-a)

---

## 📄 Contexto Académico

Este trabalho foi desenvolvido no âmbito do **Trabalho Prático de ESR – Serviço Over-the-Top para Entrega de Multimédia**, seguindo as especificações e objetivos definidos no enunciado fornecido pela equipa docente da **Universidade do Minho**.
