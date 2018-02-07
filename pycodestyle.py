#!/bin/bash
XARGS="xargs -0 -t pycodestyle"
for pyfile in `ls ./atlasclient/*.py`; do python dev/stripspace.py $pyfile; done
find ./atlasclient/ -name '*.py' -print0 | ${XARGS} --ignore=E501
