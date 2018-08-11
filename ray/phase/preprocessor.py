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
        self.all_includes = {}

    def processSrc(self, main_filename, output_file):
        include_files = ['runtime/header.ray', main_filename]
        while include_files:
            include_files = self.processSrcFiles(include_files)
        include_files = ['runtime/footer.ray']
        while include_files: # NOTE: This will normally loop once
            include_files = self.processSrcFiles(include_files)
        self.unifySrc(output_file)

    def unifySrc(self, output_file):
        for tree in self.all_includes.values():
            self.processTree(tree,output_file)

    def processSrcFiles(self, include_files):
        for file in include_files:
            if file not in  self.all_includes:
                self.all_includes[file] = None
        for filename in include_files:
            found_includes = self.extractIncludes(filename)
            include_files = set()
            for file in found_includes:
                if file not in self.all_includes:
                    include_files.add(file)
        return include_files

    def extractIncludes(self, filename):
        tree = None
        includes = set()
        with open(filename) as input:
            tree = self.parser.parse(input.read())
        for node in tree.children:
            if self.isInclude(node):
                includes.add(self.extractInclude(node))
        self.all_includes[filename] = tree
        return includes
    
    def extractInclude(self, node):
        raw = node.children[0]
        result = self.getDecoder(raw)(raw)
        args = (self.prefix, result.replace('include','').replace(' ', '').replace(';',''))
        return "%s/%s.ray" % args

    def isInclude(self,node):
        return ((not isinstance(node, Token)) 
                and node.data == 'include_statement')

    def processTree(self, tree, out):
        for node in tree.children:
            self.processNode(node, out)

    def processNode(self, node, out):
        if self.isInclude(node): return
        print(self.decodeRaw(node),file=out)

    def decodeRaw(self, node):
        if not isinstance(node, Token):
            result = []
            for child in node.children:
                result.append(self.getDecoder(child)(child))
            return " ".join(result)
        else:
            return str(node)

    def decodeInclude(self, node):
        return ""
        
    def getDecoder(self, node, default=decodeRaw):
        name = ""
        if not isinstance(node, Token):
            name = node.data
        else:
            name = node.type
        return self.nodeDecoders.get(name, partial(default, self))