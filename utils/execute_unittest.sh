#!/bin/bash

unittest_file="$1" # should give the absolutely path
output_file="$2"
wait_time="$3"
heap_check="$4" # true or false

tmp_file="/tmp/unittest_$$.tmp" # use this file to connect to threads

test_unittest() {
  $1 & # run the unittest
  echo $! > $tmp_file
  wait `cat $tmp_file` 2> /dev/null
  if [ $? -eq 0 ]
  then
    echo "OK" > $tmp_file
  else
    echo "FAIL" > $tmp_file
  fi
}

if [ -f $tmp_file ]; then
  rm $tmp_file
fi
touch $tmp_file # create tmp_file

if [ "$heap_check" == "on" ]; then
  export HEAPCHECK=normal
  export PPROF_PATH=thirdparty/pprof/bin/pprof
fi

test_unittest $unittest_file $output_file &
unittest_pid=""

while [ $wait_time -gt 0 ]; do
  sleep 1
  if [ "`cat $tmp_file`" = "OK" ]; then
    echo "PASS" >> $output_file
    echo -e "$unittest_file \033[92mPASS\033[0m"
    rm $tmp_file
    exit 0
  elif [ "`cat $tmp_file`" = "FAIL" ]; then
    echo "FAIL" >> $output_file
    echo -e "$unittest_file \033[91mFAIL\033[0m"
    rm $tmp_file
    exit 1
  else
    if [ -z $unittest_pid ]; then
      unittest_pid=`cat $tmp_file`
    fi
    wait_time=$(($wait_time - 1))
  fi
done

echo "TIMEOUT" > $output_file
kill -9 $unittest_pid
echo -e "$unittest_file \033[91mTIMEOUT\033[0m"
rm $tmp_file
exit 2
