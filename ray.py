import argparse
from io import StringIO

from lark import Lark

from cpp.transformer import RayToCpp

def main(args):

    print(args)
    main_file = "%s/%s" % (args.prefix,args.source)
    out_file = "%s/%s" % (args.out_dir, args.out)
    parser = None
    with open("ray.ebnf") as grammer:
        # parser = Lark(grammer.read(), parser='lalr',
        #               propagate_positions=True, lexer='contextual')
        # parser = Lark(grammer.read(), parser='lalr',
        #       propagate_positions=True, lexer='standard')
        parser = Lark(grammer.read(), propagate_positions=True)

    transPiler = RayToCpp(args.prefix)
    data = []
    processBuffered(parser, transPiler, ['runtime/footer.ray'], data)
    include_files = [main_file]
    while include_files:
        include_files = processBuffered(parser, transPiler, include_files, data)
    processBuffered(parser, transPiler, ['runtime/header.ray'], data)
    with open(out_file, "w") as output_file:
        for d in reversed(data):
            print(d, file=output_file)


def processBuffered(parser, transPiler, include_files, data):
    buffer = StringIO()
    include_files = processFiles(parser, transPiler, buffer, include_files)
    data.append(buffer.getvalue())
    return include_files


def processFiles(parser, transPiler, output_file, input_files=[]):
    tree = None
    for f in input_files:
        print("parsing: %s." % f)
        with open(f) as input_file:
            tree = parser.parse(input_file.read())
        result = transPiler.processTree(tree, output_file)
        print("parsing: %s succeed." % f)
        return result


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

    args = cmd.parse_args()
    # execute only if run as a script
    main(args)
