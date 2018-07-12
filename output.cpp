
#include <iostream>
#include <vector>

using I32 = int;
using Char = char;
using Void = void;
using String = std::string;

#define TRUE__ true
#define FALSE__ false

void print(String msg) { std::cout << msg; }

template <typename T> void printv(std::vector<T> vec) {
    int pos = 0;
    for (T& val : vec) {
        std::cout << "element " << pos++ << ":" << val << '\n';
    }
}

void println(String msg) { std::cout << msg << '\n'; }

struct Bool {};
struct True {
    operator bool() { return TRUE__; }
    operator String() { return "True"; }
};
struct False {
    operator bool() { return FALSE__; }
    operator String() { return "False"; }
};
std::vector<I32> iota(I32 max) {
    I32 current = 0;
    std::vector<I32> result(max);
    while (current < max) {
        result[current] = current;
        current = current + 1;
    };
    return result;
}
// I32[100] fibCache;
// def func I32 fib(I32: i){
//    I32 cached := fibCache[i];
//    if(cached !=0){
//        return cached;
//    }
//    if(i<=1){
//        fibCache[i] :=1;
//    }elif(i==2){
//        fibCache[i] :=1;
//    }else{
//        fibCache[i] := fib(i-2) + fib(i-1);
//    }
//    return fibCache[i];
//}
I32 fib(I32 i) {
    if (i <= 1) {
        return 1;
    } else if (i == 2) {
        return 1;
    } else {
        return fib(i - 2) + fib(i - 1);
    }
}
std::vector<I32> fibRange(I32 max) {
    I32 current = 1;
    std::vector<I32> result(max);
    while (current < max) {
        result[current] = fib(current);
        current = current + 1;
    };
    return result;
}
I32 main(I32 argc, Char** args) {
    I32 max = 42;
    std::vector<I32> data(max);
    printf("iota(%d):\n", max);
    data = iota(max);
    printv(data);
    printf("fibRange(%d):\n", max);
    data = fibRange(max);
    printv(data);
    printf("fib(42):%d\n", fib(42));
    return 0;
}
