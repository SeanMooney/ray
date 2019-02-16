#!/bin/bash
echo
prefix=${prefix:-"input"}
echo transpileing ${prefix}
time pipenv run python3 ray/ray.py --prefix ${prefix}
echo
echo fromating
time clang-format-7 -i build/output.cpp
echo
echo compileing
extra_flags=${extra_flags:-""}
extra_features=""
sanatizers=""
error_checks=""
if [[ "true" == "${release:-false}" ]]; then
    extra_features="-flto=thin -fwhole-program-vtables"
    optimizations="-O3 -g0 -march=native"
    error_checks="-pedantic"
else
    optimizations="-Os -Og -g -glldb -fstandalone-debug -fno-omit-frame-pointer"
    sanatizers="-fsanitize=undefined,address"
    error_checks="-Werror -Wextra-tokens -Wbind-to-temporary-copy -pedantic"
fi
#min_runtime="-ffreestanding"
min_runtime=""
stdlib="-stdlib=libc++ -lc++ -lc++abi"
features="-std=c++17 -fpic -pie -fno-exceptions -fstrict-vtable-pointers -ffast-math -fvisibility=protected"
compiler="clang++-7"
linker="-fuse-ld=lld"
cmd="${compiler} ${linker} ${optimizations} -o output/output ${stdlib} ${min_runtime} ${features} ${extra_features} ${sanatizers} ${error_checks} ${extra_flags} build/output.cpp"
echo ${cmd}
time ${cmd}
echo
echo running
time ./output/output
