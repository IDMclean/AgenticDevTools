# JulesPlayground/jules_interpreter.py

from jules_ast import *

class InterpError(Exception):
    pass

class Closure:
    def __init__(self, fun, env):
        self.fun = fun
        self.env = env

class Primitive:
    def __init__(self, fun):
        self.fun = fun

def interpret(term: Term, env: dict = None, recursion_depth=0) -> Term:
    if env is None:
        env = {}

    if recursion_depth > 100:
        raise InterpError("Recursion limit exceeded")

    if isinstance(term, (Int, String)):
        return term
    elif isinstance(term, Var):
        if term.name in env:
            return env[term.name]
        else:
            raise InterpError(f"Variable '{term.name}' not found.")
    elif isinstance(term, Fun):
        return Closure(term, env)
    elif isinstance(term, App):
        fun_val = interpret(term.f, env, recursion_depth + 1)
        arg_val = interpret(term.arg, env, recursion_depth + 1)
        if isinstance(fun_val, Closure):
            new_env = fun_val.env.copy()
            new_env[fun_val.fun.var] = arg_val
            return interpret(fun_val.fun.body, new_env, recursion_depth + 1)
        elif isinstance(fun_val, Primitive):
            return fun_val.fun(arg_val)
        else:
            raise InterpError("Cannot apply a non-function value.")
    elif isinstance(term, AST):
        return term
    else:
        raise NotImplementedError(f"Interpretation not implemented for {type(term).__name__}")

def get_default_env():
    return {
        "eval": Primitive(lambda t: interpret(t.term, get_default_env()))
    }
