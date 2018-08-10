from collections import defaultdict
from functools import partial
from io import StringIO

from lark import Lark
from lark.lexer import Token

from symbol import Symbol, Scope ,SymbolLocation
from type_defs import Type_Def

class SymbolProcessor(object):
    

    def __init__(self):
        self.nodeVisitor = {
            "module_statement": self.visitModule,
            "class_define": self.visitClassDef,
            "class_declaration" : self.visitClassDecl,
            "extern_type": self.visitExternType,
            "extern_func": self.visitExternFunc,
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
            "comment": self.visitNoop,
            "emit_statement": self.visitNoop,
            "return_statement": self.visitReturn,
            "from_statement": self.visitFrom,
            "expression_statement": self.visitExpression,
            "call_expression": self.visitCall,
        }
        self.global_scope = Scope(None)
        self.scope = self.global_scope
        self.symbol_table = {}
        self.func_table = {}
        self.type_table = {}
        self.var_table = {}
        self.module_table = {}
        self.type_defs = {}
        self.defered_imports = {}
        self.defered_deps = {}
        self.depends_on = defaultdict(list)
    
    def processTree(self, tree):
        for node in tree.children:
            if not isinstance(node,Token):
                self.visitNode(node)
        self.registerSymbols(self.global_scope)
        for node, scope in self.defered_imports.items():
            self.scope = scope
            self.visitNode(node)
        for node, scope in self.defered_deps.items():
            self.scope = scope
            self.visitNode(node)


    def registerSymbols(self, scope):
        for sym in scope.symbols.values():
            self.registerSymbol(sym)
        for sub_scope in scope.scopes.values():
            self.registerSymbols(sub_scope)

    def registerSymbol(self, symbol):
        tables = {"function":self.func_table,
                  "paramater":self.var_table,
                  "var":self.var_table,
                  "type":self.type_table,
                  "module":self.module_table}
        self.symbol_table.setdefault(symbol.qualified_name, symbol)
        table = tables.get(symbol.category)
        if table is not None:
            table.setdefault(symbol.qualified_name, symbol)
        

    def visitNode(self, node):
        self.getVisitor(node)(node)

    def visitNoop(self, node):
        pass

    def visitRaw(self, node):
        pass
        # TODO handel assignments statement for depency tracking.
        # TODO for retrun value binding?

    def visitExpression(self, node):
        self.visitNode(node.children[0])

    def visitCall(self, node):
        raw = node.children
        symbol_name = raw[0].children[0].value
        #TODO handel argument dependices.
        #args = []
        scope = self.scope
        sym = self.lookupSymbol(scope, symbol_name)
        if sym is None:
            self.defered_deps[node]=self.scope
        else:
            parent_scope = self.scope.parent
            scope_name = self.scope.name
            parent = parent_scope.symbols[scope_name]
            self.depends_on[parent].append(sym)

    def lookupSymbol(self, scope, symbol_name):
        sym = None
        while  scope is not None:
            sym = scope.symbols.get(symbol_name)
            if sym:
                break
            else:
                scope = scope.parent
        return sym


    def visitFrom(self, node):
        pass

    def visitReturn(self, node):
        pass

    def visitCondition(self, tree):
        for node in tree.children:
            self.visitNode(node)
 
    def visitIf(self, node):
        name = "if_line_%s" % node.line
        scope_type = "if"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name, scope)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitElif(self, node):
        name = "elif_line_%s" % node.line
        scope_type = "elif"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name, scope)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitElse(self, node):
        name = "else_line_%s" % node.line
        scope_type = "else"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name, scope)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitWhile(self,node):
        name = "while_line_%s" % node.line
        scope_type = "while_loop"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name, scope)
        self.scope = scope
        self.processSubNodes(node.children[3])
        self.scope = scope.parent

    def processSubNodes(self, tree):
        for node in tree.children:
            if not isinstance(node,Token):
                self.visitNode(node)

    def visitVarDecl(self,node):
        raw = node.children[0]
        
        type_name = ""
        symbol_name = ""
        sym = None

        if raw.data == 'aggregate_declaration':
            type_name = "%s[%s]" % (raw.children[0].children[0].value,
                                    raw.children[2].children[0].children[0].value)
            symbol_name = raw.children[4].children[0].value
            sym = Symbol(node, self.scope, symbol_name, "var")
        else:
            type_name = raw.children[0].children[0].value
            symbol_name = raw.children[1].children[0].value
            sym = Symbol(node, self.scope, symbol_name, "var")
        
        self.scope.symbols.setdefault(symbol_name,sym)

    def visitVarDef(self,node):
        raw = node.children[0]

        type_name = ""
        symbol_name = ""
        sym = None

        if raw.data == 'aggregate_declaration':
            type_name = "%s[%s]" % (raw.children[0].children[0].value,
                                    raw.children[2].children[0].children[0].value)
            symbol_name = raw.children[4].children[0].value
            sym = Symbol(node, self.scope, symbol_name, "var")
        else:
            type_name = raw.children[0].children[0].value
            symbol_name = raw.children[1].children[0].value
            sym = Symbol(node, self.scope, symbol_name, "var")
        #note use typename to build type later.
        self.scope.symbols.setdefault(symbol_name, sym)

    def visitParams(self,node):
        raw = node.children
        if len(raw) < 3:
            return # note you should never get here if it parsed
        for param in range(0,len(raw),4):
            type_name = raw[param].children[0].value
            symbol_name = raw[param+2].children[0].value
            sym = Symbol(raw[param+2], self.scope, symbol_name, "paramater")
            self.scope.symbols.setdefault(symbol_name, sym)
            
    def visitModule(self,node):
        name = node.children[1].children[0].value
        scope_type = "module"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name, scope)
        sym = Symbol(node, scope, name, scope_type)
        self.scope.symbols.setdefault(name, sym)
        self.scope = scope
        self.processSubNodes(node.children[2])
        self.scope = scope.parent

    def visitClassDecl(self, node):
        name = node.children[0].children[0].value
        scope_type = "type_decl"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, scope, name, scope_type)
        type_def = Type_Def(node, name, sym.qualified_name, "scalar_type")
        self.type_defs.setdefault(sym.qualified_name, type_def)
        sym.type_def = type_def
        self.scope.symbols.setdefault(name, sym)

    def visitExternType(self, node):
        name = node.children[0].children[0].value
        scope_type = "extern_type"
        # TODO support external types with bodies.
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, scope, name, scope_type)
        type_def = Type_Def(node, name, sym.qualified_name, "scalar_type")
        self.type_defs.setdefault(sym.qualified_name, type_def)
        sym.type_def = type_def
        self.scope.symbols.setdefault(name, sym)

    def visitClassDef(self, node):
        name = node.children[0].children[0].value
        scope_type = "type"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name,scope)
        sym = Symbol(node, scope, name, scope_type)
        type_def = Type_Def(node, name, sym.qualified_name, "scalar_type")
        self.type_defs.setdefault(sym.qualified_name, type_def)
        sym.type_def = type_def
        self.scope.symbols.setdefault(name, sym)
        self.scope = scope
        self.processSubNodes(node.children[1])
        self.scope = scope.parent

    def visitOperatorDef(self,node):
        name = node.children[0].children[0].value
        scope_type = "operator"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)
        self.scope.scopes.setdefault(name, scope)
        sym = Symbol(node, scope, name, scope_type)
        self.scope.symbols.setdefault(name, sym)
        self.scope = scope
        self.processSubNodes(node.children[-1])
        self.scope = scope.parent

    def visitImport(self,node):
        name = node.children[1].children[0].value
        module = self.module_table.get(name)
        if(module):
            for sym in module.scope.symbols.values():
                self.scope.symbols.setdefault(sym.name, sym)
        else:
            self.defered_imports[node]=self.scope

    def visitFunctionDef(self,node):
        name = node.children[1].children[0].value
        scope_type = "function"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)

        self.scope.scopes.setdefault(name, scope)
        sym = Symbol(node, scope, name, scope_type)
        self.scope.symbols.setdefault(name, sym)
        self.scope = scope
        if len(node.children) >5 :
            self.visitParams(node.children[3]) # params
        self.processSubNodes(node.children[-1]) # body
        self.scope = scope.parent

    def visitExternFunc(self, node):
        name = node.children[1].children[0].value
        scope_type = "external_function"
        scope = Scope(node, scope_type=scope_type,
                       scope_name=name, parent=self.scope)

        self.scope.scopes.setdefault(name, scope)
        sym = Symbol(node, scope, name, scope_type)
        self.scope.symbols.setdefault(name, sym)
        self.scope = scope
        self.visitParams(node.children[3]) # params
        self.scope = scope.parent

    def getVisitor(self, node, default=visitRaw):
        name = ""
        if not isinstance(node, Token):
            name = node.data
        else:
            name = node.type
        return self.nodeVisitor.get(name, partial(default, self))
