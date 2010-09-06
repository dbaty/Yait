#!/bin/bash

DIR="/tmp/coverage-output"

coverage run setup.py nosetests
rm -rf "$DIR"
coverage html -d "$DIR" --include "yait/*"
open "$DIR/index.html"