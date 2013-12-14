// Copyright [2013] <xujiantjdx@126.com / xujiantjdx@gmail.com>

#include "base/logging.h"

int main(int argc, char **argv) {
  LOG(INFO) << "glog info";
  LOG(WARNING) << "glog warning";
  LOG(ERROR) << "glog error";
  // VLOG(1) << "vlog level: 1";
  // VLOG(2) << "vlog level: 2";
  // VLOG(3) << "vlog level: 3";

  return 0;
}
