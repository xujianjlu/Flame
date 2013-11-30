#!/bin/bash

for filename in `find third_party/boost/boost/config -name "*.hpp"`; do
  echo Deal with $filename ...
  # sed 's/#\s*include <boost\/\(.*\)>/#include \"third_party\/boost\/boost\/\1\"/' $filename > "$filename.tmp"
  sed 's/"boost\//"third_party\/boost\/boost\//' $filename > "$filename.tmp"
  rm -f $filename
  mv "$filename.tmp" $filename
  echo "                        [done!]"
done

