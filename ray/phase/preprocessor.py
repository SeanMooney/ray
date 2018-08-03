from functools import partial
from io import StringIO

from lark import Lark
from lark.lexer import Token

class IncludeProcessor(object):

    def __init__(self, prefix, **kwargs):
        self.prefix = prefix
        with open("grammer/include.ebnf") as grammer:
            self.parser = Lark(grammer.read(), parser='lalr',
                               lexer='standard')
        self.nodeDecoders = {
            "include_statement": self.decodeInclude,
        }
        self.included_files = []

    def processSrc(self,main_filename,output_file):
        data = []
        self.processBuffered(['runtime/footer.ray'], data)
        include_files = [main_filename]
        while include_files:
            include_files = self.processBuffered(include_files, data)
        self.processBuffered(['runtime/header.ray'], data)
        for d in reversed(data):
            print(d, file=output_file)

    def processBuffered(self, include_files, data):
        buffer = StringIO()
        include_files = self.processFiles(buffer, include_files)
        data.append(buffer.getvalue())
        return include_files

    def processFiles(self, output_file, input_files=[]):
        result = []
        tree = None
        for f in input_files:
            print("processing includes for: %s." % f)
            with open(f) as input_file:
                tree = self.parser.parse(input_file.read())
            found = self.processTree(tree, output_file)
            for f in found:
                result.append(f)
            print("include: %s succeed." % f)
        return result

    def processTree(self, tree, out):
        self.included_files = []
        for node in tree.children:
            self.processNode(node, out)
        return  list(reversed(self.included_files))

    def processNode(self, node, out):
        result = self.getDecoder(node)(node)
        print(result,file=out)

    def decodeRaw(self, node):
        
        if not isinstance(node, Token):
            result = []
            for child in node.children:
                result.append(self.getDecoder(child)(child))
            return " ".join(result)
        else:
            return str(node)

    def decodeInclude(self, node):
        raw = node.children[0]
        result = self.getDecoder(raw)(raw)
        args = (self.prefix, result.replace('include','').replace(' ', '').replace(';',''))
        self.included_files.append("%s/%s.ray" % args)
        return ""
        
    def getDecoder(self, node, default=decodeRaw):
        name = ""
        if not isinstance(node, Token):
            name = node.data
        else:
            name = node.type
        return self.nodeDecoders.get(name, partial(default, self))