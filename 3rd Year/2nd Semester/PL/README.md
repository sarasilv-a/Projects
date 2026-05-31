# Processamento de Linguagens
---

## Grade: 16/20 ⭐
---

## Project: Pascal Standard Compiler
---

**Learning Outcomes**

- Understand the phases of compiler construction, including lexical, syntactic, and semantic analysis  
- Implement a compiler for the Pascal programming language targeting the EWVM virtual machine  
- Apply parsing techniques using Python libraries (`ply.lex` and `ply.yacc`)  
- Generate executable code for a stack-based virtual machine  
- Validate compiler functionality through testing on various Pascal program constructs  

---

## Project Overview

This project involved the development of a **Pascal Standard Compiler** as part of the *Processamento de Linguagens* course at Universidade do Minho. The compiler translates Pascal source code into instructions for the Educational Web Virtual Machine (EWVM), supporting key language features like variables, arrays, conditionals, loops, and input/output operations.

Key functionalities include:  

- Lexical analysis to tokenize Pascal code  
- Syntactic analysis to validate program structure and generate EWVM code  
- Semantic checks for type compatibility and variable declarations  
- Support for arithmetic, relational, and logical operations  
- Handling of arrays, strings, and control structures (if-then-else, for, while)  

### Main Features:
- Modular architecture with separate lexer (`ply.lex`) and parser (`ply.yacc`)  
- Support for Pascal constructs: variables (`integer`, `real`, `boolean`, `string`), arrays, conditionals, loops, and I/O (`readln`, `write`, `writeln`)  
- Direct code generation during parsing, without an abstract syntax tree (AST)  
- Semantic validation for undeclared variables, type mismatches, and array bounds  
- Execution and testing on the EWVM platform [](https://ewvm.epl.di.uminho.pt)  

---

## Implementation

- **Tools:** Python with `ply.lex` for lexical analysis and `ply.yacc` for syntactic analysis  
- **Lexical Analysis:** Tokenizes Pascal keywords, operators, identifiers, literals, and comments using regular expressions; case-insensitive handling and error reporting for invalid characters  
- **Syntactic Analysis:** Bottom-up parsing with a grammar supporting Pascal constructs; generates EWVM instructions for variables, arrays, conditionals, loops, and I/O  
- **Code Generation:** Produces stack-based EWVM instructions (e.g., `pushi`, `storeg`, `add`, `jz`) with dynamic labels for control flow  
- **Semantic Checks:** Tracks variable types, array bounds, and stack positions; validates operations and access to arrays/strings  

---

## Testing & Results

- Tested with provided Pascal programs covering variables, arrays, conditionals, loops, and I/O  
- Validated lexical, syntactic, and semantic phases using examples like factorial calculation and array summation  
- All test programs successfully compiled to EWVM code and executed correctly on the EWVM platform  
- Error handling tested for invalid characters, syntax errors, and semantic issues (e.g., undeclared variables, type mismatches)  
- Results confirmed correct output for arithmetic operations, control structures, and string manipulations  

---

## Developed by:

[Ana Carolina Penha Cerqueira](https://github.com/Cerqueira025)  
[Fernando Jorge da Silva Pires](https://github.com/ferjpires)  
[Sara Catarina Loureiro da Silva](https://github.com/sarasilv-a)  

