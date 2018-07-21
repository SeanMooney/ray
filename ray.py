from lark import Lark

from cpp.transformer import RayToCpp

def main():
    parser = None
    with open("ray.ebnf") as grammer:


        # parser = Lark(grammer.read(), parser='lalr',
        #               propagate_positions=True, lexer='contextual')
        # parser = Lark(grammer.read(), parser='lalr',
        #       propagate_positions=True, lexer='standard')
        parser = Lark(grammer.read(), propagate_positions=True)

    input_files = ['runtime/header.ray',
                   'input/main.ray',
                   'runtime/footer.ray']

    transPiler = RayToCpp()
    tree = None
    with open("output/output.cpp", "w") as out:
        for f in input_files:
            print("parsing: %s." % f)
            with open(f) as input_file:
                tree = parser.parse(input_file.read())
            transPiler.processTree(tree, out)
            print("parsing: %s succeed." % f)

if __name__ == "__main__":
    # execute only if run as a script
    main()
