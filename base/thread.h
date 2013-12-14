// Copyright 2010 . All Rights Reserved.
// Author: kingqj@gmail.com (Jing Qu)

#ifndef BASE_THREAD_H_
#define BASE_THREAD_H_

#include <dirent.h>
#include <errno.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/mman.h>  // mmap
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include <queue>

#include "base/mutex.h"

namespace base {

class Thread {
 public:
  Thread(bool joinable = false) : started_(false), joinable_(joinable) {}
  virtual ~Thread() {}

  pthread_t tid() const {
    return tid_;
  }

  void SetJoinable(bool joinable) {
    if (!started_)
      joinable_ = joinable;
  }

  void Start();

  void Join();

 protected:
  virtual void Run() = 0;

  static void* ThreadRunner(void* arg) {
    Thread *t = reinterpret_cast<Thread*>(arg);
    t->Run();
    return NULL;
  }

  pthread_t tid_;
  bool started_;
  bool joinable_;
};

}  // namespace base

#endif  // BASE_THREAD_H_
