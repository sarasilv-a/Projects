import ply.lex as lex

# =====================
# Lista de Tokens
# =====================

tokens = [
    'PROGRAM', 'BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'WRITELN', 'WRITE', 'READLN', 'VAR',
    'ID', 'NUMBER', 'STRING_LITERAL',
    'INTEGER', 'DOUBLE', 'STRING', 'BOOLEAN',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'ASSIGN', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'LPAREN', 'RPAREN',
    'SEMI', 'COLON', 'DOT', 'COMMA',
    'FOR', 'TO', 'DOWNTO', 'DO', 'WHILE',
    'TRUE', 'FALSE', 'DIV_INT', 'MOD', 'AND', 'OR', 'NOT',
    'ARRAY', 'OF', 'LBRACK', 'RBRACK', 'DOTDOT', 'LENGTH',
]

# =====================
# Tokens Simples (Regex direto)
# =====================

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_ASSIGN  = r':='
t_EQ      = r'='
t_NE      = r'<>'
t_LT      = r'<'
t_LE      = r'<='
t_GT      = r'>'
t_GE      = r'>='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_SEMI    = r';'
t_COLON   = r':'
t_DOT     = r'\.'
t_COMMA   = r','
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_DOTDOT = r'\.\.'

# =====================
# Ignorados
# =====================

t_ignore = ' \t'

# =====================
# Palavras Reservadas (Case-insensitive)
# =====================

def t_PROGRAM(t):  r'\b[pP][rR][oO][gG][rR][aA][mM]\b'; t.value = t.value.lower(); return t
def t_BEGIN(t):    r'\b[bB][eE][gG][iI][nN]\b'; t.value = t.value.lower(); return t
def t_END(t):      r'\b[eE][nN][dD]\b'; t.value = t.value.lower(); return t
def t_IF(t):       r'\b[iI][fF]\b'; t.value = t.value.lower(); return t
def t_THEN(t):     r'\b[tT][hH][eE][nN]\b'; t.value = t.value.lower(); return t
def t_ELSE(t):     r'\b[eE][lL][sS][eE]\b'; t.value = t.value.lower(); return t
def t_WRITELN(t):  r'\b[wW][rR][iI][tT][eE][lL][nN]\b'; t.value = t.value.lower(); return t
def t_WRITE(t):    r'\b[wW][rR][iI][tT][eE]\b'; t.value = t.value.lower(); return t
def t_READLN(t):   r'\b[rR][eE][aA][dD][lL][nN]\b'; t.value = t.value.lower(); return t
def t_VAR(t):      r'\b[vV][aA][rR]\b'; t.value = t.value.lower(); return t
def t_FOR(t):      r'\b[fF][oO][rR]\b'; t.value = t.value.lower(); return t
def t_TO(t):       r'\b[tT][oO]\b'; t.value = t.value.lower(); return t
def t_INTEGER(t):  r'\b[iI][nN][tT][eE][gG][eE][rR]\b';   t.value = t.value.lower(); return t
def t_DOUBLE(t):   r'\b[dD][oO][uU][bB][lL][eE]\b';       t.value = t.value.lower(); return t
def t_STRING(t):   r'\b[sS][tT][rR][iI][nN][gG]\b';       t.value = t.value.lower(); return t
def t_BOOLEAN(t):  r'\b[bB][oO][oO][lL][eE][aA][nN]\b';   t.value = t.value.lower(); return t
def t_DOWNTO(t):   r'\b[dD][oO][wW][nN][tT][oO]\b'; t.value = t.value.lower(); return t
def t_DO(t):       r'\b[dD][oO]\b'; t.value = t.value.lower(); return t
def t_WHILE(t):    r'\b[wW][hH][iI][lL][eE]\b'; t.value = t.value.lower(); return t
def t_TRUE(t):     r'\b[tT][rR][uU][eE]\b'; t.type = 'TRUE'; t.value = 1; return t
def t_FALSE(t):    r'\b[fF][aA][lL][sS][eE]\b'; t.type = 'FALSE'; t.value = 0; return t
def t_DIV_INT(t):  r'\b[dD][iI][vV]\b'; t.type = 'DIV_INT'; return t
def t_MOD(t):      r'\b[mM][oO][dD]\b'; t.type = 'MOD'; return t
def t_AND(t):      r'\b[aA][nN][dD]\b'; t.type = 'AND'; return t
def t_OR(t):       r'\b[oO][rR]\b'; t.type = 'OR'; return t
def t_NOT(t): r'\b[nN][oO][tT]\b'; t.type = 'NOT'; return t
def t_ARRAY(t):    r'\b[aA][rR][rR][aA][yY]\b'; t.value = t.value.lower(); return t
def t_OF(t):       r'\b[oO][fF]\b'; t.value = t.value.lower(); return t
def t_LENGTH(t):   r'\b[lL][eE][nN][gG][tT][hH]\b'; t.value = t.value.lower(); return t

# =====================
# Tokens Gerais
# =====================

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = 'ID'
    return t

def t_NUMBER(t):
    r'\d+\.\d+|\d+'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\'([^\\\n]|(\\.))*?\''
    t.value = t.value[1:-1]
    return t

# =====================
# Outros
# =====================

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'\{[^}]*\}'
    pass

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# =====================
# Construção do Lexer
# =====================

lexer = lex.lex()
