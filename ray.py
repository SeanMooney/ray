import sys
import decimal
from functools import partial

from lark import Lark
from lark.tree import pydot__tree_to_png
from lark import Transformer
from lark.lexer import Token


class RayToCpp(object):

    def __init__(self, *args, **kwargs):
        self.nodeTransformers = {
            "variable_define": self.processVarDef,
            "comment": self.processComment,
            "block_statement": self.processBlock,
            "function_define": self.processFunction,
            "return_statement": self.processReturn,
            "expression_statement": self.processExpressionStatement
        }

        self.nodeDecoders = {
            "literal_value": self.decodeLiteral,
            "runtime_value": self.decodeRuntimeVal,
            "variable_define": self.decodeVarDef,
            "block_statement": self.decodeBlock,
            "function_define": self.decodeFunctionDef,
            "return_statement": self.decodeReturn,
            "expression_statement": self.decodeExpression,
            "call_expression": self.decodeCall,
            "name": self.decodeName,
            "scalar_type_name": self.decodeScalarTypeName,
            "aggregate_type_name": self.decodeAggregateTypeName,
            "pointer_type_name": self.decodePointerTypeName,
            "comment": self.decodeComment,
            "number": self.decodeNumber,
            "token": self.decodeToken,
            "string": self.decodeString,
            "block_statement": self.decodeBlock,
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

    def decodeArgs(self, node):
        child_nodes = node.children
        data = []
        for sub_node in child_nodes:
            tmp = self.consume(self.getDecoder(sub_node)(sub_node))
            if sub_node.data == "string":
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
        parser = Lark(grammer.read(), parser='lalr', propagate_positions=True)
        #  parser = Lark(grammer.read())

    tree = None
    with open("main.ray") as input:
        tree = parser.parse(input.read())
        # print(tree)

    header = """
#include <iostream>

using I32=int;
using Char=char;
using Void=void;
using String=std::string;

void print(String msg){
    std::cout << msg;
}
"""
    transPiler = RayToCpp()
    with open("output.cpp", "w") as out:
        print(header, file=out)
        transPiler.processTree(tree, out)


if __name__ == "__main__":
    # execute only if run as a script
    main()
