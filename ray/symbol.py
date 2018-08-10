
class Scope(object):
    def __init__(self, node, scope_type="module",
                 scope_name="",parent=None):
        self.node = node
        self.type = scope_type
        self.name = scope_name
        self.scopes = {}
        self.symbols = {}
        self.parent = parent
        if parent:
            delimiter = '.' if parent.qualified_name else ''
            self.qualified_name = "%s%s%s" % (parent.qualified_name, delimiter, scope_name)
        else:
            self.qualified_name = scope_name

    def __repr__(self):
            result = "{'type':'%s', 'name':'%s', 'qualified_name':'%s'," \
                     " 'parent':'%s', 'scopes':[%r], 'symbols':[%r]}" % ( 
                self.type, self.name, self.qualified_name,
                self.parent.name if self.parent else "",
                self.scopes, self.symbols)
            return result.replace("'",'"').replace('[{}]','[]')


class Symbol(object):
    def __init__(self, node, scope, symbol_name, symbol_category):
        self.node = node
        self.scope = scope
        self.name = symbol_name
        self.category = symbol_category
        self.type_def = None
        parent = scope if symbol_category in ('var','paramater','args') else scope.parent
        if parent:
            delimiter = '.' if parent.qualified_name else ''
            self.qualified_name = "%s%s%s" % (parent.qualified_name, delimiter, symbol_name)
        else:
            self.qualified_name = symbol_name

    def __repr__(self):
            result ="{'category':'%s', 'name':'%s', 'qualified_name':'%s', 'scope':'%s'}".replace("'",'"') % ( 
                self.category, self.name, self.qualified_name, self.scope.name)
            return result.replace("'",'"')

class SymbolLocation(object):
    def __init__(self, symbol, file, line, col):
        self.symbol = symbol
        self.file = file
        self.line = line
        self.col = col