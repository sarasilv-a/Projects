import ply.yacc as yacc
import os
import sys
from lexer import tokens

precedence = (
    ('right', 'NOT'),
    ('left', 'AND', 'OR'),
    ('nonassoc', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD', 'DIV_INT'),
)

def novo_label(prefixo):
    label = f"{prefixo}{getattr(novo_label, 'count', 0)}"
    novo_label.count = getattr(novo_label, 'count', 0) + 1
    return label

def reset_parser(parser):
    parser.variaveis = {}
    parser.stack_pos = 0
    parser.ifCount = 0
    parser.elseCount = 0
    parser.loopsCount = 0
    parser.success = True

def p_programa(p):
    'programa : PROGRAM ID SEMI declaracoes bloco DOT'
    p[0] = p[4] + "start\n" + p[5] + "stop"
    print("\u2192 Programa válido!\n\nCódigo VM gerado:")
    print(p[0])

def p_declaracoes(p):
    '''declaracoes : VAR lista_decls
                   | empty'''
    p[0] = p[2] if len(p) > 2 else ""

def p_lista_decls_array(p):
    'lista_decls : lista_idents COLON array_tipo SEMI lista_decls'
    nomes = p[1]
    lower, upper, tipo = p[3]
    tamanho = upper - lower + 1
    codigo = ""

    tipo = tipo.lower()
    for nome in nomes:
        if nome in p.parser.variaveis:
            print(f"Erro: variável {nome} já declarada.")
            parser.success = False
        else:
            pos = p.parser.stack_pos
            # Guardar posição, tamanho, limite inferior e tipo
            p.parser.variaveis[nome] = (pos, tamanho, lower, tipo)

            # Inicializar consoante o tipo
            if tipo == "string":
                codigo += ('pushs ""\n' * tamanho)
            elif tipo == "double":
                codigo += ('pushf 0.0\n' * tamanho)
            elif tipo in ("integer", "boolean"):
                codigo += ('pushi 0\n' * tamanho)
            else:
                print(f"Erro: tipo '{tipo}' desconhecido.")
                parser.success = False

            p.parser.stack_pos += tamanho

    p[0] = codigo + p[5]

def p_lista_decls_simples(p):
    'lista_decls : lista_idents COLON tipo SEMI lista_decls'
    nomes = p[1]
    tipo = p[3].lower()
    codigo = ""
    for nome in nomes:
        if nome in p.parser.variaveis:
            print(f"Erro: variável {nome} já declarada.")
            parser.success = False
        else:
            pos = p.parser.stack_pos
            # Guardar tipo
            p.parser.variaveis[nome] = (pos, tipo)

            # Inicializar consoante o tipo
            if tipo == "string":
                codigo += 'pushs ""\n'
            elif tipo == "double":
                codigo += 'pushf 0.0\n'
            elif tipo in ("integer", "boolean"):
                codigo += 'pushi 0\n'
            else:
                print(f"Erro: tipo '{tipo}' desconhecido.")
                parser.success = False

            p.parser.stack_pos += 1

    p[0] = codigo + p[5]

def p_lista_decls_empty(p):
    'lista_decls : empty'
    p[0] = ''

def p_array_tipo(p):
    'array_tipo : ARRAY LBRACK NUMBER DOTDOT NUMBER RBRACK OF tipo'
    lower = p[3]
    upper = p[5]
    tipo = p[8].lower()
    p[0] = (lower, upper, tipo)

def p_lista_idents(p):
    '''lista_idents : ID COMMA lista_idents
                    | ID'''
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

def p_tipo(p):
    '''tipo : INTEGER
            | DOUBLE
            | STRING
            | BOOLEAN'''
    p[0] = p[1]

def p_bloco(p):
    'bloco : BEGIN lista_comandos END'
    p[0] = p[2]

def p_lista_comandos(p):
    '''lista_comandos : comando SEMI lista_comandos
                      | comando
                      | empty'''
    if len(p) == 4:
        p[0] = p[1] + p[3]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ""

def p_comando_writeln(p):
    'comando : WRITELN LPAREN argumentos RPAREN'
    p[0] = p[3] + "writeln\n"

def p_comando_write(p):
    'comando : WRITE LPAREN argumentos RPAREN'
    p[0] = p[3] + "writeln\n"

def p_argumentos(p):
    '''argumentos : argumento COMMA argumentos
                  | argumento'''
    p[0] = p[1] if len(p) == 2 else p[1] + p[3]

def p_argumento_string(p):
    'argumento : STRING_LITERAL'
    p[0] = f'pushs "{p[1]}"\nwrites\n'

def p_argumento_expressao(p):
    'argumento : expressao'
    codigo, tipo = p[1]

    if tipo == "string":
        p[0] = codigo + "writes\n"
    elif tipo == "double":
        p[0] = codigo + "writef\n"
    elif tipo in ("integer", "boolean"):
        if codigo.strip().endswith("charat"):
            p[0] = codigo + "writechr\n"
        else:
            p[0] = codigo + "writei\n"
    else:
        print(f"Erro: tipo inválido para escrita: {tipo}")
        p[0] = ""
        parser.success = False

def p_comando_leitura(p):
    'comando : READLN LPAREN ID RPAREN'
    var = p[3]

    if var not in p.parser.variaveis:
        print(f"Erro: variável '{var}' não declarada.")
        p[0] = ""
        parser.success = False
        return

    val = p.parser.variaveis[var]

    if isinstance(val, tuple) and len(val) == 2:
        pos, tipo = val
    else:
        print(f"Erro: leitura inválida para variável '{var}' (possivelmente array).")
        p[0] = ""
        parser.success = False
        return

    if tipo == "string":
        p[0] = f"read\nstoreg {pos}\n"
    elif tipo == "integer":
        p[0] = f"read\natoi\nstoreg {pos}\n"
    elif tipo == "double":
        p[0] = f"read\natof\nstoreg {pos}\n"
    elif tipo == "boolean":
        p[0] = f"read\natoi\nstoreg {pos}\n"
    else:
        print(f"Erro: tipo de leitura desconhecido: {tipo}")
        p[0] = ""
        parser.success = False

def p_comando_leitura_array(p):
    'comando : READLN LPAREN ID LBRACK expressao RBRACK RPAREN'
    nome = p[3]

    if nome not in p.parser.variaveis or not isinstance(p.parser.variaveis[nome], tuple):
        print(f"Erro: array '{nome}' não declarado.")
        p[0] = ""
        parser.success = False
        return

    val = p.parser.variaveis[nome]

    if len(val) != 4:
        print(f"Erro: estrutura inválida no array '{nome}'")
        p[0] = ""
        parser.success = False
        return

    base, _, lower, tipo = val
    expr_code, expr_tipo = p[5]

    if expr_tipo != "integer":
        print(f"Erro: índice do array '{nome}' deve ser inteiro, não {expr_tipo}.")
        p[0] = ""
        parser.success = False
        return

    # Gerar leitura conforme o tipo do array
    if tipo == "string":
        leitura = "read\n"
    elif tipo == "integer" or tipo == "boolean":
        leitura = "read\natoi\n"
    elif tipo == "double":
        leitura = "read\natof\n"
    else:
        print(f"Erro: tipo de elementos do array '{nome}' desconhecido: {tipo}")
        p[0] = ""
        parser.success = False
        return

    p[0] = (
        "pushgp\n" +
        expr_code +
        f"pushi {lower}\nsub\n" +
        f"pushi {base}\nadd\n" +
        leitura +
        "storen\n"
    )

def p_comando_atribuicao(p):
    'comando : ID ASSIGN expressao'
    var = p[1]
    
    if var not in p.parser.variaveis:
        print(f"Erro: variável '{var}' não declarada.")
        p[0] = ""
        parser.success = False
        return
    
    val = p.parser.variaveis[var]
    
    if isinstance(val, tuple) and len(val) == 2:
        pos, tipo_var = val
    else:
        print(f"Erro: variável '{var}' é um array ou estrutura inválida para atribuição simples.")
        p[0] = ""
        parser.success = False
        return
    
    codigo_exp, tipo_exp = p[3]
    
    if tipo_var != tipo_exp:
        # Tentar conversões automáticas válidas
        if tipo_var == "double" and tipo_exp == "integer":
            codigo_exp += "itof\n"
            tipo_exp = "double"
        elif tipo_var == "integer" and tipo_exp == "double":
            codigo_exp += "ftoi\n"
            tipo_exp = "integer"
        elif tipo_var == "boolean" and tipo_exp == "integer":
            tipo_exp = "boolean"
        else:
            print(f"Erro: tipo incompatível na atribuição '{tipo_var} := {tipo_exp}'")
            p[0] = ""
            parser.success = False
            return

    p[0] = codigo_exp + f"storeg {pos}\n"

def p_comando_atribuicao_array(p):
    'comando : ID LBRACK expressao RBRACK ASSIGN expressao'
    nome = p[1]

    if nome not in p.parser.variaveis:
        print(f"Erro: array '{nome}' não declarado.")
        p[0] = ""
        parser.success = False
        return

    val = p.parser.variaveis[nome]

    if not (isinstance(val, tuple) and len(val) >= 3):
        print(f"Erro: estrutura inválida no array '{nome}'")
        p[0] = ""
        parser.success = False
        return

    base = val[0]
    lower = val[2]
    index_code, index_type = p[3]
    value_code, _ = p[6]

    if index_type != "integer":
        print(f"Erro: índice de '{nome}' deve ser inteiro.")
        p[0] = ""
        parser.success = False
        return

    p[0] = (
        "pushgp\n" +
        index_code +
        f"pushi {lower}\nsub\n" +
        f"pushi {base}\nadd\n" +
        value_code +
        "storen\n"
    )

def p_expressao(p):
    '''expressao : NOT expressao
                 | expressao PLUS termo
                 | expressao MINUS termo
                 | expressao MOD termo
                 | expressao DIV_INT termo
                 | expressao GT termo
                 | expressao LT termo
                 | expressao GE termo
                 | expressao LE termo
                 | expressao EQ termo
                 | expressao NE termo
                 | termo'''
    if len(p) == 3 and p.slice[1].type == 'NOT':
        cod, tipo = p[2]
        if tipo != "boolean":
            print("Erro: operador 'not' requer expressão booleana.")
            p[0] = ("", None)
            parser.success = False
            return
        p[0] = (cod + "not\n", "boolean")
        return
    elif len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4 and isinstance(p[2], str) and p[2] in ['+', '-']:
        cod1, tipo1 = p[1]
        cod2, tipo2 = p[3]
        if tipo1 != tipo2:
            print(f"Erro: tipos incompatíveis em expressão: {tipo1} {p[2]} {tipo2}")
            p[0] = ("", None)
            parser.success = False
            return
        instr = "add" if p[2] == '+' else "sub"
        if tipo1 == "double":
            instr = "f" + instr
        p[0] = (cod1 + cod2 + instr + "\n", tipo1)
    elif len(p) == 4:
        cod1, tipo1 = p[1]
        op = p[2]
        cod2, tipo2 = p[3]

        cod1, tipo1 = p[1]
        op = p[2]
        cod2, tipo2 = p[3]

        # Tratar comparação especial: char '1' como inteiro
        if tipo1 == "integer" and tipo2 == "string":
            if cod2.strip().startswith("pushs") and len(cod2.strip().split('"')[1]) == 1:
                ascii_code = ord(cod2.strip().split('"')[1])
                cod2 = f"pushi {ascii_code}\n"
                tipo2 = "integer"
        elif tipo1 == "string" and tipo2 == "integer":
            if cod1.strip().startswith("pushs") and len(cod1.strip().split('"')[1]) == 1:
                ascii_code = ord(cod1.strip().split('"')[1])
                cod1 = f"pushi {ascii_code}\n"
                tipo1 = "integer"

        if tipo1 != tipo2:
            print(f"Erro: tipos incompatíveis na comparação: {tipo1} {op} {tipo2}")
            p[0] = ("", None)
            parser.success = False
            return

        if tipo1 == "integer" or tipo1 == "boolean":
            op_map = {
                '>': 'sup', '<': 'inf', '=': 'equal',
                '<>': 'nequal', '>=': 'supeq', '<=': 'infeq'
            }
        elif tipo1 == "double":
            op_map = {
                '>': 'fsup', '<': 'finf', '=': 'equal',
                '<>': 'nequal', '>=': 'fsupeq', '<=': 'finfeq'
            }
        else:
            print(f"Erro: tipo '{tipo1}' não suporta comparações com '{op}'")
            p[0] = ("", None)
            parser.success = False
            return

        instr = op_map.get(op)
        if instr is None:
            print(f"Erro: operador relacional inválido: '{op}'")
            p[0] = ("", None)
            parser.success = False
            return

        p[0] = (cod1 + cod2 + instr + "\n", "boolean")

def p_termo(p):
    '''termo : termo TIMES fator
             | termo DIVIDE fator
             | termo DIV_INT fator
             | termo MOD fator
             | fator'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        cod1, tipo1 = p[1]
        cod2, tipo2 = p[3]
        op = p.slice[2].type

        if tipo1 != tipo2:
            print(f"Erro: tipos incompatíveis em termo: {tipo1} {p[2]} {tipo2}")
            p[0] = ("", None)
            parser.success = False
            return

        if tipo1 == "integer":
            op_map = {'TIMES': 'mul', 'DIVIDE': 'div', 'DIV_INT': 'div', 'MOD': 'mod'}
        elif tipo1 == "double":
            op_map = {'TIMES': 'fmul', 'DIVIDE': 'fdiv'}  # fmod não existe!
        else:
            print(f"Erro: tipo '{tipo1}' não suporta operador '{p[2]}'")
            p[0] = ("", None)
            parser.success = False
            return

        instr = op_map.get(op)
        if instr is None:
            print(f"Erro: operador '{p[2]}' inválido para tipo '{tipo1}'")
            p[0] = ("", None)
            parser.success = False
            return

        p[0] = (cod1 + cod2 + instr + "\n", tipo1)

def p_fator(p):
    '''fator : NUMBER
             | ID
             | TRUE
             | FALSE'''
    
    if isinstance(p[1], int):
        p[0] = (f"pushi {p[1]}\n", "integer")
    elif p.slice[1].type == 'TRUE':
        p[0] = ("pushi 1\n", "boolean")
    elif p.slice[1].type == 'FALSE':
        p[0] = ("pushi 0\n", "boolean")
    elif p[1] in p.parser.variaveis:
        val = p.parser.variaveis[p[1]]
        if isinstance(val, tuple):
            if len(val) == 2:
                pos, tipo = val
                p[0] = (f"pushg {pos}\n", tipo)
            else:
                print(f"Erro: uso de array '{p[1]}' sem índice.")
                p[0] = ("", None)
                parser.success = False
        else:
            print(f"Erro interno: estrutura inesperada em variável '{p[1]}'")
            p[0] = ("", None)
            parser.success = False
    else:
        print(f"Erro: variável '{p[1]}' não declarada.")
        p[0] = ("", None)
        parser.success = False

def p_fator_array(p):
    'fator : ID LBRACK expressao RBRACK'
    nome = p[1]

    if nome not in p.parser.variaveis:
        print(f"Erro: variável '{nome}' não declarada.")
        p[0] = ("", None)
        parser.success = False
        return

    val = p.parser.variaveis[nome]

    expr_code, expr_tipo = p[3]
    if expr_tipo != "integer":
        print(f"Erro: índice de '{nome}' deve ser inteiro.")
        p[0] = ("", None)
        parser.success = False
        return

    if isinstance(val, tuple) and len(val) == 2:
        pos, tipo = val
        if tipo == "string":
            p[0] = (
                f"pushg {pos}\n" + 
                expr_code +
                "pushi 1\nsub\n" +
                "charat\n"
            , "integer")
            return
        else:
            print(f"Erro: acesso com índice inválido para tipo '{tipo}' em '{nome}'")
            p[0] = ("", None)
            parser.success = False
            return

    if isinstance(val, tuple) and len(val) == 4:
        base = val[0]
        lower = val[2]
        tipo = val[3]

        p[0] = (
            "pushgp\n" +
            expr_code +
            f"pushi {lower}\nsub\n" +
            f"pushi {base}\nadd\n" +
            "loadn\n"
        , tipo)
        return

    print(f"Erro: estrutura inesperada para '{nome}'.")
    p[0] = ("", None)
    parser.success = False

def p_fator_string(p):
    'fator : STRING_LITERAL'
    p[0] = (f'pushs "{p[1]}"\n', "string")

def p_fator_paren(p):
    'fator : LPAREN expressao RPAREN'
    p[0] = p[2]

def p_fator_length(p):
    'fator : LENGTH LPAREN ID RPAREN'
    var = p[3]

    if var not in p.parser.variaveis:
        print(f"Erro: variável '{var}' não declarada.")
        p[0] = ("", None)
        parser.success = False
        return

    val = p.parser.variaveis[var]

    if isinstance(val, tuple) and len(val) == 2:
        _, tipo = val
        if tipo != "string":
            print(f"Erro: 'length' só se aplica a strings, não a '{tipo}'")
            p[0] = ("", None)
            parser.success = False
            return
        pos, _ = val
        p[0] = (f"pushg {pos}\nstrlen\n", "integer")
    else:
        print(f"Erro: 'length' não é aplicável a arrays.")
        p[0] = ("", None)
        parser.success = False

def p_operador_rel(p):
    '''operador_rel : GT
                    | LT
                    | EQ
                    | NE
                    | GE
                    | LE'''
    p[0] = p[1]

def p_condicao(p):
    '''condicao : condicao AND condicao
            | condicao OR condicao
            | NOT condicao
            | LPAREN condicao RPAREN
            | expressao operador_rel expressao
            | expressao
            '''
    if len(p) == 3 and p.slice[1].type == 'NOT':
        cod, tipo = p[2]
        if tipo != "boolean":
            print("Erro: operador 'not' requer condição booleana.")
            p[0] = ("", None)
            parser.success = False
            return
        p[0] = (cod + "not\n", "boolean")

    if len(p) == 4 and p[2] in ("and", "or"):
        cod1, tipo1 = p[1]
        cod2, tipo2 = p[3]
        if tipo1 != "boolean" or tipo2 != "boolean":
            print(f"Erro: operador lógico '{p[2]}' exige operandos booleanos.")
            p[0] = ("", None)
            parser.success = False
            return
        op = "and" if p[2].lower() == "and" else "or"
        p[0] = (cod1 + cod2 + f"{op}\n", "boolean")

    elif len(p) == 4 and p[1] == '(':
        p[0] = p[2]

    elif len(p) == 4:
        cod1, tipo1 = p[1]
        op = p[2]
        cod2, tipo2 = p[3]

        # Conversão string-char para inteiro se necessário
        if tipo1 == "integer" and tipo2 == "string":
            if cod2.strip().startswith("pushs") and len(cod2.strip().split('\"')[1]) == 1:
                cod2 = f"pushi {ord(cod2.strip().split('\"')[1])}\n"
                tipo2 = "integer"
        elif tipo1 == "string" and tipo2 == "integer":
            if cod1.strip().startswith("pushs") and len(cod1.strip().split('\"')[1]) == 1:
                cod1 = f"pushi {ord(cod1.strip().split('\"')[1])}\n"
                tipo1 = "integer"

        if tipo1 != tipo2:
            print(f"Erro: tipos incompatíveis na comparação: {tipo1} {op} {tipo2}")
            p[0] = ("", None)
            parser.success = False
            return

        if tipo1 == "integer" or tipo1 == "boolean":
            op_map = {
                '>': 'sup', '<': 'inf', '=': 'equal',
                '<>': 'nequal', '>=': 'supeq', '<=': 'infeq'
            }
        elif tipo1 == "double":
            op_map = {
                '>': 'fsup', '<': 'finf', '=': 'equal',
                '<>': 'nequal', '>=': 'fsupeq', '<=': 'finfeq'
            }
        else:
            print(f"Erro: tipo '{tipo1}' não suporta comparações com '{op}'")
            p[0] = ("", None)
            parser.success = False
            return

        instr = op_map.get(op)
        if instr is None:
            print(f"Erro: operador relacional inválido: '{op}'")
            p[0] = ("", None)
            parser.success = False
            return

        p[0] = (cod1 + cod2 + f"{instr}\n", "boolean")

    elif len(p) == 2:
        cod, tipo = p[1] if isinstance(p[1], tuple) else (None, None)
        if cod is not None and tipo == "boolean":
            p[0] = (cod, "boolean")
        elif isinstance(p[1], str):
            var = p[1]
            if var not in p.parser.variaveis:
                print(f"Erro: variável '{var}' não declarada.")
                p[0] = ("", None)
                parser.success = False
            else:
                pos_tipo = p.parser.variaveis[var]
                if len(pos_tipo) != 2 or pos_tipo[1] != "boolean":
                    print(f"Erro: variável '{var}' não é booleana.")
                    p[0] = ("", None)
                    parser.success = False
                else:
                    pos, _ = pos_tipo
                    p[0] = (f"pushg {pos}\n", "boolean")
        else:
            print("Erro: condição inválida.")
            p[0] = ("", None)
            parser.success = False

def p_comando_if(p):
    '''comando : IF condicao THEN comando
               | IF condicao THEN comando ELSE comando'''
    cond_code, cond_type = p[2]
    if cond_type != "boolean":
        print("Erro: condição do IF não é booleana.")
        parser.success = False
        p[0] = ""
        return

    if len(p) == 5:
        end = f"endif{p.parser.ifCount}"; p.parser.ifCount += 1
        p[0] = cond_code + f"jz {end}\n" + p[4] + f"{end}:\n"
    else:
        else_ = f"else{p.parser.elseCount}"
        end = f"endif{p.parser.ifCount}"
        p.parser.ifCount += 1; p.parser.elseCount += 1
        p[0] = (
            cond_code +
            f"jz {else_}\n" +
            p[4] +
            f"jump {end}\n" +
            f"{else_}:\n" +
            p[6] +
            f"{end}:\n"
        )

def p_comando_for(p):
    '''comando : FOR ID ASSIGN expressao TO expressao DO bloco_comando
               | FOR ID ASSIGN expressao DOWNTO expressao DO bloco_comando'''
    var = p[2]

    if var not in p.parser.variaveis:
        print(f"Erro: variável '{var}' não declarada.")
        p[0] = ""
        parser.success = False
        return

    val = p.parser.variaveis[var]
    if not isinstance(val, tuple) or len(val) != 2:
        print(f"Erro: variável '{var}' é um array ou inválida.")
        p[0] = ""
        parser.success = False
        return

    idx, tipo_var = val
    cod_start, tipo_start = p[4]
    cod_end, tipo_end = p[6]

    if tipo_var != "integer" or tipo_start != "integer" or tipo_end != "integer":
        print("Erro: FOR só é permitido com variáveis e limites do tipo integer.")
        p[0] = ""
        parser.success = False
        return

    body = p[8]
    lstart = f"label{p.parser.loopsCount}"
    lend = f"label{p.parser.loopsCount+1}"
    p.parser.loopsCount += 2

    if p[5].lower() == "to":
        p[0] = (
            cod_start +
            f"storeg {idx}\n{lstart}:\n" +
            f"pushg {idx}\n" + cod_end +
            f"infeq\njz {lend}\n" +
            body +
            f"pushg {idx}\npushi 1\nadd\nstoreg {idx}\njump {lstart}\n{lend}:\n"
        )
    else:
        p[0] = (
            cod_start +
            f"storeg {idx}\n{lstart}:\n" +
            f"pushg {idx}\n" + cod_end +
            f"supeq\njz {lend}\n" +
            body +
            f"pushg {idx}\npushi 1\nsub\nstoreg {idx}\njump {lstart}\n{lend}:\n"
        )

def p_comando_while(p):
    'comando : WHILE condicao DO bloco_comando'
    lstart = f"label{p.parser.loopsCount}"
    lend = f"label{p.parser.loopsCount+1}"
    p.parser.loopsCount += 2

    codigo_cond, tipo = p[2]
    if tipo != "boolean":
        print("Erro: a condição do while não é booleana.")
        parser.success = False
        p[0] = ""
        return

    p[0] = f"{lstart}:\n{codigo_cond}jz {lend}\n{p[4]}jump {lstart}\n{lend}:\n"

def p_bloco_comando(p):
    '''bloco_comando : comando
                     | bloco'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = ''

def p_error(p):
    if p: print(f"Erro de sintaxe na linha {p.lineno}, perto de '{p.value}'"); parser.success = False
    else: print("Erro de sintaxe: fim inesperado do ficheiro."); parser.success = False

parser = yacc.yacc()
reset_parser(parser)

if __name__ == "__main__":
    from contextlib import redirect_stdout

    with open("exemplos/exemplo6.pas", "r", encoding="utf-8") as f:
        codigo = f.read()

    with open("ewvm_output.txt", "w", encoding="utf-8") as out:
        with redirect_stdout(out):
            reset_parser(parser)
            parser.parse(codigo)

