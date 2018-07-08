
#include <iostream>

using I32=int;
using Char=char;
using Void=void;
using String=std::string;

void print(String msg){
    std::cout << msg;
}
void println(String msg){
    std::cout << msg << '\n';
}

// this is a comment from ray to cpp

String genMessage(  ){
return "hello, world!\n";
}


I32 add( I32  lhs, I32  rhs  ){
return lhs + rhs;
}

String msg = genMessage() ;

 struct Bool  {
};

 struct True  {

 operator bool(  ){
return true;
}


 operator String(  ){
return "True";
}

};

 struct False  {

 operator bool(  ){
return false;
}


 operator String(  ){
return "False";
}

};

I32 main( I32  argc, Char**  args  ){
// print(msg);
// print(genMessage());
// String val := {I32(42.0f)};
// print(val);
// print({I32(42.0f)});
printf("val: %d\n", 42 );
if(1 == 1){
println("this is a test" );
}

else if(1 == 2){
println("you have bigger problems if you get here" );
}

else {
println("this should also not print." );
}


return 0;
}

