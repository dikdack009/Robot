# ------------------------------------------------------------
# Lexer.py
#
# tokenizer for language from task
# ------------------------------------------------------------
import ply.lex as lexer

class TALexer(object):
    def __init__(self):
        self.lexer = lexer.lex(module=self)

    reserved = {
        "true": "TRUE", "false": "FALSE",

        "boolean": "BOOLEAN", "cboolean": "CBOOLEAN",

        "int": "INT", "cint": "CINT", "map": "MAP",

        "inc": "INC", "dec": "DEC", "not": "NOT", "or": "OR", "gt": "GT", "lt": "LT",

        "while": "WHILE", "do": "DO",

        "if": "IF", "else": "ELSE",

        "step": "STEP", "right": "RIGHT", "left": "LEFT", "back": "BACK", "look": "LOOK",

        "proc": "PROC", "bar": "BAR", "emp": "EMP", "set": "SET", "clr": "CLR"
    }

    primitive_tokens = [
        "EQUAL",
        "ASSIGN",
        "LEFT_BRACKET",
        "RIGHT_BRACKET",
        "LEFT_SQUARE_BRACKET",
        "RIGHT_SQUARE_BRACKET",
        "NEW_LINE",
        "VARIABLE",
        "INT_DECIMAL"
    ]

    tokens = primitive_tokens + list(reserved.values())

    t_EQUAL = r"\="
    t_ASSIGN = r"\:\="
    t_LEFT_BRACKET = r"\("
    t_RIGHT_BRACKET = r"\)"
    t_LEFT_SQUARE_BRACKET = r"\["
    t_RIGHT_SQUARE_BRACKET = r"\]"

    t_ignore = ' \t'

    def t_VARIABLE(self, t):
        r"""[a-zA-Z][a-zA-Z_0-9]*"""
        t.type = self.reserved.get(t.value.lower(), "VARIABLE")  # Check for reserved words
        return t

    def t_INT_DECIMAL(self, t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    def t_LINE_BREAK(self, t):
        r"""\.\.\.\n+"""
        # Assign new value to line number depending on amount of \n escape-sequences
        t.lexer.lineno += len(t.value) - 3
        pass

    def t_NEW_LINE(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        print("\n[ERROR_HANDLER] Illegal character: '%s'" % t.value[0])
        print("[ERROR_HANDLER] Line: '%d'\n" % t.lexer.lineno)
        t.lexer.skip(1)

    def t_comment(self, t):
        r"""//.*\n+"""
        t.lexer.lineno += len(t.value) - len(t.value.replace("\n", ""))
        pass

    def token(self):
        return self.lexer.token()

    def input(self, data):
        return self.lexer.input(data)


if __name__ == '__main__':
    print("Test filename: ", end="")
    filename = input()
    filepath = '/Users/MI/PycharmProjects/TARobot/Testing/test_interpreter_' + filename

    f = open(filepath, 'r+')
    data = f.read()
    f.close()
    lexer = TALexer()
    lexer.input(data)
    while True:
        token = lexer.token()
        if token is None:
            break
        else:
            print(token)