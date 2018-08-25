class Field(object):
    def __init__(self, type_def, name, parent, value=None, qualifiers=[]):
        self.type_def = type_def
        self.name = name
        self.value = value
        self.qualifiers = qualifiers
        self.parent = parent
        self.qualifed_name = name if parent is None else "%s%s%s" % (
            parent.name,":",name)

class Scope(object):
    def __init__(self, name="", parent=None, seperator="."):
        self.name = name
        self.parent = parent
        self.seperator = seperator
        self.qualifed_name = name if parent is None else "%s%s%s" % (
            parent.name,seperator,name)

class Module(Scope):
    def __init__(self, name , parent = None):
        super().__init__(name, parent, '.')
        self.type_defs = {}
        self.statements = []
        self.scopes = {}

class Block(Scope):
    ident = 0
    def __init__(self, parent):
        super().__init__("block%s" % Block.ident, parent, '-')
        Block.ident+=1
        self.type_defs = {}
        self.statements = []
        self.scopes = {}

class TypeDef(Scope):
    max_type_id = 0
    def __init__(self, name, parent, seperator="."):
        super().__init__(name, parent, seperator)
        self.type_id = TypeDef.max_type_id
        TypeDef.max_type_id+=1

class Union(TypeDef):
    def __init__(self, name, parent,fields={},active=None):
        super().__init__(name, parent,':')
        self.fields = fields

class Variant(TypeDef):
    def __init__(self, name, parent,fields={},active=None):
        super().__init__(name, parent,':')
        self.fields = fields
        self.active = active 

class Enum(TypeDef):
    def __init__(self, name, parent, values={}, value=None):
        super().__init__(name, parent, ':')
        self.values = values
        self.value = value

class Lamda(TypeDef):
    def __init__(self, name, parent):
        super().__init__(name, parent, '&')
        self.captures = {}
        self.params = {}
        self.returns = {}
        self.statements = []

class Func(TypeDef):
    def __init__(self, name, parent):
        super().__init__(name, parent, ':')
        self.params = {}
        self.returns = {}
        self.statements = []

class Struct(TypeDef):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.fields = {}
        self.functions = {}

class Protocol(TypeDef):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.functions = {}

class Mixins(TypeDef):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.functions = {}

class Statement(object):
    pass

class Comment(Statement):
    def __init__(self, text):
        self.text = text

class AssignmentStatement(Statement):
    def __init__(self, lval, op, rval):
        super().__init__()
        self.lval = lval
        self.op = op
        self.rval = rval

class ExpressionStatement(Statement):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression

class DefineStatement(Statement):
    def __init__(self, field):
        super().__init__()
        self.field = field

class DeclStatement(Statement):
    def __init__(self, field):
        super().__init__()
        self.field = field

class ReturnStatement(Statement):
    def __init__(self, rval):
        super().__init__()
        self.rval = rval

class IterationStatement(Statement):
    pass

class ForStatement(IterationStatement):
    def __init__(self, block, predicate, params=None, continuation=None):
        super().__init__()
        self.block = block
        self.predicate = predicate
        self.params = params
        self.continuation = continuation

class WhileStatement(IterationStatement):
    def __init__(self, block, predicate):
        super().__init__()
        self.block = block
        self.predicate = predicate

class IfStatement(Statement):
    def __init__(self, block, predicate):
        super().__init__()
        self.block = block
        self.predicate = predicate

class ElifStatement(Statement):
    def __init__(self, block, predicate):
        super().__init__()
        self.block = block
        self.predicate = predicate

class ElseStatement(Statement):
    def __init__(self, block):
        super().__init__()
        self.block = block

class ConditionStatement(Statement):
    def __init__(self, if_obj, elifs=[], else_obj=None):
        super().__init__()
        self.if_obj = if_obj
        self.elifs = elifs
        self.else_obj=else_obj

class ImportStatement(Statement):
    def __init__(self, module, alias=None):
        self.module=module
        self.alias = alias

class FromStatement(Statement):
    def __init__(self, module, symbol, alias=None):
        self.module=module
        self.symbol = symbol
        self.alias = alias

class UsingStatement(Statement):
    def __init__(self, symbol, alias=None):
        self.symbol = symbol
        self.alias = alias

class WithStatement(Statement):
    def __init__(self, expression, block, alias=None):
        self.expression = expression
        self.block = block
        self.alias = alias

class CompilerStatement(Statement):
    pass


class EmitStatement(CompilerStatement):
    def __init__(self, language, block):
        super().__init__()
        self.language = language
        self.block = block

class ExternStatement(CompilerStatement):
    pass

class ExternTypeStatement(ExternStatement):
    def __init__(self, name, childern=[]):
        super().__init__()
        self.name = name
        self.childern = childern

class ExternFuncStatement(ExternStatement):
    def __init__(self, name, return_type, params=[]):
        super().__init__()
        self.name = name
        self.return_type = return_type
        self.params = params

class ExternVarStatement(ExternStatement):
    def __init__(self, type_def, name):
        super().__init__()
        self.type_def = type_def
        self.name = name

class ExternModuleStatement(ExternStatement):
    def __init__(self, name, childern=[]):
        super().__init__()
        self.name = name
        self.childern = childern

class RVal(object):
    def __init__(self, node):
        self.node = node

class Expression(RVal):
    def __init__(self, node, constant):
        super().__init__(node)
        self.constant = constant

class UniaryExpression(Expression):
    def __init__(self, node, constant, op, val):
        super().__init__(node, constant)
        self.op = op
        self.val = val

class PrefixExpression(UniaryExpression):
    def __init__(self, node, constant, op, val):
        super().__init__(node, constant, op, val)


class PostfixExpression(UniaryExpression):
    def __init__(self, node, constant, op, val):
        super().__init__(node, constant, op, val)

class BinExpression(Expression):
    def __init__(self, node, constant, op, lhs, rhs):
        super().__init__(node, constant)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

class CallExpression(Expression):
    def __init__(self, node, constant, name, args):
        super().__init__(node, constant)
        self.name = name
        self.args = args

class LiteralVal(RVal):
    constant = True
    pass

class NumberLiteral(LiteralVal):
    pass

class DecLiteral(NumberLiteral):
    pass

class HexLiteral(NumberLiteral):
    pass

class OctLiteral(NumberLiteral):
    pass

class BinLiteral(NumberLiteral):
    pass

class FloatLiteral(NumberLiteral):
    pass

class FixedPointLiteral(NumberLiteral):
    pass

class StringLiteral(LiteralVal):
    pass

class RawStringLiteral(StringLiteral):
    pass

class BooleanLiteral(LiteralVal):
    pass

class RuntimeVal(RVal):
    constant = False
    pass

class RuntimeVar(RVal):
    constant = False
    pass

class LVal(object):
    def __init__(self, node, name, type_def, constant):
        self.node = node
        self.name = name
        self.type = type_def
        self.constant = constant

