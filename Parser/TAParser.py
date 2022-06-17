import enum
import sys

from Lexer.TALexer import TALexer
import ply.yacc as yacc


class NodeType(enum.Enum):
    Program = "program"
    SentenceList = "sentence_list"
    ID = "id"
    Declaration = "declaration"
    Assignment = "assignment"
    Expression = "expression"
    Type = "type"
    Int = "int"
    Boolean = "boolean"
    If = "if"
    While = "while"
    Proc = "proc"
    Arguments = "arguments"
    Proc_call = "proc_call"
    MAP = "map"
    INC = "inc"
    DEC = "dec"


class NodeOfST:
    def __init__(self, node_type, value, children=None, lineno=-1):
        if children is None:
            children = []
        self.type = node_type
        self.value = value
        self.children = children
        self.lineno = lineno

    def __repr__(self):
        if isinstance(self.value, NodeOfST):
            return "• [" + f"Type: {self.type} - Value: STNode with type: {self.value.children}" + "]"
        return "• [" + f"Type: {self.type} - Value: {self.value}" + "]"

    def __str__(self, level=0):
        result = "\t" * level + repr(self) + "\n"
        for child in self.children:
            result += child.__str__(level + 1)
        return result


class NodeSTBuilder:
    def program(self, p):
        p[0] = NodeOfST(node_type=NodeType.Program.value, value="prog", children=[p[1]], lineno=p.lineno(1))

    def sentence_list(self, p):
        if len(p) == 2:
            p[0] = NodeOfST(node_type=NodeType.SentenceList.value, value="", children=[p[1]], lineno=p.lineno(1))
        elif len(p) == 3:
            p[0] = NodeOfST(node_type=NodeType.SentenceList.value, value="", children=[p[1], p[2]], lineno=p.lineno(1))

    def single_sentence(self, p):
        p[0] = p[1]

    def declaration(self, p):
        if len(p) == 5:
            child = NodeOfST(node_type=NodeType.ID.value, value=p[2], children=[], lineno=p.lineno(2))
            p[0] = NodeOfST(node_type=NodeType.Declaration.value, value=[p[1]], children=[child, p[4]],
                            lineno=p.lineno(2))
        elif len(p) == 3:
            p[0] = NodeOfST(node_type=NodeType.MAP.value, value="", children=[p[2]], lineno=p.lineno(2))

    def type(self, p):
        p[0] = NodeOfST(node_type=NodeType.Type.value, value=p[1], children=[], lineno=p.lineno(1))

    def int(self, p):
        p[0] = p[1]

    def boolean(self, p):
        p[0] = p[1]

    def assignment(self, p):
        p[0] = NodeOfST(node_type=NodeType.Assignment.value, value=p[1], children=[p[3]], lineno=p.lineno(2))

    def inc(self, p):
        p[0] = NodeOfST(node_type=NodeType.INC.value, value="", children=[p[2], p[3]], lineno=p.lineno(2))

    def dec(self, p):
        p[0] = NodeOfST(node_type=NodeType.DEC.value, value="", children=[p[2], p[3]], lineno=p.lineno(2))

    def robot_action(self, p):
        p[0] = NodeOfST(node_type='robot', value=p[1], children=[], lineno=p.lineno(1))

    def expression(self, p):
        p[0] = NodeOfST(node_type=NodeType.Expression.value, value="", children=[p[1]], lineno=p.lineno(1))

    def logical(self, p):
        p[0] = NodeOfST(node_type='logical', value=p[1], children=[], lineno=p.lineno(1))

    def not_p(self, p):
        p[0] = NodeOfST(node_type="not", value="", children=[p[2]], lineno=p.lineno(2))

    def or_p(self, p):
        p[0] = NodeOfST(node_type="or", value="", children=[p[2], p[3]], lineno=p.lineno(2))

    def or_arg(self, p):
        p[0] = p[1]

    def lt(self, p):
        p[0] = NodeOfST(node_type="lt", value="", children=[p[2], p[3]], lineno=p.lineno(2))

    def gt(self, p):
        p[0] = NodeOfST(node_type="gt", value="", children=[p[2], p[3]], lineno=p.lineno(2))

    def math_expression(self, p):
        p[0] = p[1]

    def while_p(self, p):
        if len(p) == 6:
            conditionChild = p[2]
            bodyChild = p[5]
            p[0] = NodeOfST(node_type=NodeType.While.value, value="", children=[conditionChild, bodyChild],
                            lineno=p.lineno(1))
        else :
            conditionChild = p[2]
            bodyChild = p[6]
            p[0] = NodeOfST(node_type=NodeType.While.value, value="", children=[conditionChild, bodyChild],
                            lineno=p.lineno(1))

    def proc(self, p):
        argumentsChild = p[4]
        bodyChild = p[7]
        value = p[2]
        p[0] = NodeOfST(node_type=NodeType.Proc.value, value=value, children=[argumentsChild, bodyChild],
                        lineno=p.lineno(1))

    def proc_args(self, p):
        if len(p) == 2:
            p[0] = p[1]
        else :
            p[0] = NodeOfST(node_type=NodeType.Arguments.value, value="", children=[p[1], p[2]], lineno=p.lineno(1))

    def proc_call(self, p):
        p[0] = NodeOfST(node_type=NodeType.Proc_call.value, value=p[1], children=[p[3]], lineno=p.lineno(1))

    def map_action(self, p):
        p[0] = NodeOfST(node_type=NodeType.MAP.value, value=p[1], children=[p[3], p[4], p[5], p[6]], lineno=p.lineno(1))

    def if_p(self, p):
        if len(p) == 7:
            conditionChild = p[2]
            bodyChild = p[5]
            p[0] = NodeOfST(node_type=NodeType.If.value, value="", children=[conditionChild, bodyChild],
                            lineno=p.lineno(1))
        else:
            conditionChild = p[2]
            bodyChild = p[5]
            elseChild = p[10]
            p[0] = NodeOfST(node_type=NodeType.If.value, value="", children=[conditionChild, bodyChild, elseChild],
                            lineno=p.lineno(1))

    def declaration_error1(self, p):
        p[0] = NodeOfST(node_type='error', value="bad declaration", children=[p[2]], lineno=p.lineno(2))
        sys.stderr.write(
            f"Line {p.lineno(2)} [SYNTAX ERROR]: Bad declaration configuration: variable '{p[2]}' should have initial value\n")

