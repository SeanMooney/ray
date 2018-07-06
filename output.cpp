
#include <iostream>

using I32=int;
using Char=char;
using Void=void;
using String=std::string;

void print(String msg){
    std::cout << msg;
}

// this is a comment from ray to cpp

String genMessage(  ){
return "hello, world!\n";
}

String msg = genMessage() ;

I32 main( I32  argc, Char**  args  ){
print(msg );
print(genMessage() );
//print("Hello, "+"World!\n");
return 42;
}

