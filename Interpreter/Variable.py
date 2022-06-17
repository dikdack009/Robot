class Variable:
    def __init__(self, type, value):
        self.type = type
        if value == "true":
            self.value = True
        elif value == "false":
            self.value = False
        else:
            self.value = value

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.type == other.type and self.value == other.value
        return NotImplemented

    def __repr__(self):
        return f"Type: {self.type}; Value: {self.value}"