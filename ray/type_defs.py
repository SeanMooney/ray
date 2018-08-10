class Type_Def(object):

    max_type_id = 0

    def __init__(self, node, type_name, qualified_name, symbol_category):
        self.node = node
        self.name = type_name
        self.qualified_name = qualified_name
        self.category = symbol_category
        self.type_id = Type_Def.max_type_id
        Type_Def.max_type_id += 1

