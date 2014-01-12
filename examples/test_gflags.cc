// Copyright [2013] <xujiantjdx@126.com / xujiantjdx@gmail.com>

#include <iostream>
#include "base/logging.h"

DEFINE_bool(bool_flags, true, "bool_flags");
DEFINE_string(str_flags, "str_flags", "str_flags");
DEFINE_int32(int32_flags, 1234, "int32_flags");
DEFINE_int64(int64_flags, 5678, "int64_flags");
DEFINE_uint64(uint64_flags, 123456, "uint64_flags");
DEFINE_double(double_flags, 3.1415926, "double_flags");

int main(int argc, char **argv) {
  base::ParseCommandLineFlags(&argc, &argv, true);
  LOG(INFO) << "bool_flags: " << FLAGS_bool_flags << std::endl;
  LOG(INFO) << "str_flags: " << FLAGS_str_flags << std::endl;
  LOG(INFO) << "int32_flags: " << FLAGS_int32_flags << std::endl;
  LOG(INFO) << "int64_flags: " << FLAGS_int64_flags << std::endl;
  LOG(INFO) << "uint64_flags: " << FLAGS_uint64_flags << std::endl;
  LOG(INFO) << "double_flags: " << FLAGS_double_flags << std::endl;

  return 0;
}
