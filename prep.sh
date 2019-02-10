#!/bin/bash
sudo apt install clang-7 lld-7 lldb-7 libc++-7-dev libc++abi-7-dev clang-format-7 -y
pip install --user pipenv
pipenv install
