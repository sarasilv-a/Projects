# Sistema Multiagente para Gestão Integrada de Cuidados de Saúde

Este projeto apresenta o desenvolvimento de um **Sistema Multiagente (SMA)** aplicado ao domínio da saúde, com foco na **gestão de emergências médicas**, **monitorização contínua de pacientes**, **agendamento de consultas** e **suporte ao paciente através de um chatbot**.

O sistema foi concebido para demonstrar a coordenação entre agentes autónomos pertencentes a diferentes domínios funcionais, comunicando entre si através de mensagens assíncronas e protocolos bem definidos.

---

## 🧠 Objetivos do Projeto

Os principais objetivos deste projeto são:

- Modelar um ecossistema de saúde distribuído recorrendo a agentes autónomos;
- Demonstrar comunicação e coordenação eficaz entre agentes;
- Simular cenários realistas de emergências médicas e cuidados contínuos;
- Integrar diferentes subsistemas (emergências, agendamentos, monitorização e suporte ao paciente);
- Avaliar o comportamento do sistema em situações concorrentes e críticas.

---

## 🏗️ Arquitetura Geral

O sistema está organizado em **domínios funcionais**, cada um composto por agentes especializados:

### Gestão de Emergências
- EmergencyCenterAgent  
- TriageAgent  
- AmbulanceAgent  
- HelicopterAgent  
- HospitalAgent  

### Monitorização
- SensorAgent  
- MonitoringAgent  

### Agendamentos
- SchedulerAgent  
- DoctorAgent  

### Suporte ao Paciente
- ChatbotPatientAgent  

Todos os agentes comunicam através de mensagens SPADE, utilizando *performatives* explícitas (`REQUEST`, `INFORM`, `CONFIRM`, `REFUSE`), garantindo clareza semântica e robustez na interação.

---

## 🔁 Fluxos Implementados

O sistema suporta vários fluxos de funcionamento representativos do domínio da saúde:

1. **Pedido de consulta médica via chatbot**  
2. **Emergência detetada automaticamente pela monitorização**  
3. **Emergência reportada diretamente por um paciente**  
4. **Encaminhamento hospitalar e continuidade de cuidados**, incluindo pedidos de especialidade médica  

Cada fluxo envolve a interação coordenada entre múltiplos agentes e foi validado através de cenários de teste específicos.

---

## ⚙️ Decisões de Projeto

O comportamento do sistema é regido por um conjunto de **regras explícitas**, implementadas diretamente no código, entre as quais:

- Seleção automática do meio de transporte com base na gravidade da emergência;
- Deteção de situações críticas a partir de limiares de sinais vitais;
- Triagem simples de urgência no chatbot baseada em palavras-chave;
- Gestão da capacidade hospitalar e aceitação ou recusa de pacientes;
- Mecanismos de *cooldown* para evitar o envio excessivo de alertas consecutivos.

Estas decisões visam garantir respostas rápidas, coerentes e seguras em contextos críticos.

---

## ▶️ Execução do Projeto

### Requisitos
- Python 3.10 ou superior  
- SPADE  
- Dependências adicionais incluídas no projeto  

### Execução de Cenários

Os diferentes cenários podem ser executados através dos scripts disponíveis em `src/scenarios/`.  
Exemplo de execução do sistema completo:

```bash
python src/scenarios/run_full_system_demo.py
```

### Outros cenários disponíveis

Para além do cenário de demonstração completa do sistema, foram desenvolvidos vários cenários adicionais com o objetivo de testar comportamentos específicos:

- **Testes básicos de emergência**, focados na validação do fluxo mínimo de triagem, despacho e admissão hospitalar;
- **Emergências com múltiplos pacientes**, permitindo avaliar o comportamento concorrente do sistema e a gestão simultânea de vários casos críticos;
- **Testes de stress ao sistema de agendamentos**, utilizados para analisar a robustez do SchedulerAgent perante múltiplos pedidos concorrentes;
- **Integração completa com monitorização ativa**, onde sinais vitais gerados por sensores desencadeiam automaticamente alertas de emergência.

---

## 📊 Resultados

Os cenários de teste realizados demonstram:

- Coordenação eficaz entre agentes autónomos;
- Capacidade de resposta adequada a emergências críticas;
- Suporte a múltiplos pedidos concorrentes;
- Integração consistente entre monitorização, emergências e agendamentos;
- Facilidade de extensão da arquitetura com novos agentes e comportamentos.

---

## 🧩 Estrutura do Projeto (simplificada)

```text
src/
├── agents/
├── protocols/
├── utils/
├── scenarios/
│   ├── run_full_system_demo.py
│   ├── run_emergency_basic.py
│   ├── run_emergency_multi_patients.py
│   └── run_appointments_stress.py
└── main.py
