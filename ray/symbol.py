
class Scope(object):
    def __init__(self, node, scope_type="module",
                 scope_name="global",parent=None):
        self.node = node
        self.type = scope_type
        self.name = scope_name
        self.scopes = {}
        self.symbols = {}
        self.parent = parent

    def __repr__(self):
            result = "{'Type':'%s', 'Name':'%s', 'Parent':'%s', 'Scopes':[%r], 'Symbols':[%r]}" % ( 
                self.type, self.name, 
                self.parent.name if self.parent else "None",
                self.scopes, self.symbols)
            return result.replace("'",'"').replace('[{}]','[]')


class Symbol(object):
    def __init__(self, node, scope, symbol_name, symbol_type):
        self.node = node
        self.scope = scope
        self.name = symbol_name
        self.type = symbol_type

    def __repr__(self):
            result ="{'Type':'%s', 'Name':'%s', 'Scope':'%s'}".replace("'",'"') % ( 
                self.type, self.name, self.scope.name)
            return result.replace("'",'"')

class SymbolLocation(object):
    def __init__(self, symbol, file, line, col):
        self.symbol = symbol
        self.file = file
        self.line = line
        self.col = col