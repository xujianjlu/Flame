#ifndef BASE_MUTEX_H_
#define BASE_MUTEX_H_

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
#include <assert.h>

#include "base/basictypes.h"
#include "base/logging.h"
#include "base/time.h"

#include "base/third_party/dynamic_annotations/dynamic_annotations.h"

namespace base {

/// Just a boolean condition. Used by Mutex::LockWhen and similar.
class Condition {
 public:
  typedef bool (*func_t)(void*);

  template <typename T>
  Condition(bool (*func)(T*), T* arg)
      : func_(reinterpret_cast<func_t>(func)), arg_(arg) {}

  Condition(bool (*func)())
      : func_(reinterpret_cast<func_t>(func)), arg_(NULL) {}

  bool Eval() { return func_(arg_); }
 private:
  func_t func_;
  void *arg_;
};

class Mutex {
  friend class CondVar;
 public:
  // This is used for the single-arg constructor
  enum LinkerInitialized { LINKER_INITIALIZED };

  // Create a Mutex that is not held by anybody.  This constructor is
  // typically used for Mutexes allocated on the heap or the stack.
  inline Mutex();
  // This constructor should be used for global, static Mutex objects.
  // It inhibits work being done by the destructor, which makes it
  // safer for code that tries to acqiure this mutex in their global
  // destructor.
  inline Mutex(LinkerInitialized);

  // Destructor
  inline ~Mutex();

  inline void Lock();    // Block if needed until free then acquire exclusively
  inline void Unlock();  // Release a lock acquired via Lock()
  inline bool TryLock(); // If free, Lock() and return true, else return false

  // Note that on systems that don't support read-write locks, these may
  // be implemented as synonyms to Lock() and Unlock().  So you can use
  // these for efficiency, but don't use them anyplace where being able
  // to do shared reads is necessary to avoid deadlock.
  inline void ReaderLock();   // Block until free or shared then acquire a share
  inline void ReaderUnlock(); // Release a read share of this Mutex
  inline void WriterLock() { Lock(); }     // Acquire an exclusive lock
  inline void WriterUnlock() { Unlock(); } // Release a lock from WriterLock()

  inline void LockWhen(Condition cond)            { Lock(); WaitLoop(cond); }
  inline void ReaderLockWhen(Condition cond)      { Lock(); WaitLoop(cond); }
  inline void Await(Condition cond)               { WaitLoop(cond); }

  bool ReaderLockWhenWithTimeout(Condition cond, int millis)
    { Lock(); return WaitLoopWithTimeout(cond, millis); }
  bool LockWhenWithTimeout(Condition cond, int millis)
    { Lock(); return WaitLoopWithTimeout(cond, millis); }
  bool AwaitWithTimeout(Condition cond, int millis)
    { return WaitLoopWithTimeout(cond, millis); }

 private:
    void WaitLoop(Condition cond) {
    signal_at_unlock_ = true;
    while(cond.Eval() == false) {
      pthread_cond_wait(&cv_, &mu_);
    }
    ANNOTATE_HAPPENS_AFTER(this);
  }

  bool WaitLoopWithTimeout(Condition cond, int millis) {
    struct timeval now;
    struct timespec timeout;
    int retcode = 0;
    gettimeofday(&now, NULL);
    timeval2timespec(&now, &timeout, millis);

    signal_at_unlock_ = true;

    while (cond.Eval() == false && retcode == 0) {
      retcode = pthread_cond_timedwait(&cv_, &mu_, &timeout);
    }
    if(retcode == 0) {
      ANNOTATE_HAPPENS_AFTER(this);
    }
    return cond.Eval();
  }

  pthread_mutex_t mu_;

  pthread_cond_t  cv_;
  bool signal_at_unlock_;  // Set to true if Wait was called.

  // We want to make sure that the compiler sets is_safe_ to true only
  // when we tell it to, and never makes assumptions is_safe_ is
  // always true.  volatile is the most reliable way to do that.
  volatile bool is_safe_;
  // This indicates which constructor was called.
  bool destroy_;

  inline void SetIsSafe() { is_safe_ = true; }

  DISALLOW_COPY_AND_ASSIGN(Mutex);
};

#define SAFE_PTHREAD(fncall)  do {   /* run fncall if is_safe_ is true */  \
  if (is_safe_ && fncall(&mu_) != 0) abort();                           \
} while (0)

