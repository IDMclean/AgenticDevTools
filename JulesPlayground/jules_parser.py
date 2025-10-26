# JulesPlayground/jules_parser.py

import re
from jules_ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if expected and token != expected:
                raise ValueError(f"Expected '{expected}' but got '{token}'")
            self.pos += 1
            return token
        if expected:
            raise ValueError(f"Expected '{expected}' but got end of input")
        return None

    def parse_atom(self):
        token = self.peek()
        if token.isdigit():
            self.consume()
            return Int(int(token))
        elif token.startswith('"'):
            self.consume()
            return String(token[1:-1])
        elif token and token not in ['let', 'in', 'fn', '(', ')', ',', '=>', ':', 'eval', 'AST', '!', 'letbang']:
            self.consume()
            return Var(token)
        elif token == '(':
            self.consume('(')
            expr = self.parse_expr()
            self.consume(')')
            return expr
        elif token == 'AST':
            self.consume('AST')
            self.consume('(')
            term = self.parse_expr()
            self.consume(')')
            return AST(term)
        elif token == '!':
            self.consume('!')
            return Promote(self.parse_atom())
        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_app(self):
        left = self.parse_atom()
        while self.peek() is not None and self.peek() not in [',', ')', 'in', '=>', ':']:
            left = App(left, self.parse_atom())
        return left

    def parse_expr(self):
        token = self.peek()
        if token == 'fn':
            self.consume('fn')
            var = self.consume()
            self.consume(':')
            type = self.parse_type()
            self.consume('=>')
            body = self.parse_expr()
            return Fun(var, type, body)
        if token == 'let':
            self.consume('let')
            var = self.consume()
            self.consume(':')
            type = self.parse_type()
            self.consume('=')
            e1 = self.parse_expr()
            self.consume('in')
            e2 = self.parse_expr()
            return App(Fun(var, type, e2), e1) # Desugar let
        if token == 'letbang':
            self.consume('letbang')
            self.consume('!')
            var = self.consume()
            self.consume('=')
            e1 = self.parse_expr()
            self.consume('in')
            e2 = self.parse_expr()
            return LetBang(var, e1, e2)
        return self.parse_app()

    def parse_type(self):
        token = self.peek()
        if token == 'Int':
            self.consume()
            return TInt()
        elif token == 'String':
            self.consume()
            return TString()
        elif token == 'Bool':
            self.consume()
            return TBool()
        elif token == 'AST':
            self.consume()
            return TAST()
        elif token == '!':
            self.consume('!')
            return TExponential(self.parse_type())
        elif token == '(':
            self.consume('(')
            t1 = self.parse_type()
            self.consume('->')
            t2 = self.parse_type()
            self.consume(')')
            return TFun(t1, t2)
        else:
            raise ValueError(f"Unknown type: {token}")

def parse(s: str) -> Term:
    s = s.strip()
    tokens = re.findall(r'\(|\)|,|=>|->|=|\b(?:let|in|fn|AST|Int|String|Bool|letbang)\b|:|\w+|"[^"]*"|!', s)
    tokens = [t for t in tokens if t and not t.isspace()]
    print(f"Tokens: {tokens}")
    parser = Parser(tokens)
    result = parser.parse_expr()
    if parser.peek() is not None:
        raise ValueError("Did not consume all tokens")
    return result
