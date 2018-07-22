#!/bin/bash
echo
echo transpileing
time pipenv run python3 ray.py --prefix input
echo
echo fromating
time clang-format -i output/output.cpp
echo
echo compileing
time clang++-6.0 -Os -Og -g  output/output.cpp
echo
echo running
time ./a.out
