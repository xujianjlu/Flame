#include <iostream>
#include "base/logging.h"
#include "base/flags.h"
#include "base/string_piece.h"
#include "time.h"
#include "base/fnv.h"
#include "base/thread_pool.h"

DEFINE_int32(end, 1000, "The last record to read");

void Print() {
  LOG(INFO) << "hahahahha";
}

int main(int argc, char **argv) {
  base::Time t = base::Time::NowFromSystemTime();
  base::StringPiece st("dddd");
  base::ParseCommandLineFlags(&argc, &argv, true);
  LOG(INFO) << FLAGS_end;
  CHECK(1 == 1) << "dd";
  {
    base::ThreadPool pool(10);
    pool.StartWorkers();
    pool.Add(base::NewCallback(Print));
    pool.Add(base::NewCallback(Print));
    pool.Add(base::NewCallback(Print));
  }

  uint64 digest[2];
  base::fnv128("hahaha", 6, &digest);
  LOG(INFO) << digest[0] << " " << digest[1];
  base::fnv128("hahaha3dafgeroidkjvnkiyurgmdfg"
               "nmlsd;akwpoeskjsljdglhk ,mslfjksljf", 30, &digest);
  LOG(INFO) << digest[0] << " " << digest[1];
  return 0;
}
