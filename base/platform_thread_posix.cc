// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "base/platform_thread.h"

#include <errno.h>
#include <sched.h>

#include "base/lazy_instance.h"
#include "base/logging.h"
#include "base/scoped_ptr.h"
#include "base/safe_strerror_posix.h"
#include "base/thread_local.h"
#include "base/thread_restrictions.h"

#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <unistd.h>



namespace base {


namespace {

LazyInstance<ThreadLocalPointer<char> >::Leaky
    current_thread_name = LAZY_INSTANCE_INITIALIZER;

struct ThreadParams {
  PlatformThread::Delegate* delegate;
  bool joinable;
};

void* ThreadFunc(void* params) {
  ThreadParams* thread_params = static_cast<ThreadParams*>(params);
  PlatformThread::Delegate* delegate = thread_params->delegate;
  if (!thread_params->joinable)
    base::ThreadRestrictions::SetSingletonAllowed(false);
  delete thread_params;
  delegate->ThreadMain();
  return NULL;
}

bool CreateThread(size_t stack_size, bool joinable,
                  PlatformThread::Delegate* delegate,
                  PlatformThreadHandle* thread_handle,
                  ThreadPriority priority) {

  bool success = false;
  pthread_attr_t attributes;
  pthread_attr_init(&attributes);

  // Pthreads are joinable by default, so only specify the detached attribute if
  // the thread should be non-joinable.
  if (!joinable) {
    pthread_attr_setdetachstate(&attributes, PTHREAD_CREATE_DETACHED);
  }


  if (stack_size > 0)
    pthread_attr_setstacksize(&attributes, stack_size);

  ThreadParams* params = new ThreadParams;
  params->delegate = delegate;
  params->joinable = joinable;
  success = !pthread_create(thread_handle, &attributes, ThreadFunc, params);

  if (priority != kThreadPriority_Normal) {
    if (priority == kThreadPriority_RealtimeAudio) {
      // Linux isn't posix compliant with setpriority(2), it will set a thread
      // priority if it is passed a tid, not affecting the rest of the threads
      // in the process.  Setting this priority will only succeed if the user
      // has been granted permission to adjust nice values on the system.
      const int kNiceSetting = -10;
      if (setpriority(PRIO_PROCESS, PlatformThread::CurrentId(), kNiceSetting))
        VLOG(1) << "Failed to set nice value of thread to " << kNiceSetting;
    } else {
      NOTREACHED() << "Unknown thread priority.";
    }
  }

  pthread_attr_destroy(&attributes);
  if (!success)
    delete params;
  return success;
}

}  // namespace

// static
PlatformThreadId PlatformThread::CurrentId() {
  // Pthreads doesn't have the concept of a thread ID, so we have to reach down
  // into the kernel.
  return syscall(__NR_gettid);
}

// static
void PlatformThread::YieldCurrentThread() {
  sched_yield();
}

// static
void PlatformThread::Sleep(int duration_ms) {
  // NOTE: This function will be supplanted by the other version of Sleep
  // in the future.  See issue 108171 for more information.
  Sleep(TimeDelta::FromMilliseconds(duration_ms));
}

// static
void PlatformThread::Sleep(TimeDelta duration) {
  struct timespec sleep_time, remaining;

  // Break the duration into seconds and nanoseconds.
  // NOTE: TimeDelta's microseconds are int64s while timespec's
  // nanoseconds are longs, so this unpacking must prevent overflow.
  sleep_time.tv_sec = duration.InSeconds();
  duration -= TimeDelta::FromSeconds(sleep_time.tv_sec);
  sleep_time.tv_nsec = duration.InMicroseconds() * 1000;  // nanoseconds

  while (nanosleep(&sleep_time, &remaining) == -1 && errno == EINTR)
    sleep_time = remaining;
}

// static
void PlatformThread::SetName(const char* name) {
  // have to cast away const because ThreadLocalPointer does not support const
  // void*
  current_thread_name.Pointer()->Set(const_cast<char*>(name));

  // tracked_objects::ThreadData::InitializeThreadContext(name);

  // On linux we can get the thread names to show up in the debugger by setting
  // the process name for the LWP.  We don't want to do this for the main
  // thread because that would rename the process, causing tools like killall
  // to stop working.
  if (PlatformThread::CurrentId() == getpid())
    return;

  // http://0pointer.de/blog/projects/name-your-threads.html
  // Set the name for the LWP (which gets truncated to 15 characters).
  // Note that glibc also has a 'pthread_setname_np' api, but it may not be
  // available everywhere and it's only benefit over using prctl directly is
  // that it can set the name of threads other than the current thread.
  int err = prctl(PR_SET_NAME, name);
  // We expect EPERM failures in sandboxed processes, just ignore those.
  if (err < 0 && errno != EPERM)
    DPLOG(ERROR) << "prctl(PR_SET_NAME)";
}


// static
bool PlatformThread::Create(size_t stack_size, Delegate* delegate,
                            PlatformThreadHandle* thread_handle) {
  return CreateThread(stack_size, true /* joinable thread */,
                      delegate, thread_handle, kThreadPriority_Normal);
}

// static
bool PlatformThread::CreateWithPriority(size_t stack_size, Delegate* delegate,
                                        PlatformThreadHandle* thread_handle,
                                        ThreadPriority priority) {
  return CreateThread(stack_size, true,  // joinable thread
                      delegate, thread_handle, priority);
}

// static
bool PlatformThread::CreateNonJoinable(size_t stack_size, Delegate* delegate) {
  PlatformThreadHandle unused;

  bool result = CreateThread(stack_size, false /* non-joinable thread */,
                             delegate, &unused, kThreadPriority_Normal);
  return result;
}

// static
void PlatformThread::Join(PlatformThreadHandle thread_handle) {
  // Joining another thread may block the current thread for a long time, since
  // the thread referred to by |thread_handle| may still be running long-lived /
  // blocking tasks.
  base::ThreadRestrictions::AssertIOAllowed();
  pthread_join(thread_handle, NULL);
}

}  // namespace base
