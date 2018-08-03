from functools import partial
from io import StringIO

from lark import Lark
from lark.lexer import Token

from symbol import Symbol, Scope ,SymbolLocation

class SymbolProcessor(object):
    

    def __init__(self):
        self.nodeVisitor = {
            "module_statement": self.visitModule,
            "class_define": self.visitClassDef,
            "operator_define": self.visitOperatorDef,
            "import_statement": self.visitImport,
            "function_define": self.visitFunctionDef,
            "paramaters": self.visitParams,
            "variable_define": self.visitVarDef,
            "variable_declaration": self.visitVarDecl,
            "while_statement": self.visitWhile,
            "condtional_statement": self.visitCondition,
            "if_statement": self.visitIf,
            "elif_statement": self.visitElif,
            "else_statement": self.visitElse,
        }
        self.global_scope = Scope(None)
        self.scope = self.global_scope
    
    def processTree(self, tree):
        for node in tree.children:
            self.visitNode(node)

    def visitNode(self, node):
        self.getVisitor(node)(node)

    def visitRaw(self, node):
        pass
        # TODO handel assignments statement for depency tracking.
        # TODO for retrun value binding?

    def visitCondition(self, tree):
        for node in tree.children:
            self.visitNode(node)
 
    def visitIf(self, node):
        name = "if_line_%s" % node.line
        scope_type = "if"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitElif(self, node):
        name = "elif_line_%s" % node.line
        scope_type = "elif"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitElse(self, node):
        name = "else_line_%s" % node.line
        scope_type = "else"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitWhile(self,node):
        name = "while_line_%s" % node.line
        scope_type = "while_loop"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        self.scope = scope
        self.processSubNodes(node.children[3])
        self.scope = scope.parent

    def processSubNodes(self, tree):
        for node in tree.children:
            self.visitNode(node)

    def visitVarDecl(self,node):
        return # handel aggregates
        raw = node.children[0]
        type_name = raw.children[0].children[0].value
        symbol_name = raw.children[1].children[0].value
        sym = Symbol(node, self.scope,symbol_name,"var")
        #note set subtype to type_name
        self.scope.symbols.setdefault(symbol_name,sym)

    def visitVarDef(self,node):
        return
        raw = node.children[0]
        type_name = raw.children[0].children[0].value
        symbol_name = raw.children[1].children[0].value
        # note add value?
        # note set subtype to typename
        sym = Symbol(node, self.scope,symbol_name,"var")
        self.scope.symbols.setdefault(symbol_name,sym)

    def visitParams(self,node):
        raw = node.children
        if len(raw) < 3:
            return # note you should never get here if it parsed
        for param in range(0,len(raw),4):
            type_name = raw[param].children[0].value
            symbol_name = raw[param+2].children[0].value
            sym = Symbol(raw[param+2], self.scope,symbol_name,"paramater")
            self.scope.symbols.setdefault(symbol_name,sym)
            
    def visitModule(self,node):
        name = node.children[1].children[0].value
        scope_type = "module"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, self.scope,name,scope_type)
        self.scope.symbols.setdefault(name,sym)
        self.scope = scope
        self.processSubNodes(node.children[2])
        self.scope = scope.parent

    def visitClassDef(self,node):
        name = node.children[0].children[0].value
        scope_type = "type"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, self.scope,name,scope_type)
        self.scope.symbols.setdefault(name,sym)
        self.scope = scope
        self.processSubNodes(node.children[1])
        self.scope = scope.parent

    def visitOperatorDef(self,node):
        name = node.children[0].children[0].value
        scope_type = "operator"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, self.scope,name,scope_type)
        self.scope.symbols.setdefault(name,sym)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitImport(self,node):
        name = node.children[1].children[0].value
        symbol_type = "module"
        sym = Symbol(node, self.scope,name,symbol_type)
        self.scope.symbols.setdefault(name,sym)

    def visitFunctionDef(self,node):
        name = node.children[1].children[0].value
        scope_type = "function"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)

        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, self.scope,name,scope_type)
        self.scope.symbols.setdefault(name,sym)
        self.scope = scope
        self.visitParams(node.children[3]) # params
        self.processSubNodes(node.children[-1]) # body
        self.scope = scope.parent

    def getVisitor(self, node, default=visitRaw):
        name = ""
        if not isinstance(node, Token):
            name = node.data
        else:
            name = node.type
        return self.nodeVisitor.get(name, partial(default, self))
