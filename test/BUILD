cc_binary(name = 'test_cpp',
          srcs = ['test_cpp.cc'],
          deps = [':test_fun']
         )

cc_binary(name = 'test_gflags',
          srcs = ['test_gflags.cc'],
          deps = ['//libs/gflags:gflags']
         )

cc_library(name = 'test_fun',
           srcs = ['test_fun.cc'],
           deps = []
          )

