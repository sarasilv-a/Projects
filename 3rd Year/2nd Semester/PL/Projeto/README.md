# Compilador Pascal → EWVM

Este projeto consiste num compilador simples para um subconjunto da linguagem Pascal, que traduz código fonte para instruções compatíveis com a máquina virtual [EWVM](https://ewvm.epl.di.uminho.pt).

## 📁 Estrutura

```
├── lexer.py               # Analisador léxico (tokens)
├── parser.py              # Analisador sintático + geração de código EWVM
├── main.py                # Script principal para executar o compilador
├── ewvm_output.txt        # Ficheiro onde é guardado o output EWVM
├── exemplos/              # Programas de exemplo em Pascal (.pas)
└── relatorio.md           # Documento descritivo do projeto
```

## ▶️ Como executar

1. Garante que tens o Python 3 instalado.
2. Instala a biblioteca PLY, se necessário:

```bash
pip install ply
```

3. Corre o compilador com um ficheiro `.pas` como argumento:

```bash
python main.py exemplos/exemplo6.pas
```

4. O código EWVM gerado será guardado no ficheiro `ewvm_output.txt`.

## 🧠 EWVM

Podes testar o código gerado em:  
📎 [https://ewvm.epl.di.uminho.pt](https://ewvm.epl.di.uminho.pt)

Basta colar o conteúdo do `ewvm_output.txt` na área de código e carregar em "Run".

---
