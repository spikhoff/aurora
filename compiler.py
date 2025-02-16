#!/usr/bin/env python3
import re
from enum import Enum, auto

# --- Token Types & Token Definition ---

class TokenType(Enum):
    IDENTIFIER = auto()
    KEYWORD = auto()
    SYMBOL = auto()
    NUMBER = auto()
    STRING = auto()
    EOF = auto()

KEYWORDS = {
    "actor", "supervisor", "func", "let", "var", "on", "spawn", "log", "restart", "message", "return"
}

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"

# --- Lexer Implementation ---

class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def next_char(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def advance(self):
        ch = self.source[self.position]
        self.position += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self):
        tokens = []
        while (ch := self.next_char()) is not None:
            # Skip whitespace
            if ch.isspace():
                self.advance()
                continue

            # Identifier or Keyword
            if ch.isalpha() or ch == "_":
                tokens.append(self.tokenize_identifier())
                continue

            # Number literal
            if ch.isdigit():
                tokens.append(self.tokenize_number())
                continue

            # String literal
            if (ch := self.next_char()) is not None and ch != '"':
                string_val += self.advance()
            if self.next_char() == '"':
                self.advance()  # skip closing quote
            return Token(TokenType.STRING, string_val, start_line, start_col)

    def tokenize_symbol(self):
        start_line, start_col = self.line, self.column
        ch = self.advance()
        # Handle multi-character symbols like "->"
        if ch == '-' and self.next_char() == '>':
            self.advance()  # consume '>'
            return Token(TokenType.SYMBOL, "->", start_line, start_col)
        return Token(TokenType.SYMBOL, ch, start_line, start_col)

# --- AST Node Definitions ---

class ASTNode:
    pass

