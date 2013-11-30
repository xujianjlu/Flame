#!/usr/bin/python


import os.path

BUILD_NAME = 'BUILD'
BUILD_OUT = '.flame-out'
LOCAL_BUILD_DIR = '/usr/local/build'
MAIN_LIB = 'libs/flame/libmain.a'

CPP_BLD_ENV_IN = 'flame/utils/building_env.h.in'
CPP_BLD_ENV_OUT = 'util/global_init/building_env.h'
CPP_UNITTEST_SCRIPT = 'flame/utils/execute_unittest.sh'
CPP_PPROF_LIB_PATH = 'libs/third_party/pprof/libtcmalloc_and_profiler.a'

#DISTCC_HOSTS = 'flame/distcc/distcc_hosts.txt'
#DISTCC_BIN = 'flame/distcc/distcc'

# Since currently thrift supposes all php related files under the same folder,
# we hard-code the static files directory here and will copy them to the
# scons out folder at deploy time
PY_THRIFT_DIR = 'third_party/thrift/py/src/'

PROTO_BIN = 'third_party/protobuf/bin/protoc'
PROTO_OUT = 'proto-out'
PROTO_INC = 'third_party/protobuf/'
PROTO_PY_INC = 'third_party/protobuf/python'

STATIC_LIB_PATH = 'libs/'
STATIC_LIB_PREFIX = '//%s' % STATIC_LIB_PATH
BUILD_FILE_PATH = 'libs/flame/'
BUILD_FILE_PREFIX = '//%s' % BUILD_FILE_PATH

THRIFT_BIN = 'third_party/thrift/bin/thrift'
THRIFT_OUT = 'thrift-out'
THRIFT_INC = 'third_party/thrift/include'

CUDA_BIN_DIR = 'third_party/cuda/bin/'
CUDA_NVCC_BIN = 'third_party/cuda/bin/nvcc'
CUDA_INC = 'third_party/cuda/include'
CUDA_SDK_COMMON_INC = 'third_party/cuda/sdk/common/include'
CUDA_SDK_SHARED_INC = 'third_party/cuda/sdk/shared/include'
CUDA_SHRUTIL_LIB = 'libs/third_party/cuda/sdk/shared/libshrutil_x86_64.a'
CUDA_UTIL_LIB = 'libs/third_party/cuda/sdk/lib/libcutil_x86_64.a'
CUDA_RT_LIB = 'libs/third_party/cuda/lib/libcudart.so'
CUDA_FFT_LIB = 'libs/third_party/cuda/lib/libcufft.so'

BISON_DIR = 'third_party/bison'
BISON_BIN = 'third_party/bison/bin/bison'
BISON_OUT = 'bison-out'

PYINSTALLER_CONFIURE = '//third_party/pyinstaller/Configure.py'
PYINSTALLER_CONF_FILE = 'third_party/pyinstaller/config.dat'
PYINSTALLER_MAKER = 'third_party/pyinstaller/Makespec.py'
PYINSTALLER_BUILDER = 'third_party/pyinstaller/Build.py'

SBT_BIN_PATH = 'flame/sbt/sbtnocolors'
SBT_CLEAN_ACTION = '"set logLevel := Level.Error" clean-files'
SBT_LIB_JAR_BUILD_ACTION = '"set logLevel := Level.Error" update package'
SBT_BIN_JAR_BUILD_ACTION = '"set logLevel := Level.Error" update "set test in AssemblyKeys.assembly := {}" assembly'
SBT_WAR_BUILD_ACTION = '"set logLevel := Level.Error" update package'

# ANDROID_UPDATE_CMD = 'android/third_party/androidsdk/android-sdk-linux/tools/android'
# ANDROID_COMPILER = 'android/third_party/androidsdk/apache-ant-1.8.2/bin/ant'
# ANDROID_SDK_PATH = 'android/third_party/androidsdk/android-sdk-linux/'
# ANDROID_TEST = 'android/tools/android_test.py'
# ANDROID_DISTRIBUTE = 'android/tools/distribute/distribute.sh'
# ANDROID_DISTRIBUTE_CONFIG = 'android/tools/distribute/config.txt'
# ANDROID_LIBS = 'android/third_party/libs'

# FRONTEND_OUT = 'frontend'
# THRIFT_PHP_OUT = FRONTEND_OUT + '/php/thrift-out';
# CLOSURE_PATH = 'frontend/third_party/closure-library'
# JAVASCRIPT_BUILDER_PATH = '%s/closure/bin/build' % CLOSURE_PATH
# JAVASCRIPT_BUILDER = os.path.join(JAVASCRIPT_BUILDER_PATH, 'closurebuilder.py')
# JAVASCRIPT_DEPSWRITER = os.path.join(JAVASCRIPT_BUILDER_PATH, 'depswriter.py')
# JAVASCRIPT_COMPILER = 'frontend/tools/jsmodule.py -c frontend/third_party/closure-compiler/compiler.jar'
# CSS_COMPILER = 'frontend/third_party/yui-library/yuicompressor.jar'
# CSS_COMPILER_HELPER = 'frontend/tools/csscompiler.py -c ' + CSS_COMPILER
# SOY_COMPILER = 'frontend/third_party/soy/SoyToJsSrcCompiler.jar'
# MODULE_DIR = '.module_dir'
# MODULE_RESULTS_DIR = 'js_compiled'

#SCALAC_NAME = 'scalac'
#SCALAC = os.path.join('third_party/scala/bin', SCALAC_NAME)

#PHP_THRIFT_DIR = 'third_party/thrift/php/src/'
