import argparse
from io import StringIO

from lark import Lark

from code_gen.cpp.transformer import RayToCpp
from phase.preprocessor import IncludeProcessor
# from phase.inference import SymbolProcessor
from phase.ast_builder import ASTProcessor

def main(args):

    print(args)
    main_file = "%s/%s" % (args.prefix,args.source)
    unity_file = "%s/unity.ray" % args.build_dir 

    preprocessor = IncludeProcessor(args.prefix)
    with open(unity_file, "w") as output_file:
        preprocessor.processSrc(main_file,output_file)
        
    out_file = "%s/%s" % (args.build_dir, args.out)
    parser = None
    with open("grammer/ray.ebnf") as grammer:
        parser = Lark(grammer.read(), propagate_positions=True)
    tree = None
    with open(unity_file) as inpute_file:
        tree = parser.parse(inpute_file.read())
    
    # symbol_builder = SymbolProcessor()
    # symbol_builder.processTree(tree)
    astBuilder = ASTProcessor()
    astBuilder.processTree(tree)

    transPiler = RayToCpp(args.prefix)
    with open(out_file, "w") as output_file:
        transPiler.processTree(tree,output_file)

if __name__ == "__main__":
    cmd = argparse.ArgumentParser(description='Ray Compiler')
    cmd.add_argument('--src', dest='source', default="main.ray",
                     help='ray source file', type=str)
    cmd.add_argument('--prefix', dest='prefix', default=".",
                     help='ray source dir', type=str)
    cmd.add_argument('--out-dir', dest='out_dir', default="output",
                     help='ray source dir', type=str)
    cmd.add_argument('--out', dest='out', default="output.cpp",
                     help='output file', type=str)
    cmd.add_argument('--build-dir', dest='build_dir', default="build",
                     help='ray build dir', type=str)
    
    args = cmd.parse_args()
    # execute only if run as a script
    main(args)
