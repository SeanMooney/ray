#!/bin/bash
echo
echo transpileing
time pipenv run python3 ray/ray.py --prefix input
echo
echo fromating
time clang-format -i build/output.cpp
echo
echo compileing
time clang++-6.0 -Os -Og -g -o output/output  build/output.cpp
echo
echo running
time ./output/output
