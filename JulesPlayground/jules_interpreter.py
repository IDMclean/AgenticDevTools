# JulesPlayground/jules_interpreter.py

from jules_ast import *

class TypeCheckError(Exception):
    pass

class TypeChecker:
    def __init__(self):
        self.unrestricted_context = {}
        self.linear_context = {}

    def type_check(self, term: Term) -> Type:
        if isinstance(term, Int):
            return TInt()
        elif isinstance(term, String):
            return TString()
        elif isinstance(term, Var):
            if term.name in self.linear_context:
                return self.linear_context.pop(term.name)
            elif term.name in self.unrestricted_context:
                return self.unrestricted_context[term.name]
            else:
                raise TypeCheckError(f"Variable '{term.name}' not found.")
        elif isinstance(term, Fun):
            if isinstance(term.type, TExponential):
                self.unrestricted_context[term.var] = term.type.t
            else:
                self.linear_context[term.var] = term.type
            body_type = self.type_check(term.body)
            return TFun(term.type, body_type)
        elif isinstance(term, App):
            fun_type = self.type_check(term.f)
            arg_type = self.type_check(term.arg)
            if not isinstance(fun_type, TFun):
                raise TypeCheckError("Cannot apply a non-function type.")
            if fun_type.t1 != arg_type:
                raise TypeCheckError("Type mismatch in application.")
            return fun_type.t2
        elif isinstance(term, Promote):
            original_linear_context = self.linear_context
            self.linear_context = {}
            t = self.type_check(term.e)
            if self.linear_context:
                raise TypeCheckError("Cannot promote with used linear variables.")
            self.linear_context = original_linear_context
            return TExponential(t)
        elif isinstance(term, LetBang):
            e1_type = self.type_check(term.e1)
            if not isinstance(e1_type, TExponential):
                raise TypeCheckError("Expected exponential type in let!.")
            self.unrestricted_context[term.v] = e1_type.t
            return self.type_check(term.e2)
        elif isinstance(term, AST):
            return TAST()
        else:
            raise NotImplementedError(f"Type checking not implemented for {type(term).__name__}")

class InterpError(Exception):
    pass

class Closure:
    def __init__(self, fun, env):
        self.fun = fun
        self.env = env

class Primitive:
    def __init__(self, fun, type):
        self.fun = fun
        self.type = type

def interpret(term: Term, env: dict = None, recursion_depth=0) -> Term:
    if env is None:
        env = {}

    if recursion_depth > 100:
        raise InterpError("Recursion limit exceeded")

    # Type check before interpreting
    checker = TypeChecker()
    checker.unrestricted_context = {k: v.type for k, v in env.items() if isinstance(v, Primitive)}
    checked_type = checker.type_check(term)
    if checker.linear_context:
        raise TypeCheckError("Unused linear variables.")

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
    elif isinstance(term, Promote):
        return interpret(term.e, env, recursion_depth + 1)
    elif isinstance(term, LetBang):
        val = interpret(term.e1, env, recursion_depth + 1)
        new_env = env.copy()
        new_env[term.v] = val
        return interpret(term.e2, new_env, recursion_depth + 1)
    elif isinstance(term, AST):
        return term
    else:
        raise NotImplementedError(f"Interpretation not implemented for {type(term).__name__}")

def get_default_env():
    return {
        "eval": Primitive(lambda t: interpret(t.term, get_default_env()), TFun(TAST(), TAST())),
        "print": Primitive(lambda t: print(t.value), TFun(TString(), TString())),
    }
