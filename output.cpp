
#include <iostream>

using I32 = int;
using Char = char;
using Void = void;
using String = std::string;
#define TRUE__ true
#define FALSE__ false

void print(String msg) { std::cout << msg; }

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

I32 fib(I32 i) {
    if (i == 1) {
        return 1;
    }

    else if (i == 2) {
        return 1;
    }

    else {
        return fib(i - 2) + fib(i - 1);
    }
}

I32 main(I32 argc, Char** args) {
    printf("%d", fib(42));
    return 0;
}