class Actor(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body  # list of functions, variable definitions, or event handlers

    def __repr__(self):
        return f"Actor({self.name}, body={self.body})"

class Supervisor(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self):
        return f"Supervisor({self.name}, body={self.body})"

class Function(ASTNode):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body  # In a real compiler, this would be a list of statement nodes.

    def __repr__(self):
        return f"Function({self.name}, params={self.params}, return={self.return_type}, body={self.body})"

class EventHandler(ASTNode):
    def __init__(self, event, params, body):
        self.event = event
        self.params = params
        self.body = body

    def __repr__(self):
        return f"EventHandler({self.event}, params={self.params}, body={self.body})"

class Main(ASTNode):
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return f"Main(body={self.body})"

# --- Parser Implementation (Simplified) ---

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def consume(self, expected_type=None, expected_value=None):
        token = self.current()
        if expected_type and token.type != expected_type:
            raise Exception(f"Expected token type {expected_type} but got {token.type} at line {token.line}")
        if expected_value and token.value != expected_value:
            raise Exception(f"Expected token '{expected_value}' but got '{token.value}' at line {token.line}")
        self.position += 1
        return token

    def parse(self):
        nodes = []
        while self.current().type != TokenType.EOF:
            nodes.append(self.parse_declaration())
        return nodes

    def parse_declaration(self):
        token = self.current()
        if token.type == TokenType.KEYWORD:
            if token.value == "actor":
                return self.parse_actor()
            elif token.value == "supervisor":
                return self.parse_supervisor()
            elif token.value == "func":
                return self.parse_function()
            elif token.value == "main":
                return self.parse_main()
        raise Exception(f"Unexpected token {token}")

    def parse_actor(self):
        self.consume(TokenType.KEYWORD, "actor")
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "{")
        body = []
        while self.current().value != "}":
            if self.current().value == "func":
                body.append(self.parse_function())
            elif self.current().value == "on":
                body.append(self.parse_event_handler())
            else:
                # Skipping other declarations (like variable declarations) for brevity.
                self.consume()
        self.consume(TokenType.SYMBOL, "}")
        return Actor(name, body)

    def parse_supervisor(self):
        self.consume(TokenType.KEYWORD, "supervisor")
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "{")
        body = []
        while self.current().value != "}":
            if self.current().value == "func":
                body.append(self.parse_function())
            elif self.current().value == "on":
                body.append(self.parse_event_handler())
            else:
                self.consume()
        self.consume(TokenType.SYMBOL, "}")
        return Supervisor(name, body)

    def parse_function(self):
        self.consume(TokenType.KEYWORD, "func")
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "(")
        params = self.parse_parameters()
        self.consume(TokenType.SYMBOL, ")")
        self.consume(TokenType.SYMBOL, "->")
        return_type = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "{")
        body = []
        # Collect tokens until the matching "}".
        while self.current().value != "}":
            body.append(self.consume())
        self.consume(TokenType.SYMBOL, "}")
        return Function(name, params, return_type, body)

    def parse_main(self):
        self.consume(TokenType.KEYWORD, "func")
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "(")
        self.consume(TokenType.SYMBOL, ")")
        self.consume(TokenType.SYMBOL, "->")
        return_type = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "{")
        body = []
        while self.current().value != "}":
            if self.current().value == "let":
                body.append(self.parse_let())
            elif self.current().type == TokenType.IDENTIFIER and self.current().value == "supervisor":
                body.append(self.parse_supervisor_send())
            else:
                body.append(self.consume())
        self.consume(TokenType.SYMBOL, "}")
        return Main(body)

    def parse_let(self):
        self.consume(TokenType.KEYWORD, "let")
        var_name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "=")
        expr = self.consume()
        self.consume(TokenType.SYMBOL, ";")
        return f"let {var_name} = {expr.value};"

    def parse_supervisor_send(self):
        supervisor = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, ".")
        method = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "(")
        self.consume(TokenType.KEYWORD, "message")
        self.consume(TokenType.SYMBOL, ":")
        self.consume(TokenType.SYMBOL, "{")
        param = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.IDENTIFIER, "in")
        call = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, ".")
        method_call = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "(")
        self.consume(TokenType.SYMBOL, ")")
        self.consume(TokenType.SYMBOL, "}")
        self.consume(TokenType.SYMBOL, ")")
        self.consume(TokenType.SYMBOL, ";")
        return f"{supervisor}.{method}(message: {{ {param} in {call}.{method_call}() }});"

    def parse_event_handler(self):
        self.consume(TokenType.KEYWORD, "on")
        event = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.SYMBOL, "(")
        params = self.parse_parameters()
        self.consume(TokenType.SYMBOL, ")")
        self.consume(TokenType.SYMBOL, "{")
        body = []
        while self.current().value != "}":
            body.append(self.consume())
        self.consume(TokenType.SYMBOL, "}")
        return EventHandler(event, params, body)

    def parse_parameters(self):
        params = []
        while self.current().type != TokenType.SYMBOL or self.current().value != ")":
            params.append(self.consume())
            if self.current().type == TokenType.SYMBOL and self.current().value == ",":
                self.consume(TokenType.SYMBOL, ",")
        return params

# --- Code Generator (Simplified) ---

class CodeGenerator:
    def __init__(self, ast_nodes):
        self.ast_nodes = ast_nodes

    def generate(self):
        # In a real compiler, this step would convert the AST into target code.
        # Here, we’ll simply print a representation of the AST.
        for node in self.ast_nodes:
            print(node)

# --- Main Compiler Function ---

def compile_source(source):
    # Lexing
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print("Tokens:")
    for token in tokens:
        print(token)

    # Parsing
    parser = Parser(tokens)
    ast_nodes = parser.parse()
    print("\nAST:")
    for node in ast_nodes:
        print(node)

    # Code Generation (here, just printing the AST)
    print("\nGenerated Code:")
    codegen = CodeGenerator(ast_nodes)
    codegen.generate()

# --- Sample Aurora Source Code (from your example) ---

sample_source = '''
actor Counter {
    let count: Int = 0;

    func increment() -> Int {
        count += 1;
        return count;
    }

    on unknown(msg) {
        log("Unhandled message: " + msg);
    }
}

supervisor CounterSupervisor {
    var counter: Actor<Counter>;

    func start() -> Void {
        counter = spawn(Counter);
    }

    on error(actor, err) {
        log("Error in " + actor + ": " + err);
        restart(actor);
    }
}

func main() -> Void {
    let supervisor = spawn(CounterSupervisor);
    supervisor.send(message: { actor in actor.increment() });
}
'''

if __name__ == "__main__":
    compile_source(sample_source)