class TAParser(object):
    tokens = TALexer.tokens
    node_builder = NodeSTBuilder()

    def __init__(self):
        self.lexer = TALexer()
        self.parser = yacc.yacc(module=self)
        self.funcTable = dict()
        self.hasSyntaxErrors = False

    def parse(self, input_data, debug=False):
        parse_result = self.parser.parse(input_data, debug=debug)
        return parse_result, self.funcTable, self.hasSyntaxErrors

    def p_program(self, p):
        """program : sentence_list"""
        self.node_builder.program(p)

    def p_sentence_list(self, p):
        """sentence_list : sentence_list single_sentence
                         | single_sentence"""
        self.node_builder.sentence_list(p)

    def p_single_sentence(self, p):
        """single_sentence : declaration NEW_LINE
                           | assignment NEW_LINE
                           | if NEW_LINE
                           | while NEW_LINE
                           | proc NEW_LINE
                           | proc_call NEW_LINE
                           | robot_action NEW_LINE
                           | inc NEW_LINE
                           | dec NEW_LINE
                           | logical NEW_LINE"""
        self.node_builder.single_sentence(p)

    def p_declaration(self, p):
        """declaration : type VARIABLE EQUAL expression
                        | MAP VARIABLE"""
        self.node_builder.declaration(p)

    def p_type(self, p):
        """type : int
                | boolean"""
        self.node_builder.type(p)

    def p_error(self, p):
        try:
            print("Syntax error, line: %d\n" % p.lineno)
        except Exception:
            print("Syntax error")
        self.hasSyntaxErrors = True

    def p_int(self, p):
        """int : INT
                | CINT"""
        self.node_builder.int(p)

    def p_boolean(self, p):
        """boolean : BOOLEAN
                    | CBOOLEAN"""
        self.node_builder.boolean(p)

    def p_assignment(self, p):
        """assignment : VARIABLE ASSIGN expression"""
        self.node_builder.assignment(p)

    def p_if(self, p):
        """if : IF logical LEFT_BRACKET NEW_LINE sentence_list RIGHT_BRACKET
                    | IF logical LEFT_BRACKET NEW_LINE sentence_list RIGHT_BRACKET ELSE LEFT_BRACKET NEW_LINE sentence_list RIGHT_BRACKET"""
        self.node_builder.if_p(p)

    def p_inc(self, p):
        """inc : INC expression expression"""
        self.node_builder.inc(p)

    def p_dec(self, p):
        """dec : DEC expression expression"""
        self.node_builder.dec(p)

    def p_while(self, p):
        """while : WHILE logical NEW_LINE DO single_sentence
                            | WHILE logical NEW_LINE DO LEFT_BRACKET NEW_LINE sentence_list RIGHT_BRACKET"""
        self.node_builder.while_p(p)

    def p_proc(self, p):
        """proc : PROC VARIABLE LEFT_SQUARE_BRACKET proc_args RIGHT_SQUARE_BRACKET LEFT_BRACKET NEW_LINE sentence_list RIGHT_BRACKET"""
        self.node_builder.proc(p)

    def p_proc_args(self, p):
        """proc_args : VARIABLE
                        | proc_args VARIABLE"""
        self.node_builder.proc_args(p)

    def p_proc_call(self, p):
        """proc_call : VARIABLE LEFT_SQUARE_BRACKET proc_args RIGHT_SQUARE_BRACKET"""
        self.node_builder.proc_call(p)

    def p_robot_action(self, p):
        """robot_action : STEP
                        | BACK
                        | RIGHT
                        | LEFT
                        | LOOK"""
        self.node_builder.robot_action(p)

    def p_map_action(self, p):
        """map_action : BAR LEFT_SQUARE_BRACKET VARIABLE VARIABLE VARIABLE VARIABLE RIGHT_SQUARE_BRACKET
                        | EMP LEFT_SQUARE_BRACKET VARIABLE VARIABLE VARIABLE VARIABLE RIGHT_SQUARE_BRACKET
                        | SET LEFT_SQUARE_BRACKET VARIABLE VARIABLE VARIABLE VARIABLE RIGHT_SQUARE_BRACKET
                        | CLR LEFT_SQUARE_BRACKET VARIABLE VARIABLE VARIABLE VARIABLE RIGHT_SQUARE_BRACKET"""
        self.node_builder.map_action(p)

    def p_expression(self, p):
        """expression : math_expression
                      | VARIABLE
                      | logical
                      | robot_action"""
        self.node_builder.expression(p)

    def p_logical(self, p):
        """logical : not
                    | or
                    | lt
                    | gt
                    | TRUE
                    | FALSE"""
        self.node_builder.logical(p)

    def p_not(self, p):
        """not : NOT logical
                    | NOT proc_call"""
        self.node_builder.not_p(p)

    def p_or(self, p):
        """or : OR or_arg or_arg"""
        self.node_builder.or_p(p)

    def p_or_arg(self, p):
        """or_arg : logical
                        | proc_call"""
        self.node_builder.or_arg(p)

    def p_lt(self, p):
        """lt : LT math_expression math_expression"""
        self.node_builder.lt(p)

    def p_gt(self, p):
        """gt : GT math_expression math_expression"""
        self.node_builder.gt(p)

    def p_math_expression(self, p):
        """math_expression : inc
                            | dec
                            | INT_DECIMAL"""
        self.node_builder.math_expression(p)


if __name__ == '__main__':
    parser = TAParser()
    print("Enter filename: ", end="")
    filename = input()
    s = '/Users/MI/PycharmProjects/TARobot/Testing/test_interpreter_' + filename
    f = open(s, 'r')
    data = f.read()
    f.close()

    syntax_tree, func_table, hasErrors = parser.parse(data, debug=False)
    print(syntax_tree)

