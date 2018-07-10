import sys
import decimal
from functools import partial

from lark import Lark
from lark.tree import pydot__tree_to_png
from lark import Transformer
from lark.lexer import Token


class RayToCpp(object):

    def __init__(self, *args, **kwargs):
        self.targetLang = "cpp"
        self.nodeTransformers = {
            "variable_define": self.processVarDef,
            "comment": self.processComment,
            "block_statement": self.processBlock,
            "function_define": self.processFunction,
            "return_statement": self.processReturn,
            "expression_statement": self.processExpressionStatement,
            "class_define": self.processClass,
            "condtional_statement": self.processCondtional,
            "compiler_statement": self.processCompilerStatement
        }

        self.nodeDecoders = {
            "literal_value": self.decodeLiteral,
            "runtime_value": self.decodeRuntimeVal,
            "variable_define": self.decodeVarDef,
            "class_define": self.decodeClassDef,
            "function_define": self.decodeFunctionDef,
            "operator_define": self.decodeOperator,
            "construct_expression": self.decodeConstruct,
            "call_expression": self.decodeCall,
            "bin_expression": self.decodeBinExpression,
            "compiler_statement": self.decodeCompilerStatement,
            "block_statement": self.decodeBlock,
            "block": self.decodeBlock,
            "escaped_block": self.decodeEscapedBlock,
            "return_statement": self.decodeReturn,
            "expression_statement": self.decodeExpression,
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

    def processTree(self, tree, out=sys.stdout):
        for node in tree.children:
            self.processNode(node, out)

    def processNode(self, node, out=sys.stdout):
        func = self.nodeTransformers.get(node.data, self.defaultNode)
        func(node, out=out)


    def processCompilerStatement(self, node, out=sys.stdout):
        print(self.consume(self.decodeCompilerStatement(node)), file=out)

    def decodeCompilerStatement(self, node):
        raw = node.children
        if raw[1].children[0].value == self.targetLang:
            sub_node = raw[3]
            current = self.getDecoder(sub_node)(sub_node)
            data = []
            data += self.consume(current)
            data += "\n"
            yield "".join(data)
        else:
            yield ""

    def decodeEscapedBlock(self,node):
        yield node.children[0].value[3:-3]


    def processBlock(self, node, out=sys.stdout):
        print(self.consume(self.decodeBlock(node)), file=out)

    def decodeBlock(self, node):
        raw = node.children
        data = []
        for sub_node in raw:
            current = self.getDecoder(sub_node)(sub_node)
            data += self.consume(current)
            data += "\n"
        yield "".join(data)

    def processCondtional(self, node, out=sys.stdout):
        print(self.consume(self.decodeCondtional(node)), file=out)


    def decodeCondtional(self, node, out=sys.stdout):
        raw = node.children
        data = []
        for sub_node in raw:
            current = self.getDecoder(sub_node)(sub_node)
            data += self.consume(current)
            data += "\n"
        yield "".join(data)

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

    def processComment(self, node, out=sys.stdout):
        print(self.consume(self.decodeComment(node)), file=out)

    def decodeComment(self, node):
        val = self.decodeToken(node.children[0])
        yield self.consume(val).replace('#', '//', 1)

    def processFunction(self, node, out=sys.stdout):
        print(self.consume(self.getDecoder(node)(node)), file=out)

    def decodeFunctionDef(self, node):
        # return "function def"
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "name": self.consume(self.decodeName(child_nodes[1])),
            "args": "",
            "block": self.consume(self.decodeBlock(child_nodes[-1])),
        }
        if len(child_nodes) == 6:
            params["args"] = self.consume(self.decodeParams(child_nodes[3]))

        cpp = "\n%(type)s %(name)s( %(args)s )%(block)s"
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

        cpp = "\n operator %(type)s( %(args)s )%(block)s"
        yield cpp % params

    def processClass(self, node, out=sys.stdout):
        print(self.consume(self.getDecoder(node)(node)), file=out)

    def decodeClassDef(self, node):
        child_nodes = node.children
        params = {
            "type": self.consume(self.decodeScalarTypeName(child_nodes[0])),
            "block": self.consume(self.decodeBlock(child_nodes[-1])),
            "parent": ""
        }
        if len(child_nodes) == 4:
            params["parent"] = ': public ' + self.consume(self.decodeParams(child_nodes[2]))

        cpp = "\n struct %(type)s %(parent)s %(block)s;"
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

    def processExpressionStatement(self, node, out=sys.stdout):
        print(self.consume(self.getDecoder(node)(node)), file=out)

    def decodeExpression(self, node):
        # yield "expression"
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            data += self.getDecoder(sub_node)(sub_node)
        yield "".join(data)

    def processReturn(self, node, out=sys.stdout):
        result = self.consume(self.getDecoder(node)(node))
        print(result, file=out)

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

    def processVarDef(self, node, out=sys.stdout):
        result = self.consume(self.decodeVarDef(node))
        print(result, file=out)

    def decodeVarDef(self, node):
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
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            data += self.getDecoder(sub_node)(sub_node)
        yield "".join(data)

    def decodePointerTypeName(self, node):
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            data += self.getDecoder(sub_node)(sub_node)
        yield "".join(data)

    def defaultNode(self, node, out=sys.stdout):
        print("// ", node, file=out)


def main():
    parser = None
    with open("ray.ebnf") as grammer:


        # parser = Lark(grammer.read(), parser='lalr',
        #               propagate_positions=True, lexer='contextual')
        # parser = Lark(grammer.read(), parser='lalr',
        #       propagate_positions=True, lexer='standard')
        parser = Lark(grammer.read(), propagate_positions=True)


    tree = None
    with open("main.ray") as input:
    # with open("input.ray") as input:
        tree = parser.parse(input.read())

    transPiler = RayToCpp()
    with open("output.cpp", "w") as out:
        transPiler.processTree(tree, out)


if __name__ == "__main__":
    # execute only if run as a script
    main()
