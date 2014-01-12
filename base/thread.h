// Copyright 2010  Inc. All Rights Reserved.
// Author: quj@.com (Jing Qu)

#ifndef BASE_THREAD_H_
#define BASE_THREAD_H_

#include <pthread.h>

#include "base/basictypes.h"

namespace base {

// Simple warper to pthread.
// Sample useage:
//
// class Mythread : public base::Thread {
//  public:
//   Mythread() { }
//  protected:
//   virtual void Run() {
//     LOG(INFO) << "int the thread";
//   }
// };
//
// ...
//
// Mythread mythread;
// mythread.Start();
//
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

 private:
  DISALLOW_COPY_AND_ASSIGN(Thread);
};

}  // namespace base

#endif  // BASE_THREAD_H_
