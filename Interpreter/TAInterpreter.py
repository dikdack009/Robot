import copy
from Parser.TAParser import *
from Parser.TAParser import NodeType
from ErrorHandler import *
from TypeConverter import TypeConverter
from Variable import Variable
from collections import deque


# from Robot.JazzRobot import *


class VariableList:
    def __init__(self):
        self.pre = None
        self.variables = {}
        self.next = None


class TAInterpreter:
    def __init__(self):
        self.parser = TAParser()
        self.syntax_tree = None
        self.func_table = dict()
        self.declaration_table = [dict()]
        self.visibility_scope = 0
        self.recursion_depth = dict()
        self.variables = VariableList()

        self.robot = None

    def start(self, prog=None, robot=None):
        self.robot = robot
        self.syntax_tree, self.func_table, has_syntax_errors = self.parser.parse(prog)
        for key in self.func_table.keys():
            self.recursion_depth[key] = 0
        if not has_syntax_errors:
            self.handleCaseWithoutSyntaxErrors()

    def handleCaseWithoutSyntaxErrors(self):
        mainFuncKey = "main"
        if mainFuncKey in self.func_table.keys():
            start_node = self.func_table["main"].children["body"]
            self.handleNode(start_node)
            for d in self.declaration_table:
                for key in d.keys():
                    print(f"{key}: {d[key]}")
                print()
        else:
            ErrorHandler().raise_error(code=ErrorType.MissingProgramStartPoint.value)
            return

    def handleNode(self, node):
        if node is None:
            return "None Node"

        node_type = node.type
        match node_type:
            case NodeType.Program.value:
                self.handleNode(node.children)
            case NodeType.SentenceList.value:
                for child in node.children:
                    # print(child.type)
                    self.handleNode(child)
            case NodeType.Declaration.value:
                # declaration-node has field value which equals type-node, and this type-node has field value
                # which equals int-node or bool-node
                type = node.value.value
                children = node.children
                try:
                    self.declare(type, children)
                except ValueException:
                    print("[DEBUG]: Value Exception")
                    pass
                except UnexpectedTypeException:
                    print("[DEBUG]: Unexpected Type Exception")
                    pass
            case NodeType.Assignment.value:
                try:
                    return self.handle_assignment(node)
                except UndeclaredException:
                    ErrorHandler().raise_error(node=node, code=ErrorType.UndeclaredError.value)
            case NodeType.Expression.value:
                return self.handleNode(node.children)
            case NodeType.If.value:
                self.handle_if_else(node)
            case NodeType.While.value:
                self.handle_dowhile(node)

            case NodeType.CallProc.value:
                # node: type: func_call, value: name of calling function
                try:
                    self.handle_proc_cal(node)
                except RecursionException:
                    ErrorHandler().raise_error(node=node, code=ErrorType.RecursionError.value)
                except UndeclaredFunctionException:
                    ErrorHandler().raise_error(node=node, code=ErrorType.UndeclaredFunctionError.value)
                except Exception:
                    ErrorHandler().raise_error(code=ErrorType.UnexpectedError.value)
            case "robot":
                match node.value:
                    case "wall":
                        return Variable('int', self.back())
                    case "exit":
                        return Variable('bool', self.exit())
                    case "right":
                        return self.right()
                    case "left":
                        return self.left()
                    case "move":
                        exp = self.handleNode(node.children)
                        return Variable('bool', self.step(exp.value))

            case _:
                print("[DEBUG]: Errors in grammar and syntax tree building")

    def declare(self, decl_type, children):
        # Example: cint a = 5
        # where 5 is declaration_value
        declaration_name = children[0].value
        if len(children) == 2:
            declaration_value = children[1]
            expression = self.handleNode(declaration_value)
            self.add_to_declare_table(decl_type, declaration_name, expression)
        else:
            self.add_to_declare_table(decl_type, declaration_name, self.handleNode(None))

    def add_to_declare_table(self, decl_type, decl_name, value):
        expression = self.configure_declaration(decl_type, value)
        declaration_table_in_scope = self.declaration_table[self.visibility_scope]
        if decl_name not in declaration_table_in_scope.keys():
            declaration_table_in_scope[decl_name] = expression
        else:
            raise RedeclarationException

    def configure_declaration(self, type, value):
        if type == "cboolean" and isinstance(value.value, int):
            return Variable("cboolean", bool(value.value))
        elif type == "cint" and isinstance(value.value, bool):
            return Variable("cint", int(value.value))
        return self.configure_variable(type, value)

    def configure_variable(self, type, value):
        if type == "int" and value.type == "cint":
            return TypeConverter().convert_type(type, Variable("int", value.value))
        if type == "boolean" and value.type == "cboolean":
            return TypeConverter().convert_type(type, value.value)
        return TypeConverter().convert_type(type, value)

    def extract_variable_value(self, node):
        if node.value in self.declaration_table[self.visibility_scope].keys():
            return self.declaration_table[self.visibility_scope][node.value]
        else:
            raise UndeclaredException

    ###################################
    def handle_assignment(self, node):
        # met something like a := 5
        # a is decl_name
        decl_name = node.value.value
        if decl_name not in self.declaration_table[self.visibility_scope].keys():
            raise UndeclaredException
        try:
            var = self.declaration_table[self.visibility_scope][decl_name]
            new_value = node.children[0]
            new_value = self.handleNode(new_value)
            self.declaration_table[self.visibility_scope][decl_name] = Variable(var.type, int(new_value.value))
        except TypeException:
            ErrorHandler().raise_error(node=node, code=ErrorType.TypeError.value)
        except ConstantAssignmentException:
            ErrorHandler().raise_error(node=node, code=ErrorType.ConstantAssignmentError.value)

    ###################################


    def createNewEnv(self):
        current = VariableList()
        current.pre = self.variables
        self.variables.next = current
        self.variables = self.variables.next

    def expression(self, node):
        if node.type == 'variable':
            return self.get_variable(node)
        elif node.type == 'math expression':
            return self.math_expression(node)
        elif node.type == 'boolean':
            return Variable(node.data, 'boolean')
        elif node.type == 'call proc':
            return self.proc_call(node)
        elif node.type == 'Robot command':
            return self.handleNode(node)
        else:
            raise ErrorType.UnexpectedError

    def returnEnv(self):
        self.variables = self.variables.pre

    def handle_if_else(self, node):
        # if-node has children = [conditionChild, bodyChild] | [conditionChild, bodyChild, elseChild]
        condition = node.children[0]
        # condition = TypeConverter().convert_type("bool", condition).value
        expression = node.children[0]
        then_statement = node.children[1]
        if len(node.children) == 2:
            self.createNewEnv()
            expression = node.children[0]
            condition = self.expression(expression)
            condition = TypeConverter().convert_type('bool', condition).value
            if condition == 'true':
                self.handleNode(then_statement)
        else:
            else_statement = node.children[2]
            self.createNewEnv()
            condition = self.expression(expression)
            condition = TypeConverter().convert_type('bool', condition).value
            if condition == 'true':
                self.handleNode(then_statement)
            elif condition == 'false':
                self.handleNode(else_statement)
            self.returnEnv()

    def handle_dowhile(self, node):
        body = node.children[0]
        expression = node.children[1]
        self.createNewEnv()
        counter = 0
        condition = 'true'
        while condition == 'true':
            counter += 1
            self.handleNode(body)
            condition = self.expression(expression)
            condition = TypeConverter().convert_type('bool', condition).value
            if counter > 1000:
                raise RuntimeError()
        self.returnEnv()

    def back(self):
        return self.robot.back()

    def exit(self):
        result = self.robot.exit()
        if result:
            self.exit_found = True
        return result

    def right(self):
        return self.robot.right()

    def left(self):
        return self.robot.left()

    def step(self, expression):
        return self.robot.step(expression)


def create_robot(descriptor, window):
    pass


if __name__ == '__main__':
    interpreter = TAInterpreter()
    print("Enter filename: ", end="")
    filename = input()
    s = f'/Users/MI/PycharmProjects/TARobot/Testing/test_interpreter__{filename}.txt'
    #s = f'/Users/MI/PycharmProjects/TARobot/Testing/test_interpreter_exit_alg.txt'
    f = open(s, "r")
    program = f.read()
    f.close()
