#ifndef BASE_THREAD_POOL_H_
#define BASE_THREAD_POOL_H_

#include <pthread.h>
#include <semaphore.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>

#include <queue>

#include "base/mutex.h"
#include "base/third_party/dynamic_annotations/dynamic_annotations.h"

namespace base {

class Closure;
class WorkerThread;

class ProducerConsumerQueue {
 public:
  ProducerConsumerQueue(int unused) {
    ANNOTATE_PCQ_CREATE(this);
  }
  ~ProducerConsumerQueue() {
    CHECK(q_.empty());
    ANNOTATE_PCQ_DESTROY(this);
  }

  // Put.
  void Put(void *item) {
    mu_.Lock();
      q_.push(item);
      ANNOTATE_CONDVAR_SIGNAL(&mu_); // LockWhen in Get()
      ANNOTATE_PCQ_PUT(this);
    mu_.Unlock();
  }

  // Get.
  // Blocks if the queue is empty.
  void *Get() {
    mu_.LockWhen(Condition(IsQueueNotEmpty, &q_));
      void* item = NULL;
      bool ok = TryGetInternal(&item);
      CHECK(ok);
    mu_.Unlock();
    return item;
  }

  // If queue is not empty,
  // remove an element from queue, put it into *res and return true.
  // Otherwise return false.
  bool TryGet(void **res) {
    mu_.Lock();
      bool ok = TryGetInternal(res);
    mu_.Unlock();
    return ok;
  }

 private:
  Mutex mu_;
  std::queue<void*> q_; // protected by mu_

  // Requires mu_
  bool TryGetInternal(void ** item_ptr) {
    if (q_.empty())
      return false;
    *item_ptr = q_.front();
    q_.pop();
    ANNOTATE_PCQ_GET(this);
    return true;
  }

  static bool IsQueueNotEmpty(std::queue<void*> * queue) {
     return !queue->empty();
  }
};

// A thread pool that uses ProducerConsumerQueue.
//   Usage:
//   {
//     ThreadPool pool(n_workers);
//     pool.StartWorkers();
//     pool.Add(NewCallback(func_with_no_args));
//     pool.Add(NewCallback(func_with_one_arg, arg));
//     pool.Add(NewCallback(func_with_two_args, arg1, arg2));
//     ...  more calls to pool.Add()
//
//      the ~ThreadPool() is called: we wait workers to finish
//      and then join all threads in the pool.
//   }

class ThreadPool {
 public:
  // Create n_threads threads, but do not start.
  explicit ThreadPool(int n_threads);

  // Wait workers to finish, then join all threads.
  ~ThreadPool();

  // Start all threads.
  void StartWorkers();

  // Add a closure.
  void Add(Closure *closure) {
    queue_.Put(closure);
  }

  int num_threads() { return workers_.size();}

 private:
  std::vector<WorkerThread*>  workers_;
  ProducerConsumerQueue queue_;

  static void* Worker(void *p);
};


/// Function pointer with zero, one or two parameters.
struct Closure {
  typedef void (*F0)();
  typedef void (*F1)(void *arg1);
  typedef void (*F2)(void *arg1, void *arg2);
  int  n_params;
  void *f;
  void *param1;
  void *param2;

  void Execute() {
    if (n_params == 0) {
      (F0(f))();
    } else if (n_params == 1) {
      (F1(f))(param1);
    } else {
      CHECK(n_params == 2);
      (F2(f))(param1, param2);
    }
    delete this;
  }
};

// static Closure *NewCallback(void (*f)()) {
//   Closure *res = new Closure;
//   res->n_params = 0;
//   res->f = (void*)(f);
//   res->param1 = NULL;
//   res->param2 = NULL;
//   return res;
// }

template <class P1>
Closure *NewCallback(void (*f)(P1), P1 p1) {
  CHECK(sizeof(P1) <= sizeof(void*));
  Closure *res = new Closure;
  res->n_params = 1;
  res->f = (void*)(f);
  res->param1 = (void*)p1;
  res->param2 = NULL;
  return res;
}

template <class P1, class P2>
Closure *NewCallback(void (*f)(P1, P2), P1 p1, P2 p2) {
  CHECK(sizeof(P1) <= sizeof(void*));
  CHECK(sizeof(P2) <= sizeof(void*));
  Closure *res = new Closure;
  res->n_params = 2;
  res->f = (void*)(f);
  res->param1 = (void*)p1;
  res->param2 = (void*)p2;
  return res;
}

/// Wrapper for pthread_create()/pthread_join().
class WorkerThread {
 public:
  typedef void *(*worker_t)(void*);

  WorkerThread(worker_t worker,
               void *arg = NULL,
               const char *name = NULL)
      :w_(worker), arg_(arg), name_(name) {}

  WorkerThread(void (*worker)(void),
               void *arg = NULL,
               const char *name = NULL)
      :w_(reinterpret_cast<worker_t>(worker)), arg_(arg), name_(name) {}

  WorkerThread(void (*worker)(void *),
               void *arg = NULL,
               const char *name = NULL)
      :w_(reinterpret_cast<worker_t>(worker)), arg_(arg), name_(name) {}

  ~WorkerThread(){ w_ = NULL; arg_ = NULL;}

  void Start() {
    pthread_attr_t attr;
    CHECK_EQ(pthread_attr_init(&attr), 0);
    CHECK_EQ(pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE),
             0);

    CHECK(0 == pthread_create(&t_, &attr, (worker_t)ThreadBody, this));
    CHECK_EQ(pthread_attr_destroy(&attr), 0);
  }

  void Join() {
    CHECK(0 == pthread_join(t_, NULL));
  }

  pthread_t tid() const { return t_; }

 private:
  static void ThreadBody(WorkerThread *my_thread) {
    if (my_thread->name_) {
      ANNOTATE_THREAD_NAME(my_thread->name_);
    }
    my_thread->w_(my_thread->arg_);
  }
  pthread_t t_;
  worker_t  w_;
  void     *arg_;
  const char *name_;
};

}

#endif
