
#include <cstdint>
#include <stdio.h>
#include <vector>
namespace Runtime {
using Int8 = int8_t;
using Int16 = int16_t;
using Int32 = int32_t;
using Int64 = int64_t;
using UInt8 = uint8_t;
using UInt16 = uint16_t;
using UInt32 = uint32_t;
using UInt64 = uint64_t;
using Float32 = float;
using Float64 = double;
using Char = char;
using Void = void;
using CString = const char*;
#define TRUE__ true
#define FALSE__ false
void print(CString msg) { printf("%s", msg); }
template <typename T> void printv(std::vector<T> vec) {
    Int32 pos = 0;
    for (T& val : vec) {
        printf("Element(%d): %ld\n", pos++, (Int64)val);
    }
}
void println(CString msg) { printf("%s\n", msg); }
} // namespace Runtime

namespace Runtime {

// def struct Bool{}
struct True {
    operator bool() { return TRUE__; }
    operator CString() { return "True"; }
};
struct False {
    operator bool() { return FALSE__; }
    operator CString() { return "False"; }
};
} // namespace Runtime

namespace Runtime {
#undef TRUE__
#undef FALSE__
} // namespace Runtime

namespace Utils {
using CString = Runtime::CString;
CString message() { return "hello from utils"; }
} // namespace Utils
namespace Temp {
using namespace Runtime;
Void printMessage(CString msg) { println(msg); }
} // namespace Temp
using Int32 = Runtime::Int32;
using Char = Runtime::Char;
Int32 __main__(Int32 argc, Char** args) {
    auto& printMessage = Temp::printMessage;
    Int32 x = 42;
    std::vector<Int32> y(100);
    printMessage("hello world");
    return 0;
}

Int32 main(Int32 argc, Char** args) { return __main__(argc, args); }
