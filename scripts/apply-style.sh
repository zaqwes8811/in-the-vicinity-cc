#!/bin/sh
set -e

DIRS=("projects/")

for DIR in "${DIRS[@]}"
do
    find $DIR -iname "*.hpp" -o -iname "*.cpp" -o -iname "*.cc" -o -iname "*.h"  | xargs clang-format -i
done
