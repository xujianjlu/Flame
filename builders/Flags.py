#!/usr/bin/python


import os.path

BUILD_NAME = 'BUILD'
BUILD_OUT = '.flame-out'
LOCAL_BUILD_DIR = '/tmp/build'
MAIN_LIB = 'libs/flame/libmain.a'

CPP_BLD_ENV_IN = 'flame/utils/building_env.h.in'
CPP_BLD_ENV_OUT = 'utils/cpp/global_init/building_env.h'
CPP_UNITTEST_SCRIPT = 'flame/utils/execute_unittest.sh'
CPP_PPROF_LIB_PATH = 'thirdparty/gprofiler/lib/'

#DISTCC_HOSTS = 'flame/distcc/distcc_hosts.txt'
#DISTCC_BIN = 'flame/distcc/distcc'

#PROTO_BIN = 'libs/proto/bin/protoc'
PROTO_OUT = 'proto-out'
PROTO_BIN = 'thirdparty/protobuf-2.4/bin/protoc'
PROTO_INC = 'thirdparty/protobuf-2.4/include/'
PROTO_LIB = 'thirdparty/protobuf-2.4/lib'
PROTO_PY_INC = 'thirdparty/protobuf-2.4/pyinclude/'
# PROTO_GOOGLE_API_INC = 'thirdparty/protobuf/cppinclude/'

# gRPC include path
GRPC_INC = 'thirdparty/grpc/include/'
GRPC_PLUGIN_CPP = 'thirdparty/grpc/bins/opt/grpc_cpp_plugin'

IDICT_INC = "thirdparty/idict/include/"

STATIC_LIB_PATH = 'thirdparty/'
STATIC_LIB_PREFIX = '//%s' % STATIC_LIB_PATH
BUILD_FILE_PATH = 'thirdparty/'
BUILD_FILE_PREFIX = '//%s' % BUILD_FILE_PATH

THRIFT_BIN = 'thirdparty/thrift/bin/thrift'
THRIFT_OUT = 'thrift-out'
THRIFT_INC = 'thirdparty/thrift/include'

# Since currently thrift supposes all php related files under the same folder,
# we hard-code the static files directory here and will copy them to the
# scons out folder at deploy time
PY_THRIFT_DIR = 'thirdparty/thrift/py/src/'

CUDA_BIN_DIR = 'thirdparty/cuda/bin/'
CUDA_NVCC_BIN = 'thirdparty/cuda/bin/nvcc'
CUDA_INC = 'thirdparty/cuda/include'
CUDA_SDK_COMMON_INC = 'thirdparty/cuda/sdk/common/include'
CUDA_SDK_SHARED_INC = 'thirdparty/cuda/sdk/shared/include'
CUDA_SHRUTIL_LIB = 'libs/thirdparty/cuda/sdk/shared/libshrutil_x86_64.a'
CUDA_UTIL_LIB = 'libs/thirdparty/cuda/sdk/lib/libcutil_x86_64.a'
CUDA_RT_LIB = 'libs/thirdparty/cuda/lib/libcudart.so'
CUDA_FFT_LIB = 'libs/thirdparty/cuda/lib/libcufft.so'

BISON_DIR = 'thirdparty/bison'
BISON_BIN = 'thirdparty/bison/bin/bison'
BISON_OUT = 'bison-out'

PYINSTALLER_CONFIURE = '//thirdparty/pyinstaller/configure.py'
PYINSTALLER_CONF_FILE = 'thirdparty/pyinstaller/config.dat'
PYINSTALLER_MAKER = 'thirdparty/pyinstaller/makespec.py'
PYINSTALLER_BUILDER = 'thirdparty/pyinstaller/build.py'

SBT_BIN_PATH = 'flame/sbt/sbtnocolors'
SBT_CLEAN_ACTION = '"set logLevel := Level.Error" clean-files'
SBT_LIB_JAR_BUILD_ACTION = '"set logLevel := Level.Error" update package'
SBT_BIN_JAR_BUILD_ACTION = '"set logLevel := Level.Error" update "set test in AssemblyKeys.assembly := {}" assembly'
SBT_WAR_BUILD_ACTION = '"set logLevel := Level.Error" update package'

# ANDROID_UPDATE_CMD = 'android/thirdparty/androidsdk/android-sdk-linux/tools/android'
# ANDROID_COMPILER = 'android/thirdparty/androidsdk/apache-ant-1.8.2/bin/ant'
# ANDROID_SDK_PATH = 'android/thirdparty/androidsdk/android-sdk-linux/'
# ANDROID_TEST = 'android/tools/android_test.py'
# ANDROID_DISTRIBUTE = 'android/tools/distribute/distribute.sh'
# ANDROID_DISTRIBUTE_CONFIG = 'android/tools/distribute/config.txt'
# ANDROID_LIBS = 'android/thirdparty/libs'

# FRONTEND_OUT = 'frontend'
# THRIFT_PHP_OUT = FRONTEND_OUT + '/php/thrift-out';
# CLOSURE_PATH = 'frontend/thirdparty/closure-library'
# JAVASCRIPT_BUILDER_PATH = '%s/closure/bin/build' % CLOSURE_PATH
# JAVASCRIPT_BUILDER = os.path.join(JAVASCRIPT_BUILDER_PATH, 'closurebuilder.py')
# JAVASCRIPT_DEPSWRITER = os.path.join(JAVASCRIPT_BUILDER_PATH, 'depswriter.py')
# JAVASCRIPT_COMPILER = 'frontend/tools/jsmodule.py -c frontend/thirdparty/closure-compiler/compiler.jar'
# CSS_COMPILER = 'frontend/thirdparty/yui-library/yuicompressor.jar'
# CSS_COMPILER_HELPER = 'frontend/tools/csscompiler.py -c ' + CSS_COMPILER
# SOY_COMPILER = 'frontend/thirdparty/soy/SoyToJsSrcCompiler.jar'
# MODULE_DIR = '.module_dir'
# MODULE_RESULTS_DIR = 'js_compiled'

#SCALAC_NAME = 'scalac'
#SCALAC = os.path.join('thirdparty/scala/bin', SCALAC_NAME)

#PHP_THRIFT_DIR = 'thirdparty/thrift/php/src/'