Mutex::Mutex() : destroy_(true) {
  SetIsSafe();
  if (is_safe_) {
    CHECK(0 == pthread_mutex_init(&mu_, NULL));
    CHECK(0 == pthread_cond_init(&cv_, NULL));
  }
  signal_at_unlock_ = false;
}
Mutex::Mutex(Mutex::LinkerInitialized) : destroy_(false) {
  SetIsSafe();
  if (is_safe_) {
    CHECK(0 == pthread_mutex_init(&mu_, NULL));
    CHECK(0 == pthread_cond_init(&cv_, NULL));
  }
  signal_at_unlock_ = false;
}
Mutex::~Mutex() {
  if (destroy_) {
    SAFE_PTHREAD(pthread_mutex_destroy);
    CHECK(0 == pthread_cond_destroy(&cv_));
  }
}
void Mutex::Lock() {
  SAFE_PTHREAD(pthread_mutex_lock);
}
void Mutex::Unlock() {
  ANNOTATE_HAPPENS_BEFORE(this);
  if (signal_at_unlock_) {
    CHECK(0 == pthread_cond_signal(&cv_));
  }
  SAFE_PTHREAD(pthread_mutex_unlock);
}
bool Mutex::TryLock()      { return is_safe_ ?
                             pthread_mutex_trylock(&mu_) == 0 : true; }
void Mutex::ReaderLock()   { Lock(); }
void Mutex::ReaderUnlock() { Unlock(); }
#undef SAFE_PTHREAD

// --------------------------------------------------------------------------
// Some helper classes

// MutexLock(mu) acquires mu when constructed and releases it when destroyed.
class MutexLock {
 public:
  explicit MutexLock(Mutex *mu) : mu_(mu) { mu_->Lock(); }
  ~MutexLock() { mu_->Unlock(); }
 private:
  Mutex * const mu_;
  // Disallow "evil" constructors
  MutexLock(const MutexLock&);
  void operator=(const MutexLock&);
};

// ReaderMutexLock and WriterMutexLock do the same, for rwlocks
class ReaderMutexLock {
 public:
  explicit ReaderMutexLock(Mutex *mu) : mu_(mu) { mu_->ReaderLock(); }
  ~ReaderMutexLock() { mu_->ReaderUnlock(); }
 private:
  Mutex * const mu_;
  // Disallow "evil" constructors
  ReaderMutexLock(const ReaderMutexLock&);
  void operator=(const ReaderMutexLock&);
};

class WriterMutexLock {
 public:
  explicit WriterMutexLock(Mutex *mu) : mu_(mu) { mu_->WriterLock(); }
  ~WriterMutexLock() { mu_->WriterUnlock(); }
 private:
  Mutex * const mu_;
  // Disallow "evil" constructors
  WriterMutexLock(const WriterMutexLock&);
  void operator=(const WriterMutexLock&);
};

// Catch bug where variable name is omitted, e.g. MutexLock (&mu);
#define MutexLock(x) COMPILE_ASSERT(0, mutex_lock_decl_missing_var_name)
#define ReaderMutexLock(x) COMPILE_ASSERT(0, rmutex_lock_decl_missing_var_name)
#define WriterMutexLock(x) COMPILE_ASSERT(0, wmutex_lock_decl_missing_var_name)

class BlockingCounter {
 public:
  explicit BlockingCounter(int initial_count) :
    count_(initial_count) {}
  bool DecrementCount() {
    MutexLock lock(&mu_);
    count_--;
    return count_ == 0;
  }
  void Wait() {
    mu_.LockWhen(Condition(&IsZero, &count_));
    mu_.Unlock();
  }
 private:
  static bool IsZero(int *arg) { return *arg == 0; }
  Mutex mu_;
  int count_;
};

class SpinLock {
 public:
  SpinLock() {
    CHECK(0 == pthread_spin_init(&mu_, 0));
  }
  ~SpinLock() {
    CHECK(0 == pthread_spin_destroy(&mu_));
  }
  void Lock() {
    CHECK(0 == pthread_spin_lock(&mu_));
  }
  void Unlock() {
    CHECK(0 == pthread_spin_unlock(&mu_));
  }
 private:
  pthread_spinlock_t mu_;
};

/// Wrapper for pthread_cond_t.
class CondVar {
 public:
  CondVar()   { CHECK(0 == pthread_cond_init(&cv_, NULL)); }
  ~CondVar()  { CHECK(0 == pthread_cond_destroy(&cv_)); }
  void Wait(Mutex *mu) { CHECK(0 == pthread_cond_wait(&cv_, &mu->mu_)); }
  bool WaitWithTimeout(Mutex *mu, int millis) {
    struct timeval now;
    struct timespec timeout;
    gettimeofday(&now, NULL);
    timeval2timespec(&now, &timeout, millis);
    return 0 != pthread_cond_timedwait(&cv_, &mu->mu_, &timeout);
  }
  void Signal() { CHECK(0 == pthread_cond_signal(&cv_)); }
  void SignalAll() { CHECK(0 == pthread_cond_broadcast(&cv_)); }
 private:
  pthread_cond_t cv_;
};

}  // namespace base

#endif  // #define BASE_MUTEX_H__
