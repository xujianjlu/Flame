cc_binary(name = 'test_cpp',
          srcs = ['test_cpp.cc'],
          deps = [':test_fun']
         )

# this gflags is variant of google gflags.
# it used in Chromium project.
cc_binary(name = 'test_gflags',
          srcs = ['test_gflags.cc'],
          deps = ['//base:base']
         )

# this glog is variant of google glog,
# the log level info is added into log output,
# it used in Chromium project.
# and I have changed the the output formate to
# '[levle][pid/tid][timeinfo][file(linenumber)] your log output'
cc_binary(name = 'test_glog',
          srcs = ['test_glog.cc'],
          deps = ['//base:base']
         )

cc_library(name = 'test_fun',
           srcs = ['test_fun.cc'],
           deps = []
          )

cc_binary(name = 'test_proto_cpp',
          srcs = ['test_proto.cc'
                 ],
          deps = ['//base:base',
                  '//examples/proto:test_proto'
                 ]
             )
