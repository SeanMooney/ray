
#include <cstdint>
#include <stdio.h>
#include <vector>
namespace Runtime {
using Int8=int8_t;
using Int16=int16_t;
using Int32=int32_t;
using Int64=int64_t;
using UInt8=uint8_t;
using UInt16=uint16_t;
using UInt32=uint32_t;
using UInt64=uint64_t;
using Float32=float;
using Float64=double;
using Char=char;
using Void=void;
using CString=const char*;
#define TRUE__ true
#define FALSE__ false
void print(CString msg){
printf("%s",msg);
}
template<typename T>
void printv(std::vector<T> vec){
Int32 pos=0;
for(T& val : vec){
printf("Element(%d): %ld\n",pos++,(Int64)val);
}
}
void println(CString msg){
printf("%s\n",msg);
}
}


namespace Runtime {
struct Bool  {
};
struct True  {
operator bool(  ){
return TRUE__;
}
operator CString(  ){
return "True";
}
};
struct False  {
operator bool(  ){
return FALSE__;
}
operator CString(  ){
return "False";
}
};
}

namespace Runtime {
#undef TRUE__
#undef FALSE__
}

namespace Test {
using namespace Runtime;
std::vector<Int32> iota( Int8  max  ){
Int32 current = 0 ;
std::vector<Int32> result(max);
while(current < max){
result[current] = current;
current = current + 1;
};
return result;
}
std::vector<Int64> fibCache(64);
Int64 fib( Int8  i  ){
Int64& cached = fibCache[i] ;
if(cached != 0){
return cached;
}
if(i <= 1){
cached = 1;
}
else if(i == 2){
cached = 2;
}
else {
cached = fib(i - 2 ) + fib(i - 1 );
}
return cached;
}
std::vector<Int64> fibRange( Int8  max  ){
std::vector<Int64> result(max);
Int8 current = 0 ;
while(current < max){
result[current] = fib(current );
current = current + 1;
};
return result;
}
struct Object  {
};
}
using namespace Runtime;
struct Pair  {
};
Int32 __main__( Int32  argc, Char**  args  ){
Int8 max = 64 ;
println("hello world" );
{
auto& iota = Test::iota;
printf("iota(%d):\n", max );
std::vector<Int32> data(max);
data = iota(max );
printv(data );
}
// from Test import Object;
{
using namespace Test;
printf("fibRange(%d):\n", max );
auto data = fibRange(max ) ;
printv(data );
}
return 0;
}

Int32 main(Int32 argc, Char** args){ return __main__(argc,args);}

