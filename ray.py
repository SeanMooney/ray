from lark import Lark

def main():
    tree = ""
    lexer = None
    with open("ray.ebnf") as grammer:
        lexer = Lark(grammer.read(), parser='lalr', propagate_positions=True)
        #  lexer = Lark(grammer.read())

    with open("input.ray") as input:
        tree = lexer.parse(input.read())

        with open("output.cpp","w") as out:
            print(tree)
            print(tree.pretty(), file=out)
            # for node in tree:
                # print(node)

if __name__ == "__main__":
    # execute only if run as a script
    main()
