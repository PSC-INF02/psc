#!/bin/sh
# Usage: cat foobar.clean.wsd.linear | ./extract_systran_content.sh

sed 's/^/ /' \
| sed 's/ \([^|]*\)-.-[^ ]*/\1 /g' \
| sed -e 's/ \([,.) ]\|\]\)/\1/g' \
      -e 's/\([([]\) /\1/g' \
      -e 's/$/\n/'
