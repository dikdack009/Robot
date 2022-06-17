from Parser.TAParser import *


def yellAboutError(errorInfo="Something got wrong!"):
    sys.stderr.write(errorInfo)


class ErrorType(enum.Enum):
    UnexpectedError = -1
    MissingProgramStartPoint = 1
    RedeclarationError = 2
    UndeclaredError = 3
    TypeError = 4
    MissingParameterError = 5
    RecursionError = 6
    ReturnSpecificationError = 7
    FunctionReturnAssignmentError = 8
    RedeclarationReturnSpecificationError = 9
    UndeclaredFunctionError = 10
    ConstantAssignmentError = 11
    RuntimeError = 12


class ErrorHandler:
    def __init__(self, node=None):
        if node is None:
            node = NodeOfST(node_type="placeholder",
                            value="placeholder",
                            children=[NodeOfST(node_type="placeholder", value="placeholder", children=[], lineno=-1)],
                            lineno=-1)
        self.node = node

    def raise_error(self, node=None, code=-1, type=""):
        if node is not None:
            if isinstance(node.children, dict):
                self.node = NodeOfST(node_type=node.type,
                                     value=node.value,
                                     children=[NodeOfST(node_type="placeholder", value="placeholder", children=[],
                                                        lineno=-1)],
                                     lineno=node.lineno)
            else:
                self.node = node

        errors_description = {
            -1: f"[ERROR]: Got unexpected error\n",
            1: f"[ERROR]: Missing 'main()' function in program!\n",
            2: f"[ERROR]: Name '{self.node.children[0].value}' of {type} declared at line {self.node.lineno} was used before\n",
            3: f"[ERROR]: Trying to use undeclared variable/constant/function at line {self.node.lineno}\n",
            4: f"[ERROR]: Type conflict occurred while assignment at line {self.node.lineno}\n",
            5: f"[ERROR]: Missing passing parameters in calling function with name '{self.node.value}' at line {self.node.lineno}\n",
            6: f"[ERROR]: Maximum recursion depth reached while calling function with name '{self.node.value}'\n",
            7: f"[ERROR]: Return specification not completed: declare needed variables in defined configuration",
            8: f"[ERROR]: Calling function '{self.node.value}' returns values, you should to assign them\n",
            9: f"[ERROR]: Function with name '{self.node.value}', which you trying to call at line {self.node.lineno}, has name conflicts in its declaration\n",
            10: f"[ERROR]: Function with '{self.node.value}' you trying to call at line {self.node.lineno} is not declared, check that it is spelled correctly\n",
            11: f"[ERROR]: Trying to assign new value to constant at line {self.node.lineno}\n",
            12: f"[ERROR]: Runtime Error {self.node.lineno}\n"

        }
        match code:
            case ErrorType.MissingProgramStartPoint.value:
                yellAboutError(errors_description[1])
            case ErrorType.RedeclarationError.value:
                yellAboutError(errors_description[2])
            case ErrorType.UndeclaredError.value:
                yellAboutError(errors_description[3])
            case ErrorType.TypeError.value:
                yellAboutError(errors_description[4])
            case ErrorType.MissingParameterError.value:
                yellAboutError(errors_description[5])
            case ErrorType.RecursionError.value:
                yellAboutError(errors_description[6])
            case ErrorType.ReturnSpecificationError.value:
                yellAboutError(errors_description[7])
            case ErrorType.FunctionReturnAssignmentError.value:
                yellAboutError(errors_description[8])
            case ErrorType.RedeclarationReturnSpecificationError.value:
                yellAboutError(errors_description[9])
            case ErrorType.UndeclaredFunctionError.value:
                yellAboutError(errors_description[10])
            case ErrorType.ConstantAssignmentError.value:
                yellAboutError(errors_description[11])
            case _:
                print("[DEBUG]: Got incorrect code for raising error")



class RedeclarationException(Exception):
    pass


class ValueException(Exception):
    pass


class UnexpectedTypeException(Exception):
    pass


class UndeclaredException(Exception):
    pass


class TypeException(Exception):
    pass


class MissingParameterException(Exception):
    pass


class RecursionException(Exception):
    pass


class ReturnSpecificationException(Exception):
    pass


class FunctionReturnAssignmentException(Exception):
    pass


class RedeclarationReturnSpecificationException(Exception):
    pass


class UndeclaredFunctionException(Exception):
    pass


class ConstantAssignmentException(Exception):
    pass


class MyRuntimeError(Exception):
    pass
