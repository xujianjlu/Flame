// Copyright 2013 Jike Inc. All Rights Reserved.
// Author: Liqiang Guo(guoliqiang@jike.com)
// I just want to GH to hss~
// Date  : 2013-04-06 00:42:53
// File  : define.h
// Brief :

#ifndef  BASE_PUBLIC_DEFINE_H_
#define  BASE_PUBLIC_DEFINE_H_
#include <stdlib.h>
#include <string>
#include <iostream>   // NOLINT
#define DISABLE_ASSIGN_COPY(name)\
       void operator = (const name &);\
       name(const name &);
/*
#define CHECK(condition) if (!(condition)) {\
          std::cout<< "condition is false" << std::endl;\
          exit(0);\
        }

#define CHECK_EQ(a, b) if ((a) != (b)) { \
         std::cout<< a << " is not equal with " << b\
                  << std::endl;\
         exit(0);\
       }
*/
#endif  // BASE_PUBLIC_DEFINE_H_
