#!/bin/bash

for filename in `find thirdparty/boost/boost/config -name "*.hpp"`; do
  echo Deal with $filename ...
  # sed 's/#\s*include <boost\/\(.*\)>/#include \"thirdparty\/boost\/boost\/\1\"/' $filename > "$filename.tmp"
  sed 's/"boost\//"thirdparty\/boost\/boost\//' $filename > "$filename.tmp"
  rm -f $filename
  mv "$filename.tmp" $filename
  echo "                        [done!]"
done

