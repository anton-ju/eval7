#!/bin/bash
python setup.py build_ext --inplace
cd tests
python -m unittest -v
