#!/usr/bin/env python3
"""expression_parser — Recursive descent parser for math expressions with AST. Zero deps."""
import sys, math

class Token:
    def __init__(self, kind, value=None):
        self.kind, self.value = kind, value
    def __repr__(self): return f"Token({self.kind}, {self.value})"

def tokenize(expr):
    tokens, i = [], 0
    while i < len(expr):
        if expr[i].isspace(): i += 1
        elif expr[i] in "+-*/^()%":
            tokens.append(Token(expr[i])); i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(Token('NUM', float(expr[i:j]))); i = j
        elif expr[i].isalpha():
            j = i
            while j < len(expr) and expr[j].isalnum():
                j += 1
            tokens.append(Token('FUNC', expr[i:j])); i = j
        else:
            raise ValueError(f"Unexpected: {expr[i]}")
    return tokens

class Parser:
    FUNCS = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
             'sqrt': math.sqrt, 'abs': abs, 'log': math.log,
             'ln': math.log, 'exp': math.exp}
    CONSTS = {'pi': math.pi, 'e': math.e, 'tau': math.tau}

    def __init__(self, tokens):
        self.tokens, self.pos = tokens, 0

    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def eat(self, kind=None):
        t = self.peek()
        if kind and (not t or t.kind != kind):
            raise ValueError(f"Expected {kind}, got {t}")
        self.pos += 1
        return t

    def parse(self):
        result = self.expr()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected: {self.peek()}")
        return result

    def expr(self):
        result = self.term()
        while self.peek() and self.peek().kind in '+-':
            op = self.eat().kind
            r = self.term()
            result = result + r if op == '+' else result - r
        return result

    def term(self):
        result = self.power()
        while self.peek() and self.peek().kind in '*/%':
            op = self.eat().kind
            r = self.power()
            if op == '*': result *= r
            elif op == '/': result /= r
            else: result %= r
        return result

    def power(self):
        base = self.unary()
        if self.peek() and self.peek().kind == '^':
            self.eat()
            return base ** self.power()
        return base

    def unary(self):
        if self.peek() and self.peek().kind == '-':
            self.eat()
            return -self.unary()
        if self.peek() and self.peek().kind == '+':
            self.eat()
            return self.unary()
        return self.atom()

    def atom(self):
        t = self.peek()
        if t.kind == 'NUM':
            self.eat()
            return t.value
        if t.kind == 'FUNC':
            name = self.eat().value
            if name in self.CONSTS:
                return self.CONSTS[name]
            if name in self.FUNCS:
                self.eat('(')
                val = self.expr()
                self.eat(')')
                return self.FUNCS[name](val)
            raise ValueError(f"Unknown: {name}")
        if t.kind == '(':
            self.eat()
            val = self.expr()
            self.eat(')')
            return val
        raise ValueError(f"Unexpected: {t}")

def evaluate(expr):
    return Parser(tokenize(expr)).parse()

def main():
    exprs = ["2 + 3 * 4", "(2 + 3) * 4", "2 ^ 10", "sqrt(144) + sin(pi/2)",
             "-5 + 3", "e ^ 1", "100 % 7"]
    for expr in exprs:
        print(f"  {expr} = {evaluate(expr)}")
    if len(sys.argv) > 1:
        e = ' '.join(sys.argv[1:])
        print(f"\n  {e} = {evaluate(e)}")

if __name__ == "__main__":
    main()
