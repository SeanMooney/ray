from collections import defaultdict
from functools import partial
from io import StringIO

from lark import Lark
from lark.lexer import Token

import ray_ast as rast

class ASTProcessor(object):

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
            "comment": self.visitComment,
            "emit_statement": self.visitEmit,
            "return_statement": self.visitReturn,
            "from_statement": self.visitFrom,
            "expression_statement": self.visitExpression,
            "call_expression": self.visitCall,
        }
        self.global_scope = rast.Module("") 
        self.scope = self.global_scope
        self.module_table = {}
        self.type_table = {}
        
    def lookupVisableTypeDef(self, name, scope, recurse=False):
        current_scope = scope
        while current_scope:
            typeDef = current_scope.type_defs.get(name) if isinstance(current_scope, rast.Module) else None
            if typeDef:
                if isinstance(typeDef, rast.ExternTypeStatement) or isinstance(typeDef, rast.ExternFuncStatement):
                    typeDef = typeDef.type_def
                return typeDef
            elif recurse:
                current_scope = current_scope.parent
            else:
                return None # dont allow parent lookup for now.
        else:
            return None

    
    def processTree(self, tree):
        for node in tree.children:
            if not isinstance(node,Token):
                self.visitNode(node)
        
    def processSubNodes(self, tree):
        for node in tree.children:
            if not isinstance(node,Token):
                self.visitNode(node)

    def visitRaw(self, node):
        pass
        # TODO handel assignments statement for depency tracking.
        # TODO for retrun value binding?

    def getVisitor(self, node, default=visitRaw):
        name = ""
        if not isinstance(node, Token):
            name = node.data
        else:
            name = node.type
        visitor = self.nodeVisitor.get(name, partial(default, self))
        if visitor is default:
            print("node not supported", node)
        return visitor

    def visitNode(self, node):
        self.getVisitor(node)(node)

    def visitEmit(self, node):
        raw = node.children
        lang = raw[1].children[0].value
        block = raw[3].children[0].value[3:-3]
        statement = rast.EmitStatement(lang,block)
        self.scope.statements.append(statement)

    def visitNoop(self, node):
        pass

    def visitComment(self, node):
        raw = node.children
        text = raw[0].value
        statement = rast.Comment(text)
        self.scope.statements.append(statement)

    def visitExpression(self, node):
        self.visitNode(node.children[0])

    def visitCall(self, node):
        pass

    def visitFrom(self, node):
        raw = node.children
        module_name = raw[1].children[0].value
        module = self.module_table.get(module_name)
        assert(module is not None)
        if( isinstance(raw[3], Token) and raw[3].value == "*"):
            type_defs = self.scope.type_defs if isinstance(self.scope, rast.Module) else self.scope.parent.type_defs
            for symbol_name , symbol in module.type_defs.items():
                alias=symbol_name
                if alias not in type_defs:
                    statement = rast.FromStatement(module, symbol, alias=alias)
                    self.scope.statements.append(statement)
                    sym = type_defs.setdefault(alias, symbol)
                    assert(sym is symbol)
        else:
            symbol_name = raw[3].children[0].value
            alias = raw[5].children[0].value if len(raw) == 7 else symbol_name
            type_defs = self.scope.type_defs if isinstance(self.scope, rast.Module) else self.scope.parent.type_defs
            if alias not in type_defs:
                delim = "." if  symbol_name[0].isupper() else ":"
                qualifed_sym = "{}{}{}".format(module_name, delim, symbol_name)
                symbol = self.type_table.get(qualifed_sym)
                assert(symbol is not None)
                statement = rast.FromStatement(module, symbol, alias=alias)
                self.scope.statements.append(statement)
                sym = type_defs.setdefault(alias, symbol)
                assert(sym is symbol)

    def visitImport(self,node):
        raw = node.children
        module_name = raw[1].children[0].value
        alias = raw[3].children[0].value if len(raw) == 5 else module_name
        type_defs = self.scope.type_defs if isinstance(self.scope, rast.Module) else self.scope.parent.type_defs
        if alias not in type_defs:
            module = self.module_table.get(module_name)
            assert(module is not None)
            statement = rast.ImportStatement(module, alias=alias)
            self.scope.statements.append(statement)
            mod = type_defs.setdefault(alias, module)
            assert(mod is module)

    def visitReturn(self, node):
        pass

    def visitCondition(self, tree):
        pass

    def visitIf(self, node):
        pass

    def visitElif(self, node):
        pass

    def visitElse(self, node):
        pass

    def visitWhile(self, node):
        pass

    def visitVarDecl(self, node):
        sub_node = node.children[0]
        raw = sub_node.children
        sub_node_type = sub_node.data
        type_def = None
        name = ""
        parent = self.scope
        if sub_node_type == "aggregate_declaration":
            sub_node_len  = len(raw)
            typename = raw[0].children[0].value
            size = None if sub_node_len != 6 else raw[2].children[0].children[0].value
            scalar_type_def = self.lookupVisableTypeDef(typename, parent)
            assert(scalar_type_def is not None)
            scalar_parent = scalar_type_def.parent
            name = "{}[{}]".format(typename, size or "")
            qualifed_name = name if parent is None or scalar_parent.qualifed_name == "" else "%s%s%s" % (
                scalar_parent.qualifed_name, ".", name)
            type_def = self.lookupVisableTypeDef(name, scalar_parent)
            if type_def is None:
                type_def = rast.Aggregate(name, scalar_parent, size)
                type_def = parent.type_defs.setdefault(name, type_def)
                self.type_table.setdefault(qualifed_name, type_def)
        var = rast.LVal(node, name, type_def, constant=False)
        statement = rast.DeclStatement(var)
        parent.statements.append(statement)


    def visitVarDef(self, node):
        pass

    def visitParams(self, node):
        pass
            
    def visitModule(self, node):
        raw = node.children
        name = raw[1].children[0].value
        block = raw[2]
        parent = self.scope
        module = parent.scopes.setdefault(name, rast.Module(name,parent))
        self.module_table.setdefault(module.qualifed_name, module)
        parent.statements.append(rast.ModuleStatement(module))
        self.scope = module
        self.processSubNodes(block)
        self.scope = parent

    def visitClassDecl(self, node):
        pass

    def visitExternType(self, node):
        raw = node.children
        name = raw[0].children[0].value
        parent = self.scope
        statement = rast.ExternTypeStatement(name, parent)
        type_def = parent.type_defs.setdefault(name, statement.type_def)
        assert(type_def is statement.type_def)
        self.type_table.setdefault(type_def.qualifed_name, statement.type_def)
        parent.statements.append(statement)
        # Incomplete: this does not handel recursing into
        # external types with vars or functions.
    
    def visitExternFunc(self, node):
        statements = []
        raw = node.children
        parent = self.scope
        type_defs = parent.type_defs if isinstance(parent, rast.Module) else parent.parent.type_defs
        return_type_name = raw[0].children[0].value
        return_type = type_defs.get(return_type_name)
        if return_type is None:
            statement = rast.ExternTypeStatement(return_type_name, parent)
            return_type = type_defs.setdefault(return_type_name,
                statement.type_def)
            assert(return_type is statement.type_def)
            self.type_table.setdefault(return_type.qualifed_name,
                statement.type_def)
            statements.append(statement)    
        name = raw[1].children[0].value
        raw_params = raw[3].children
        params = []
        for index in range(0, len(raw_params), 4):
            typename = raw_params[index].children[0].value
            param_name = raw_params[index+2].children[0].value
            type_def = self.lookupVisableTypeDef(typename, parent)
            if type_def is None:
                statement = rast.ExternTypeStatement(typename,parent)
                type_def = type_defs.setdefault(typename,
                    statement.type_def)
                assert(type_def == statement.type_def)
                self.type_table.setdefault(type_def.qualifed_name,
                    statement.type_def)
                statements.append(statement)
            param = rast.Paramater(type_def, param_name)
            params.append(param)
        statement = rast.ExternFuncStatement(name, parent,
            return_type, params)
        type_def = type_defs.setdefault(name,
            statement.type_def)
        assert(type_def == statement.type_def)
        self.type_table.setdefault(type_def.qualifed_name,
                    statement.type_def)
        statements.append(statement)
        for s in statements:
            parent.statements.append(s)

    def visitClassDef(self, node):
        statements = []
        raw = node.children
        parent = self.scope
        name = raw[0].children[0].value
        type_def = self.lookupVisableTypeDef(name, parent)
        if type_def is None:
            statement = rast.StructStatement(name, parent)
            type_def = parent.type_defs.setdefault(name,
                statement.type_def)
            assert(type_def == statement.type_def)
            self.type_table.setdefault(type_def.qualifed_name,
                    statement.type_def)
            statements.append(statement)
        else:
            type_def.external = False
        block = raw[1]
        self.scope = type_def
        self.processSubNodes(block)
        self.scope = parent
        for s in statements:
            parent.statements.append(s)

    def visitOperatorDef(self,node):
        pass
        # for now do not support operator overloading
        
    def visitFunctionDef(self,node):
        statements = []
        raw = node.children
        parent = self.scope
        type_defs = parent.type_defs if isinstance(parent, rast.Module) else parent.parent.type_defs
        return_type_name = raw[0].children[0].value
        return_type = type_defs.get(return_type_name)
        if return_type is None:
            statement = rast.StructStatement(return_type_name, parent)
            return_type = type_defs.setdefault(return_type_name,
                statement.type_def)
            assert(return_type is statement.type_def)
            self.type_table.setdefault(return_type.qualifed_name,
                    statement.type_def)
            statements.append(statement)    
        name = raw[1].children[0].value
        raw_params = raw[3].children if not isinstance(raw[3],Token) else []
        params = []
        for index in range(0, len(raw_params), 4):
            typename = raw_params[index].children[0].value
            param_name = raw_params[index+2].children[0].value
            type_def = self.lookupVisableTypeDef(typename, parent)
            if type_def is None:
                statement = rast.StructStatement(typename,parent)
                type_def = type_defs.setdefault(typename,
                    statement.type_def)
                assert(type_def == statement.type_def)
                self.type_table.setdefault(type_def.qualifed_name,
                    statement.type_def)
                statements.append(statement)
            param = rast.Paramater(type_def, param_name)
            params.append(param)
        statement = rast.FuncStatement(name, parent,
            return_type, params)
        type_def = type_defs.setdefault(name,
            statement.type_def)
        assert(type_def == statement.type_def)
        self.type_table.setdefault(type_def.qualifed_name,
                    statement.type_def)
        statements.append(statement)
        for s in statements:
            parent.statements.append(s)


