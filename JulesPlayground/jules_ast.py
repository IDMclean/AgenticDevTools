# JulesPlayground/jules_ast.py

from typing import Union

# --- Types ---

class TInt:
    def __repr__(self):
        return "TInt"

class TString:
    def __repr__(self):
        return "TString"

class TBool:
    def __repr__(self):
        return "TBool"

class TFun:
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2
    def __repr__(self):
        return f"({self.t1} -> {self.t2})"

class TAST:
    def __repr__(self):
        return "TAST"

class TExponential:
    def __init__(self, t):
        self.t = t
    def __repr__(self):
        return f"!{self.t}"

Type = Union[TInt, TString, TBool, TFun, TAST, TExponential]

# --- Terms ---

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Var({self.name})"

class Int:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Int({self.value})"

class String:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"String({self.value})"

class App:
    def __init__(self, f, arg):
        self.f = f
        self.arg = arg
    def __repr__(self):
        return f"App({self.f}, {self.arg})"

class Fun:
    def __init__(self, var, type, body):
        self.var = var
        self.type = type
        self.body = body
    def __repr__(self):
        return f"Fun({self.var}: {self.type}, {self.body})"

class AST:
    def __init__(self, term):
        self.term = term
    def __repr__(self):
        return f"AST({self.term})"

class Promote:
    def __init__(self, e):
        self.e = e
    def __repr__(self):
        return f"Promote({self.e})"

class LetBang:
    def __init__(self, v, e1, e2):
        self.v = v
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return f"LetBang(!{self.v}, {self.e1}, {self.e2})"

Term = Union[Var, Int, String, App, Fun, AST, Promote, LetBang]
