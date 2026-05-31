<h1 style="text-align: center;">Construção de um Compilador para Pascal Standard</h1>

<h1 style="text-align: center; font-size: 28px;">Processamento de Linguagens</h1>

<p style="text-align: center;"><strong>Grupo 15</strong></p>
<p style="text-align: center;">1 de junho de 2025</p>

<div style="display: flex; justify-content: center; gap: 60px; margin-top: 20px;">

<div style="text-align: center;">
  <strong>Ana Carolina Penha Cerqueira</strong><br>
  A104188
</div>

<div style="text-align: center;">
  <strong>Fernando Jorge da Silva Pires</strong><br>
  A77399
</div>

<div style="text-align: center;">
  <strong>Sara Catarina Loureiro da Silva</strong><br>
  A104608
</div>

</div>


## 1. Introdução

A compreensão completa do processo de transformação de uma linguagem de programação em instruções executáveis revela-se uma componente essencial para o desenvolvimento de competências em programação, possibilitando uma melhor perceção do processo de escrita de código.

Entender como as linguagens são interpretadas pelas máquinas, desde o momento em que o código é escrito até à sua execução final, permite escrever programas mais eficientes, prever comportamentos durante a execução e identificar com maior facilidade os erros que podem surgir.

No sentido de aplicar os conhecimentos teóricos adquiridos ao longo da unidade curricular, surgiu a realização deste projeto. O seu objetivo é a construção de um compilador para a linguagem Pascal standard, permitindo explorar os diferentes estágios do processo de compilação — desde a análise léxica e sintática até à geração de código.

### 1.1. Pascal

Antes da construção do compilador, foi essencial compreender a linguagem que iríamos analisar e traduzir. A linguagem escolhida foi **Pascal**, uma linguagem de programação imperativa, fortemente tipada, criada por **Niklaus Wirth** nos anos 70 com o objetivo de promover boas práticas de programação e ensino estruturado.

Entre as principais características da linguagem Pascal, destacam-se:

- Estrutura modular: programas compostos por cabeçalho (`program Nome;`), secção de declarações (`var`) e bloco principal (`begin ... end.`);
- Tipos primitivos como `integer`, `real`, `boolean` e `char`;
- Suporte a **arrays** com intervalos personalizados, como `array[1..10] of integer`;
- Estruturas de controlo como `if-then[-else]`, `for`, `while`, `repeat-until`;
- Entrada e saída com `readln`, `write`, `writeln`, entre outros;
- Possibilidade de criar funções e procedimentos (não abordados neste projeto).

Estas características tornam Pascal uma linguagem ideal para compreender conceitos fundamentais de compilação como **análise sintática**, **verificação de tipos**, **tradução de expressões**, e **controlo de fluxo**.

#### Exemplo simples em Pascal

```pascal
program HelloWorld;
begin
  writeln('Ola, Mundo!');
end.
```

Este pequeno programa ilustra a estrutura básica de um programa Pascal: uma instrução `writeln` dentro de um bloco `begin ... end`, terminando com ponto final (`.`), obrigatório em Pascal.

### 1.2. EWVM – Máquina Virtual Educacional

A **EWVM (Educational Web Virtual Machine)** é uma máquina virtual baseada em stack, desenvolvida para fins pedagógicos no ensino de compiladores. Através de uma interface web interativa, permite executar programas escritos numa linguagem de montagem simples, visualizar o estado da stack, registos e memória, e acompanhar a execução passo a passo.

No contexto deste projeto, a EWVM foi utilizada para testar e validar o código gerado pelo compilador Pascal, facilitando a deteção de erros e a verificação do comportamento esperado dos programas.

