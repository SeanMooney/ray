#!/bin/bash
echo
echo transpileing
time pipenv run python3 ray.py
echo
echo compileing
time clang++-7 output.cpp
echo
echo running
time ./a.out