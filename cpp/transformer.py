import sys
import decimal
from functools import partial

from lark.lexer import Token

class RayToCpp(object):

    def __init__(self, *args, **kwargs):
        self.targetLang = "cpp"
        self.nodeDecoders = {
            "literal_value": self.decodeLiteral,
            "runtime_value": self.decodeRuntimeVal,
            "variable_declaration": self.decodeVarDeclare,
            "scalar_declaration": self.decodeScalareDeclare,
            "variable_define": self.decodeVarDef,
            "scalar_define": self.decodeScalarDef,
            "aggregate_define": self.decodeAggregateDef,
            "aggregate_declaration": self.decodeAggregateDeclare,
            "class_define": self.decodeClassDef,
            "function_define": self.decodeFunctionDef,
            "operator_define": self.decodeOperator,
            "construct_expression": self.decodeConstruct,
            'prefix_expression': self.decodePrefix,
            'postfix_expression': self.decodePostfix,
            "subscript": self.decodeSubscript,
            "call_expression": self.decodeCall,
            "bin_expression": self.decodeBinExpression,
            "compiler_statement": self.decodeCompilerStatement,
            "assignment_statement": self.decodeAssignment,
            "module_statement": self.decodeModule,
            "import_statement": self.decodeImport,
            "from_statement": self.decodeFrom,
            "block_statement": self.decodeBlock,
            "block": self.decodeBlock,
            "escaped_block": self.decodeEscapedBlock,
            "return_statement": self.decodeReturn,
            "expression_statement": self.decodeExpression,
            "while_statement": self.decodeWhile,
            "if_statement": self.decodeIf,
            "elif_statement": self.decodeElif,
            "else_statement": self.decodeElse,
            "condtional_statement": self.decodeCondtional,
            "name": self.decodeName,
            "constant_name": self.decodeConstant,
            "scalar_type_name": self.decodeScalarTypeName,
            "aggregate_type_name": self.decodeAggregateTypeName,
            "pointer_type_name": self.decodePointerTypeName,
            "comment": self.decodeComment,
            "number": self.decodeNumber,
            "token": self.decodeToken,
            "string": self.decodeString,
            "DEC_NUMBER": self.decodeDecNumber,
            "OCT_NUMBER": self.decodeOctNumber,
            "BIN_NUMBER": self.decodeBinNumber,
            "HEX_NUMBER": self.decodeHexNumber,
            "FLOAT_NUMBER": self.decodeFloat,
            "FIXED_POINT_NUMBER": self.decodeFixed
        }
        self.included_files = []

    def processTree(self, tree, out=sys.stdout):
        for node in tree.children:
            self.processNode(node, out)
        result = self.included_files
        self.included_files = []
        return  result

    def processNode(self, node, out=sys.stdout):
        print(self.consume(self.getDecoder(node)(node)),file=out)

    def decodeCompilerStatement(self, node):
        raw = node.children
        if raw[1].children[0].value == self.targetLang:
            sub_node = raw[3]
            current = self.getDecoder(sub_node)(sub_node)
            data = []
            data += self.consume(current)
            data += "\n"
            yield "".join(data[:-1])
        else:
            yield ""

    def decodeEscapedBlock(self,node):
        yield node.children[0].value[3:-3]

    def decodeSubscript(self,node):
        raw = node.children[1]
        yield "[%s]" % self.consume(self.getDecoder(raw)(raw))

    def decodePostfix(self,node):
        raw = node.children
        data = []
        for sub_node in raw:
            current = self.getDecoder(sub_node)(sub_node)
            data += self.consume(current)
        yield "".join(data)

    def decodePrefix(self,node):
        raw = node.children
        data = []
        for sub_node in raw:
            current = self.getDecoder(sub_node)(sub_node)
            data += self.consume(current)
        yield "".join(data)

    def decodeBlock(self, node):
        raw = node.children
        data = []
        for sub_node in raw:
            current = self.getDecoder(sub_node)(sub_node)
            data += self.consume(current)
            data += "\n"
        yield "".join(data[:-1])

    def decodeCondtional(self, node, out=sys.stdout):
        raw = node.children
        data = []
        for sub_node in raw:
            current = self.getDecoder(sub_node)(sub_node)
            data += self.consume(current)
            data += "\n"
        yield "".join(data[:-1])

    def decodeIf(self, node):
        raw = node.children
        cpp = "if(%(condition)s)%(body)s"
        condition = self.consume(self.getDecoder(raw[1])(raw[1]))
        body = self.consume(self.getDecoder(raw[3])(raw[3]))
        yield cpp % {"condition": condition, "body": body}


    def decodeElif(self, node):
        raw = node.children
        cpp = "else if(%(condition)s)%(body)s"
        condition = self.consume(self.getDecoder(raw[1])(raw[1]))
        body = self.consume(self.getDecoder(raw[3])(raw[3]))
        yield cpp % {"condition": condition, "body": body}

    def decodeElse(self, node):
        raw = node.children
        cpp = "else %(body)s"
        body = self.consume(self.getDecoder(raw[0])(raw[0]))
        yield cpp % {"body": body}

    def decodeComment(self, node):
        val = self.decodeToken(node.children[0])
        yield self.consume(val).replace('#', '//', 1)

    def decodeFunctionDef(self, node):
        # return "function def"
        child_nodes = node.children
        params = {
            "type": self.consume(self.getDecoder(child_nodes[0])(child_nodes[0])),
            "name": self.consume(self.decodeName(child_nodes[1])),
            "args": "",
            "block": self.consume(self.decodeBlock(child_nodes[-1])),
        }
        if len(child_nodes) == 6:
            params["args"] = self.consume(self.decodeParams(child_nodes[3]))
        if params["name"] == "main":
            params["name"] = "__main__"
        cpp = "%(type)s %(name)s( %(args)s )%(block)s"
        yield cpp % params

    def decodeOperator(self, node):
        # return "function def"
        child_nodes = node.children
        params = {
            "type": self.consume(self.getDecoder(child_nodes[0])(child_nodes[0])),
            "args": "",
            "block": self.consume(self.decodeBlock(child_nodes[-1])),
        }
        if len(child_nodes) == 5:
            params["args"] = self.consume(self.decodeParams(child_nodes[3]))

        cpp = "operator %(type)s( %(args)s )%(block)s"
        yield cpp % params

    def decodeClassDef(self, node):
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "block": self.consume(self.decodeBlock(child_nodes[-1])),
            "parent": ""
        }
        if len(child_nodes) == 4:
            params["parent"] = ': public ' + self.consume(self.decodeParams(child_nodes[2]))

        cpp = "struct %(type)s %(parent)s %(block)s;"
        yield (cpp % params).replace('\n;',';')

    def decodeBinExpression(self, node):
        lhs = node.children[0]
        operator = node.children[1]
        rhs = node.children[2]
        params = {
            "lhs": self.consume(self.getDecoder(lhs)(lhs)),
            "operator": self.consume(self.getDecoder(operator)(operator)),
            "rhs": self.consume(self.getDecoder(rhs)(rhs))
        }
        cpp = "%(lhs)s %(operator)s %(rhs)s"
        yield (cpp % params)


    def decodeArgs(self, node):
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            tmp = self.consume(self.getDecoder(sub_node)(sub_node))
            if not isinstance(sub_node, Token) and sub_node.data == "string":
                tmp = "'%s'" % tmp
            data += '%s ' % tmp
        args = "".join(data)
        yield args.replace(' ,', ',').replace('  )', ')')

    def decodeParams(self, node):
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            data += self.consume(self.getDecoder(sub_node)(sub_node))
            data += ' '
        yield "".join(data).replace(':', '').replace(' ,', ',')

    def decodeExpression(self, node):
        # yield "expression"
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            data += self.getDecoder(sub_node)(sub_node)
        yield "".join(data)

    def decodeReturn(self, node):
        raw = node.children[0]
        name = self.consume(self.getDecoder(raw)(raw))
        yield "return %s;" % name

    def decodeCall(self, node):
        child_nodes = node.children
        params = {
            "name": self.consume(self.decodeName(child_nodes[0])),
            "args": ""
        }
        if len(child_nodes) > 3:
            args = self.consume(self.decodeArgs(child_nodes[2]))
            params["args"] = args
        cpp = "%(name)s(%(args)s)"
        yield cpp % params

    def decodeConstruct(self, node):
        child_nodes = node.children
        params = {}
        cpp = ""
        if not isinstance(child_nodes[0],Token):
            params = {
                "name": self.consume(self.decodeName(child_nodes[0])),
                "args": ""
            }
            if len(child_nodes) > 3:
                args = self.consume(self.decodeArgs(child_nodes[2]))
                params["args"] = args
            cpp = "%(name)s(%(args)s)"
        else:
            params = self.consume(self.decodeArgs(child_nodes[1]))
            cpp = "{%s}"
        yield cpp % params


    def consume(self, val):
        ret = val
        from types import GeneratorType as generator
        while(isinstance(ret, generator)):
            ret = next(ret)
        return ret

    def decodeWhile(self, node):
        child_nodes = node.children
        params = {
            "condition": self.consume(self.getDecoder(child_nodes[1])(child_nodes[1])),
            "block": self.consume(self.getDecoder(child_nodes[3])(child_nodes[3])),
        }
        cpp = "while(%(condition)s)%(block)s;"
        yield cpp % params

    def decodeAssignment(self, node):
        child_nodes = node.children

        params = {
            "name":  self.consume(self.getDecoder(child_nodes[0])(child_nodes[0])),
            "offset":"[" +  self.consume(self.getDecoder(child_nodes[2])(child_nodes[2])) + "]",
            "rval": self.consume(self.getDecoder(child_nodes[5])(child_nodes[5])),
        } if len(child_nodes) == 7 else {
            "name":  self.consume(self.getDecoder(child_nodes[0])(child_nodes[0])),
            "offset": "",
            "rval": self.consume(self.getDecoder(child_nodes[2])(child_nodes[2])),
        }
        cpp = "%(name)s%(offset)s = %(rval)s;"
        yield cpp % params

    def decodeVarDeclare(self, node):
        raw = node.children[0]
        yield self.getDecoder(raw)(raw)

    def decodeAggregateDeclare(self, node):
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "size": self.consume(self.decodeRVal(child_nodes[2])),
            "name": self.consume(self.decodeName(child_nodes[4])),
        }
        cpp = "std::vector<%(type)s> %(name)s(%(size)s);"
        yield cpp % params

    def decodeScalareDeclare(self, node):
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "name": self.consume(self.decodeName(child_nodes[1])),
        }
        cpp = "%(type)s %(name)s;"
        yield cpp % params

    def decodeVarDef(self,node):
        raw = node.children[0]
        yield self.getDecoder(raw)(raw)

    def decodeAggregateDef(self, node):
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "name": self.consume(self.decodeName(child_nodes[1])),
            "val": self.consume(self.decodeRVal(child_nodes[3])),
        }
        cpp = "std::array<%(type)s,%(size)s> %(name)s = %(val)s ;"
        yield cpp % params

    def decodeScalarDef(self, node):
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "name": self.consume(self.decodeName(child_nodes[1])),
            "val": self.consume(self.decodeRVal(child_nodes[3])),
        }
        cpp = "%(type)s %(name)s = %(val)s ;"
        yield cpp % params

    def decodeRaw(self, node):
        yield str(node)

    def decodeConstant(self, node):
        yield node.children[0].value

    def decodeToken(self, node):
        yield node.value

    def getDecoder(self, node, default=decodeRaw):
        name = ""
        if not isinstance(node, Token):
            name = node.data
        else:
            name = node.type
        return self.nodeDecoders.get(name, partial(default, self))

    def decodeDecNumber(self, token):
        raw = token.value
        yield int(raw)

    def decodeHexNumber(self, token):
        raw = token.value
        yield int(raw, 16)

    def decodeOctNumber(self, token):
        raw = token.value
        yield int(raw, 8)

    def decodeBinNumber(self, token):
        raw = token.value
        yield int(raw, 2)

    def decodeFloat(self, token):
        raw = token.value
        yield "%sf" % float(raw.replace('f', ''))

    def decodeFixed(self, token):
        raw = token.value
        yield "%s_fp" % decimal.Decimal(raw)

    def decodeNumber(self, node):
        sub_node = node.children[0]
        yield self.getDecoder(sub_node)(sub_node)

    def decodeString(self, node):
        raw = node.children[0].value
        if node.children[0].type == "STRING":
            yield raw[1:-1]
        else:
            yield raw[3:-3]

    def decodeLiteral(self, node):
        if len(node.children) > 1:
            data = ['R"===(']
            for sub_node in node.children:
                data += self.consume(self.decodeString(sub_node))
            data += ')==="'
            yield "".join(data)
        else:
            sub_node = node.children[0]
            result = self.consume(self.getDecoder(sub_node)(sub_node))
            if sub_node.data == "string":
                result = "\"%s\"" % result
            yield result

    def decodeRVal(self, node):
        yield self.getDecoder(node)(node)

    def decodeName(self, node):
        yield self.decodeToken(node.children[0])

    def decodeRuntimeVal(self, node):
        sub_node = node.children[0]
        yield self.getDecoder(sub_node)(sub_node)

    def decodeScalarTypeName(self, node):
        yield self.decodeToken(node.children[0])

    def decodeAggregateTypeName(self, node):
        raw = node.children[0]
        typename = self.consume(self.getDecoder(raw)(raw))
        yield "std::vector<%s>" % typename

    def decodePointerTypeName(self, node):
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            data += self.consume(self.getDecoder(sub_node)(sub_node))
        yield "".join(data)

    def decodeModule(self, node):
        child_nodes = node.children
        data = ["namespace "]
        for sub_node in child_nodes[1:]:
            data += self.consume(self.getDecoder(sub_node)(sub_node))
            data += ' '
        yield "".join(data[:-1])

    def decodeImport(self, node):
        raw = node.children[1]
        yield "using namespace %s;" % self.consume(self.getDecoder(raw)(raw))

    def decodeFrom(self, node):
        raw = node.children
        params = {}
        cpp = ""
        if(raw[3].data != "name"):
            params = {
                "module": self.consume(self.getDecoder(raw[1])(raw[1])),
                "name": self.consume(self.getDecoder(raw[3])(raw[3])),
            }
            cpp = "using %(name)s = %(module)s::%(name)s;"
        else :
            params = {
                "module": self.consume(self.getDecoder(raw[1])(raw[1])),
                "name": self.consume(self.getDecoder(raw[3])(raw[3])),
            }
            cpp = "auto& %(name)s = %(module)s::%(name)s;"
        yield cpp % params

    def defaultNode(self, node, out=sys.stdout):
        print("// ", node, file=out)