Está disponível online em: [https://ewvm.epl.di.uminho.pt](https://ewvm.epl.di.uminho.pt)


## 2. Arquitetura

### 2.1. Análise Léxica
O analisador léxico tem como objetivo converter o código-fonte Pascal numa sequência de *tokens*, reconhecendo palavras-chave, identificadores, operadores, literais e delimitadores. Para este projeto, utilizou-se a biblioteca `ply.lex`.

Foram definidos tokens para todas as palavras-chave da linguagem Pascal (como `program`, `begin`, `end`, `var`, `integer`, `boolean`, etc.), bem como para operadores aritméticos (`+`, `-`, `*`, `/`, `div`, `mod`), relacionais (`=`, `<>`, `<`, `>`, `<=`, `>=`) e lógicos (`and`, `or`, `not`). O reconhecimento das palavras-chave é feito de forma *case-insensitive* usando expressões regulares com grupos de letras maiúsculas e minúsculas. Todos os identificadores são convertidos para minúsculas com `t.value = t.value.lower()`.

Os números são reconhecidos como inteiros ou reais através de expressões regulares, sendo convertidos com `int` ou `float` conforme necessário. As strings são delimitadas por apóstrofos (`'`) e reconhecidas por um estado especial. O conteúdo é extraído sem as aspas exteriores com `t.value[1:-1]`.

Para o tratamento de comentários, foi definida uma regra simples que ignora qualquer sequência de caracteres delimitada por chavetas `{ ... }`. Esta regra não gera tokens e permite ao analisador léxico continuar a leitura normalmente após o comentário.
Desta forma, os comentários são removidos do fluxo de análise de forma eficiente, sem necessidade de estados personalizados ou manipulação adicional. Não foi implementado suporte a outros formatos como `(* ... *)` ou `//`.

O lexer também ignora espaços, tabs e quebras de linha com `t_ignore = ' \t'`, uma vez que não influenciam a estrutura gramatical da linguagem Pascal.

A função pré-definida `length` também é tratada no nível léxico como identificador ou palavras-chave específica, permitindo, posteriormente, a sua distinção semântica no parser.

Por fim, qualquer carácter que não seja reconhecido por nenhuma das regras anteriores é considerado inválido. Nestes casos, o lexer chama a função `t_error`, que imprime uma mensagem com o carácter ilegal encontrado e avança um carácter na análise, permitindo a continuação da compilação.

- Excertos do Lexer

  - Token de operador aritmético:

    ```python
    t_PLUS = r'\+'
    ```
    <p style="text-align: center; margin-top: -4px;"><em>Código 1: Token para o operador aritmético '+'</em></p>

  - Token de palavra-chave:

    ```python
    def t_BEGIN(t):
        r'\b[bB][eE][gG][iI][nN]\b'
        t.value = t.value.lower()
        return t
    ```
    <p style="text-align: center; margin-top: -4px;"><em>Código 2: Token para a palavra-chave begin </em></p>

  - Token de número: 
    
    ```python
    def t_NUMBER(t):
        r'\d+\.\d+|\d+'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t
    ```
    <p style="text-align: center; margin-top: -4px;"><em>Código 3: Token para números inteiros e reais</em></p> 

  - Token de string literal:

    ```python
    def t_STRING_LITERAL(t):
        r"'([^\\\n]|(\\.))*?'"
        t.value = t.value[1:-1]
        return t
    ```
    <p style="text-align: center; margin-top: -4px;"><em>Código 4: Token para literais de string entre apóstrofos</em></p>

  - Tratamento de erros:

    ```python
    def t_error(t):
        print(f"Carácter ilegal '{t.value[0]}'")
        t.lexer.skip(1)
    ```
    <p style="text-align: center; margin-top: -4px;"><em>Código 5: Tratamento de erros para carácteres inválidos</em></p>


### 2.2. Análise Sintática

O analisador sintático tem como objetivo validar se a sequência de tokens produzida pelo analisador léxico está de acordo com a gramática da linguagem Pascal. Para além da validação gramatical, o parser também é responsável por gerar o código correspondente para a máquina virtual (EWVM), à medida que reconhece estruturas válidas.

A implementação foi realizada com recurso à biblioteca `ply.yacc`, que permite definir regras sintáticas, como funções Python. Cada uma dessas funções representa uma produção da gramática e, quando acionada, executa ações semânticas que geram as instruções EWVM correspondentes.

O parser mantém uma tabela de variáveis que regista não só os identificadores, como também os seus tipos e dimensões (no caso de arrays). Esta estrutura permite validar se os identificadores estão corretamente declarados e se os tipos usados em expressões, atribuições e condições são compatíveis.

Foram incluídas verificações específicas para acesso a arrays, leitura e escrita com múltiplos argumentos, e chamadas a funções como `length`. Além disso, são gerados labels dinâmicos para estruturar o fluxo de execução de instruções condicionais e ciclos (`if-then-else`, `while`, `for`).

O parser assume, assim, um papel fundamental na ponte entre a estrutura lógica do programa em Pascal e a sua tradução para um conjunto de instruções sequenciais, tipadas e executáveis pela máquina virtual.

#### 2.2.1. Gramática

Inicialmente foi definida uma gramática do tipo bottom-up, capaz de reconhecer todos os tokens gerados pelo analisador léxico e construir corretamente o parser responsável pela validação estrutural do código fonte.

Segue-se um excerto de algumas regras que implementamos.

```python
programa        : PROGRAM ID ';' bloco '.'
bloco           : declaracoes BEGIN comandos END
declaracoes     : VAR lista_decl
                | empty
lista_decl      : lista_decl ID ':' tipo ';'
                | ID ':' tipo ';'
tipo            : INTEGER
                | DOUBLE
                | BOOLEAN
                | STRING
                | ARRAY '[' NUM '..' NUM ']' OF tipo
comandos        : comandos comando
                | comando
comando         : atribuicao ';'
                | leitura ';'
                | escrita ';'
                | condicional
                | ciclo
                | bloco
atribuicao      : ID ':=' expressao
                | ID '[' expressao ']' ':=' expressao
leitura         : READLN '(' lista_ids ')'
escrita         : WRITE '(' lista_expr ')'
                | WRITELN '(' lista_expr ')'
condicional     : IF expressao THEN comando
                | IF expressao THEN comando ELSE comando
ciclo           : WHILE expressao DO comando
                | FOR ID ':=' expressao TO expressao DO comando
                | FOR ID ':=' expressao DOWNTO expressao DO comando
lista_ids       : lista_ids ',' ID
                | ID
lista_expr      : lista_expr ',' expressao
                | expressao
expressao       : expressao '+' expressao
                | expressao '-' expressao
                | expressao '*' expressao
                | expressao '/' expressao
                | expressao DIV expressao
                | expressao MOD expressao
                | expressao AND expressao
                | expressao OR expressao
                | NOT expressao
                | expressao relop expressao
                | '(' expressao ')'
                | ID
                | ID '[' expressao ']'         (* Acesso a array *)
                | CHARAT '(' ID ',' expressao ')'  (* Acesso a string *)
                | LENGTH '(' ID ')'
                | NUM
                | STRING_LITERAL
                | TRUE
                | FALSE

```

O símbolo inicial `programa` representa um programa Pascal completo, que inclui a palavra-chave `program`, um `identificador`, um `bloco de código` e o `ponto final`. O símbolo bloco agrupa `declarações` e o corpo do programa é delimitado por `begin ... end`.

A secção `declaracoes` permite definir variáveis simples ou arrays, incluindo o tipo de dados. Os comandos aceites incluem atribuições, leitura, escrita, estruturas condicionais e ciclos.

As `expressões` podem ser aritméticas, lógicas ou relacionais, sendo suportadas todas as operações típicas da linguagem Pascal, bem como funções sobre strings (`length`) e acesso a arrays por índice.

A gramática foi concebida para ser modular, legível e compatível com a tradução direta para instruções da EWVM.

#### 2.2.2. Variáveis Auxiliares do Parser

Durante o processo de parsing e tradução para código EWVM, foram utilizadas variáveis auxiliares associadas ao objeto `parser`, de forma a controlar o estado da compilação e facilitar a geração de instruções. Estas variáveis são reiniciadas no início da análise através da função `reset_parser`.

- **parser.variaveis**: Dicionário onde são registadas as variáveis declaradas, com a sua posição na stack, tipo e, no caso de arrays, também os limites e dimensão.
- **parser.stack_pos**: Inteiro que representa a próxima posição livre na stack global, usada para alocar variáveis.
- **parser.ifCount / parser.elseCount**: Contadores usados para gerar labels únicos nas instruções `if-then[-else]`, permitindo aninhamento seguro.
- **parser.loopsCount**: Contador utilizado para gerar labels únicos em ciclos `for` e `while`, garantindo controlo correto de fluxo.
- **parser.success**: Flag booleana que indica se ocorreram erros durante a análise (léxica, sintática ou semântica).

Estas variáveis tornam o parser mais robusto e ajudam a estruturar corretamente o código gerado, assegurando a integridade das posições de memória e dos saltos de controlo.

## 3. Implementação

### 3.1. Operações e Expressões

O compilador suporta operações aritméticas (`+`, `-`, `*`, `/`, `div`, `mod`), relacionais (`=`, `<>`, `<`, `>`, `<=`, `>=`) e lógicas (`and`, `or`, `not`). A geração de código depende do tipo de operandos, sendo usadas instruções distintas para inteiros (`add`, `sub`, `mul`, `div`, `mod`) e para reais (`fadd`, `fsub`, `fmul`, `fdiv`). Comparações resultam sempre em valores booleanos e são convertidas para instruções como `equal`, `sup`, `inf`, entre outras.

#### Exemplo: Expressão aritmética com atribuição

```pascal
var a, b: integer;
begin
  b := 10;
  a := b + 2;
end.
```

**Output**

```shell
pushi 0
pushi 0
start
pushi 10
storeg 1
pushg 1
pushi 2
add
storeg 0
stop
```

### 3.2. Condicionais

As estruturas `if-then[-else]` são implementadas com recurso a labels gerados dinamicamente, permitindo condicionalmente saltar para o bloco adequado com `jz` e `jump`. Para suportar aninhamentos, são usados contadores auxiliares (`ifCount`, `elseCount`) que garantem nomes únicos para os labels.

#### Exemplo: Condicional simples

```pascal
program Teste;
var a, b: integer;
begin
  b := 10;
  if b > 5 then
    a := b + 2
  else
    a := 0;
end.
```

**Output**

```shell
pushi 0
pushi 0
start
pushi 10
storeg 1
pushg 1
pushi 5
sup
jz else0
pushg 1
pushi 2
add
storeg 0
jump endif0
else0:
pushi 0
storeg 0
endif0:
stop
```

### 3.3. Ciclos

O compilador suporta ciclos `for` com `to` e `downto`, e ciclos `while`. Todos usam labels dinâmicos e controlam a iteração através de comparações (`infeq`, `supeq`) e saltos condicionais. No `for`, o valor da variável de controlo é atualizado automaticamente, enquanto no `while` a condição é verificada no início de cada iteração.

#### Exemplo: Ciclo for com acumulação

```pascal
program Teste;
var i, soma: integer;
begin
  soma := 0;
  for i := 1 to 5 do
    soma := soma + i;
end.
```

**Output**

```shell
pushi 0
pushi 0
start
pushi 0
storeg 1
pushi 1
storeg 0
label0:
pushg 0
pushi 5
infeq
jz label1
pushg 1
pushg 0
add
storeg 1
pushg 0
pushi 1
add
storeg 0
jump label0
label1:
stop
```

### 3.4. Variáveis e Arrays

As variáveis são registadas na estrutura `parser.variaveis`, com posição na stack e tipo. Arrays são também suportados, com armazenamento do tamanho, limites e tipo base. O código gerado usa instruções como `storeg`, `pushg`, `loadn` e `storen`, conforme se trate de variáveis simples ou arrays indexados.

#### Exemplo: Declaração e uso de variáveis e arrays

```pascal
program Teste;
var a, i: integer;
    numeros: array[1..3] of integer;
begin
  numeros[1] := 10;
  a := numeros[1];
end.
```

**Output**

```shell
pushi 0
pushi 0
pushi 0
pushi 0
pushi 0
start
pushgp
pushi 1
pushi 1
sub
pushi 0
add
pushi 10
storen
pushgp
pushi 1
pushi 1
sub
pushi 0
add
loadn
storeg 3
stop
```

### 3.5. Leitura e Escrita

As instruções `readln`, `write` e `writeln` permitem interações com o utilizador. O tipo da variável determina o código gerado: `read + atoi` para inteiros, `read + atof` para reais, e `read` direto para strings. Na escrita, são usadas instruções como `writei`, `writef`, `writes` ou `writechr`, com conversões implícitas quando necessário.

#### Exemplo: Leitura e escrita de diferentes tipos

```pascal
program Teste;
var nome: string;
    idade: integer;
begin
  readln(nome);
  readln(idade);
  writeln('Nome:', nome);
  writeln('Idade:', idade);
end.
```

**Output**

```shell
pushs ""
pushi 0
start
read
storeg 1
read
atoi
storeg 0
pushs "Nome:"
writes
pushg 1
writes
writeln
pushs "Idade:"
writes
pushg 0
writei
writeln
stop
```

### 3.6. Suporte a Strings

Strings são tratadas como referências na stack e suportam operações como `length(s)` e `s[i]` (através de `strlen` e `charat`). Isto permite manipular textos diretamente e integrar os resultados em expressões ou instruções de escrita.

#### Exemplo: Operações com strings

```pascal
program Teste;
var texto: string;
    tamanho, codigo: integer;
begin
  texto := 'abc';
  tamanho := length(texto);
  codigo := texto[2];
end.
```

**Output**

```shell
pushs ""
pushi 0
pushi 0
start
pushs "abc"
storeg 2
pushg 2
strlen
storeg 0
pushg 2
pushi 2
pushi 1
sub
charat
storeg 1
stop
```

## 4. Testes

Foram realizados testes com os programas fornecidos no enunciado do projeto, abrangendo as principais construções da linguagem Pascal: declaração de variáveis, expressões aritméticas, estruturas condicionais, ciclos `for` e `while`, leitura e escrita, bem como manipulação de arrays e strings.

Estes testes permitiram validar a capacidade do compilador em diferentes fases — análise léxica, sintática, semântica e geração de código. Todos os programas foram traduzidos com sucesso para código EWVM e testados na plataforma oficial da máquina virtual [EWVM](https://ewvm.epl.di.uminho.pt), com resultados corretos e coerentes com os esperados em Pascal.

Apresentam-se de seguida dois exemplos representativos.

### Exemplo 1: Fatorial (`exemplo2.pas`)

Este programa calcula o fatorial de um número utilizando um ciclo `for`. É um teste importante para validar:

* o suporte a variáveis,
* a estrutura `for ... to`,
* operações aritméticas,
* escrita de resultados.

```pascal
fat := 1;
for i := 1 to n do
  fat := fat * i;
writeln(fat);
```

A tradução gerada para EWVM produz um ciclo com `label`, `infeq`, `add`, `mul`, e `storeg`, terminando com `writei` e `writeln`. O resultado é corretamente impresso, por exemplo, para `n = 5`, a saída esperada é `120`.

### Exemplo 2: Soma de Elementos (`exemplo5.pas`)

Este programa lê cinco inteiros para um array e calcula a sua soma acumulada. Testa:

* leitura com `readln`,
* acesso indexado a arrays (`numeros[i]`),
* operações acumulativas,
* escrita final do resultado.

```pascal
for i := 1 to 5 do
begin
  readln(numeros[i]);
  soma := soma + numeros[i];
end;
writeln(soma);
```

A tradução usa instruções `read`, `atoi`, `storen`, `loadn`, `add`, e `storeg`. O comportamento final corresponde ao somatório dos cinco valores inseridos, impresso corretamente.

Para além disso, fornecemos na diretoria `exemplos` uma série de exemplos para executar e verificar funcionalidades.

## 5. Considerações Adicionais

Durante o desenvolvimento do compilador, foram tomadas várias decisões técnicas com o objetivo de equilibrar a complexidade do sistema com a sua funcionalidade e clareza.

Uma dessas decisões foi optar por uma tradução imediata durante a análise sintática, sem construção de uma árvore sintática abstrata (AST). Esta abordagem permitiu uma geração de código mais direta e simplificada, embora com menor flexibilidade para otimizações futuras.

O compilador inclui suporte a verificação semântica básica, como a deteção de variáveis não declaradas, acesso indevido a arrays e verificação de tipos em expressões aritméticas e lógicas. Ainda assim, não foram implementadas verificações avançadas, como tipos de retorno de funções, dada a ausência de subprogramas.

O tratamento de erros foi assegurado em três níveis distintos:
- **Erros léxicos**: caracteres ilegais são reportados pelo lexer, que continua a análise ignorando o símbolo inválido;
- **Erros sintáticos**: regras de recuperação simples permitem ao parser sinalizar e continuar após detetar construções inválidas;
- **Erros semânticos**: são detetados manualmente nas ações semânticas das regras, como operações entre tipos incompatíveis ou acesos a índices fora dos limites declarados.

Finalmente, a modularização do código em ficheiros distintos (`lexer.py`, `parser.py`) permitiu manter a separação de responsabilidades e facilitou a manutenção e os testes do compilador.


## 6. Trabalho Futuro

Apesar de o compilador desenvolvido suportar as principais estruturas da linguagem Pascal, existem várias áreas que podem ser alvo de melhoria e extensão.

Uma das evoluções naturais será o suporte a subprogramas — nomeadamente `procedure` e `function` — com passagem de argumentos e retorno de valores. Esta funcionalidade permitiria modularizar o código Pascal e reutilizar blocos de lógica, aproximando ainda mais o compilador da linguagem original.

Outra melhoria importante prende-se com a construção de uma árvore sintática abstrata (AST) que permita uma separação clara entre análise e tradução. Esta estrutura intercalar tornaria o compilador mais modular e abriria portas a otimizações futuras.

A integração de um interpretador em modo interativo é também uma possibilidade, permitindo ao utilizador compilar e executar programas diretamente, sem necessidade de recorrer a uma plataforma externa.

Adicionalmente, poderão ser exploradas otimizações ao nível da geração de código, como eliminação de instruções redundantes, análise de constantes e reordenação de instruções para maior eficiência.

## 7. Conclusão

O desenvolvimento deste compilador para a linguagem Pascal constituiu uma oportunidade valiosa para consolidar os conhecimentos adquiridos ao longo da unidade curricular de *Processamento de Linguagens*. Ao longo do projeto, foi possível aplicar de forma prática os conceitos fundamentais da construção de compiladores — desde a análise léxica e sintática até à geração de código para uma máquina virtual específica (EWVM).

Apesar das limitações impostas pelo tempo e pelo âmbito do projeto, o compilador implementado suporta com sucesso as principais construções da linguagem Pascal, incluindo variáveis simples e arrays, estruturas condicionais, ciclos, leitura e escrita, bem como operações aritméticas e lógicas com conversão de tipos.

A decisão de gerar código diretamente durante o *parsing*, sem recorrer a estruturas intermédias como árvores sintáticas abstratas (AST), revelou-se acertada para este contexto académico, favorecendo a simplicidade, a clareza do código e a facilidade de testes.

Durante o processo, surgiram diversos desafios técnicos — como a correta gestão de tipos e posições na *stack*, a implementação de ciclos `for` com limites dinâmicos, ou a tradução de chamadas como `length` e `charat`. A sua resolução exigiu uma compreensão aprofundada das interações entre a sintaxe da linguagem, a semântica das construções e as instruções da máquina virtual.

Mais do que um exercício de programação, este projeto permitiu-nos desenvolver uma maior consciência sobre o funcionamento interno dos compiladores, o que certamente contribuirá para a nossa formação como engenheiros informáticos mais completos, rigorosos e conscientes das ferramentas que utilizamos no dia a dia.

