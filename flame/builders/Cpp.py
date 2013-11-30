#!/usr/bin/env python2.6


import sys
sys.path.append('flame/utils')

from Access import AccessChecker
from LanguageBuilder import LanguageBuilder
from LanguageBuilder import RegisterObj
from SCons.Script import ARGUMENTS
from SCons.Script import Action
from SCons.Script import Builder
from datetime import datetime

import commands
import os
import socket

import Flags
import Path
import Util
import cpplint


"""Cpp build registerers"""
def _cc_internal(name, srcs, deps, data, copt, libs,
                 cflags, link_flags, build_type):
  opt = {}
  if copt != None and len(copt) > 0:
    opt['copt'] = copt
  if data != None and len(data) > 0:
    opt['data'] = data
  if libs != None and len(libs) > 0:
    opt['libs'] = libs
  if cflags != None and len(cflags) > 0:
    opt['cflags'] = cflags
  if link_flags != None and len(link_flags) > 0:
    opt['link_flags'] = link_flags
  RegisterObj(name, srcs, deps, opt, build_type)


def cc_library(name = None, srcs = [], deps = [], data = [], copt = [],
               libs = [], cflags = [], link_flags = []):
  _cc_internal(name, srcs, deps, data, copt,
               libs, cflags, link_flags, 'cc_library')


def cc_binary(name = None, srcs = [], deps = [],
              data = [], copt = [], libs = [], cflags = [], link_flags = []):
  _cc_internal(name, srcs, deps, data, copt, libs,
               cflags, link_flags, 'cc_binary')


def cc_test(name = None, srcs = [], deps = [], data = [],
            copt = [], libs = [], cflags = [], link_flags = []):
  _cc_internal(name, srcs, deps, data, copt, libs,
               cflags, link_flags, 'cc_test')


def cc_benchmark(name = None, srcs = [], deps = [],
                 data = [], copt = [], libs = [], cflags = [], link_flags = []):
  _cc_internal(name, srcs, deps, data, copt, libs,
               cflags, link_flags, 'cc_benchmark')


def CheckSpecialDependency(obj):
  obj.has_thrift_dep = obj.name_.endswith('_thrift')
  obj.has_proto_dep = obj.name_.endswith('_proto')
  obj.has_cuda_dep = obj.name_.endswith('_cuda')
  obj.has_bison_dep = obj.name_.endswith('_bison')
  for d in obj.depends_:
    if d.endswith('_thrift'):
      obj.has_thrift_dep = True
    elif d.endswith('_proto'):
      obj.has_proto_dep = True
    elif d.endswith('_cuda'):
      obj.has_cuda_dep = True
    elif d.endswith('_bison'):
      obj.has_bison_dep = True

def GetCppInclude(obj):
  result = ['.', Path.GetOutputDir(), Path.GetGlobalDir()]
  if not hasattr(obj, 'has_proto_dep'):
    CheckSpecialDependency(obj)
  if obj.has_thrift_dep:
    result.append(Path.GetAbsPath(Flags.THRIFT_INC))
    result.append(Path.GetThriftOutPath())
    result.append(Path.GetAbsPath('third_party/boost'))
    result.append(Path.GetAbsPath('third_party/libevent'))
  if obj.has_proto_dep:
    result.append(Path.GetProtoOutPath())
    result.append(Path.GetAbsPath(Flags.PROTO_INC))
  if obj.has_cuda_dep:
    result.append(Flags.CUDA_INC)
    result.append(Flags.CUDA_SDK_COMMON_INC)
    result.append(Flags.CUDA_SDK_SHARED_INC)
  if obj.has_bison_dep:
    result.insert(0, Path.GetBisonOutPath())
  return result


class CppBuilder(LanguageBuilder):
  """C++ code builders"""
  def __init__(self):
    LanguageBuilder.__init__(self)
    self._is_svn_client = Path.IsSVNClient()
    self._is_git_client = Path.IsGITClient()
    cpplint._cpplint_state.ResetErrorCounts()
    self._opend_files = set()
    self._checked_dir = set()
    self._always_test = ARGUMENTS.get('always_test', 'on')
    self._build_mode = ARGUMENTS.get('c', 'dbg')
    self._check_lib_dep = ARGUMENTS.get('check_dep', 'on')
    self._check_style = ARGUMENTS.get('check_cpp_style', 'on')
    self._test_suffix = 'passed'
    self._access_checker = AccessChecker()
    self._lib_name_map = {}
    self._binaries = set()
    p = 'libs/gtest/lib%s.a'
    lib_base = self._GetStaticLib('//base:base', abort = False)
    if not lib_base:
      lib_base = self._GetLibName('//base:base')
    self._gtest_lib_source = [Path.GetAbsPath(x, abort = False) for x in
        (p % 'gtest_main', p % 'gmock', p % 'gtest')] + [lib_base]
    self._benchmark_lib_source = [Path.GetAbsPath(x, abort = False) for x in
        (p % 'benchmark_main', p % 'gtest')] + [lib_base]
    self._main_lib = [Path.GetAbsPath(Flags.MAIN_LIB, abort = False)]

  def _HasCopt(self, obj, opt):
    """Checks if an obj is specified one c/c++ option."""
    return obj.option_.has_key('copt') and opt in obj.option_['copt']

  def _GetGccVersion(self):
    #return commands.getoutput('gcc -dumpversion')
    return commands.getoutput('gcc --version')

  def GetBuildRegisterers(self):
    return ['cc_benchmark',
            'cc_binary',
            'cc_library',
            'cc_test']


  def RegisterSConsBuilders(self):
    return {'UnitTest' : Builder(action = Action('$CCTESTCOM', '$CCTESTCOMSTR'),
                                 suffix = self._test_suffix)
           }

  def _GetOpenedFiles(self, path):
    if self._check_style != 'on': return
    d = os.path.dirname(path)
    if d in self._checked_dir:
      return
    self._checked_dir.add(d)
    output = []
    if self._is_svn_client and not Path.IsInDir(d, Path.GetGlobalDir()):
      output = os.popen('svn st %s' % d).read().split('\n')
    elif self._is_git_client:
      output = os.popen('git status --porcelain %s' % d).read().split('\n')
    for f in output:
      seg = f.strip().split(' ')
      if seg[0] == 'D' or seg[0] == '!':
        continue
      f = seg[len(seg)-1]
      # not check style for third party code
      if (f.find('/third_party/') != -1 or
          f.find('/infrastructure/firewood/scrib/') != -1):
        continue
      if f.endswith('.h') or f.endswith('.cc') or f.endswith('.cpp'):
        self._opend_files.add(f)
    pass

  def _StyleCheck(self):
    # not check style for third party code
    for f in self._opend_files:
      cpplint.ProcessFile(f, cpplint._cpplint_state.verbose_level, False)
    if cpplint._cpplint_state.error_count > 0:
      print Util.BuildMessage(
          'There\'re %d style warnings in the opend files, '
          'please try fixing them before submit the code!' %
          cpplint._cpplint_state.error_count, 'WARNING')
    pass


  def _GenerateBuildingEnv(self, env):
    content = open(Path.GetAbsPath(Flags.CPP_BLD_ENV_IN)).read()
    content = content.replace('BD_TIME', 'UTC %s' % datetime.utcnow())
    content = content.replace('BD_HOST', socket.gethostname())
    cxx = env['CXX'].split('/')
    cxx.reverse()
    content = content.replace('BD_COM', '-'.join((cxx[0], env['CXXVERSION'])))
    content = content.replace('BD_MODE', self._build_mode)
    (sys, d1, release, d2, machine) = os.uname()
    content = content.replace('BD_PLATFORM', '-'.join((sys, release, machine)))
    base = ''
    rev = ''
    if self._is_svn_client:
      info = os.popen('svn info .').read().split('\n')
      for line in info:
        if line.startswith('URL'):
          base = line.split(': ')[1].strip()
        elif line.startswith('Revision:'):
          rev = line.split(':')[1].strip()
    content = content.replace('BD_SVN_BASE', base)
    content = content.replace('BD_SVN_REV', rev)
    # build binary map
    targets = ''
    for b in self._binaries:
      if len(targets) > 0: targets += ','
      targets += '%s:%s' % (os.path.basename(b), b)
    content = content.replace('BD_TARGET', targets)
    path = os.path.join(Path.GetOutputDir(), Flags.CPP_BLD_ENV_OUT)
    Util.MkDir(os.path.dirname(path))
    open(path, 'w').write(content)

  def GenerateEnv(self, env):
    env['LINK'] = 'g++'
    env['CCTESTCOM'] = ('bash %s $SOURCE $TARGET $CCTESTTIMEOUTFLAGS '
                        '$CCTESTHEAPCHECKFLAGS' % Flags.CPP_UNITTEST_SCRIPT)

    env['CUDA_LIB'] = str('%s %s %s %s' %
                          (Flags.CUDA_SHRUTIL_LIB,
                           Flags.CUDA_UTIL_LIB,
                           Flags.CUDA_FFT_LIB,
                           Flags.CUDA_RT_LIB))

    cc_flags = ('-m64 -fPIC -Wall -Werror -Wwrite-strings -Wno-sign-compare -g '
                '-Wuninitialized -Wno-error=deprecated-declarations ')
    # xujian: this is used to forbiden xcode warning.
    cc_flags += (' -Qunused-arguments ')
    # these is just for using proftools
    cc_flags += ('-fno-builtin-malloc -fno-builtin-free -fno-builtin-realloc '
                 '-fno-builtin-calloc -fno-builtin-cfree -fno-builtin-memalign '
                 '-fno-builtin-posix_memalign -fno-builtin-valloc '
                 '-fno-builtin-pvalloc -fno-omit-frame-pointer ')
    link_flags = ['-pthread -Qunused-arguments ']
    if self._GetGccVersion() >= '4.5':  # only available after gcc4.5
      link_flags.append('-static-libstdc++')
    else:
      cc_flags += '-fno-strict-aliasing '
    if self._build_mode != 'gprof':
        pass
    else:
      link_flags.append('-pg')
    env.Replace(LINKFLAGS = ' '.join(link_flags))
    if self._build_mode == 'dbg':
      env.Replace(CCFLAGS = ' '.join([cc_flags]))
    elif self._build_mode == 'gprof':
      env.Replace(CCFLAGS = ' '.join([cc_flags, '-pg -O2 -DNDEBUG']))
    elif self._build_mode == 'opt':
      env.Replace(CCFLAGS = ' '.join([cc_flags, '-O2 -DNDEBUG']))
    else:
      assert False, 'wrong build strategy: %s' % self._build_mode

  def _GetSourcePath(self, sources):
    result = []
    for x in sources:
      p = Path.GetAbsPath(x)
      if Path.IsInDir(p, Path.GetBaseDir()):
        result.append(Path.GetBuiltPath(x))
      else:
        result.append(p)
    return result

  def _GetLibPath(self, path):
    lib_name = 'lib' + os.path.basename(path) + '.a'
    return os.path.join(os.path.dirname(path), lib_name)

  def _GetLibName(self, name):
    try:
      lib_name = self._lib_name_map[name]
    except:
      build_name = Path.GetBuiltPath(name)
      lib_name = self._GetLibPath(build_name)
      self._lib_name_map[name] = lib_name
    return lib_name

  def _GetStaticLib(self, path, abort = True):
    p = os.path.join(Flags.STATIC_LIB_PATH, Path.GetRelativePath(path))
    return Path.GetAbsPath(self._GetLibPath(p), abort)

  def _GetLibNameForObj(self, obj):
    if obj.is_private_:
      return self._GetStaticLib(obj.name_)
    return self._GetLibName(obj.name_)

  def _GetFlags(self, obj, env):
    source = []
    always_link_libs = ''
    #libs = ['dl', 'rt', 'crypt']
    libs = ['dl']
    if 'libs' in obj.option_:
      libs += obj.option_['libs']
    path = []

    # check dependent obj's special attributes
    obj.has_thrift_dep = obj.name_.endswith('_thrift')
    obj.has_proto_dep = obj.name_.endswith('_proto')
    obj.has_cuda_dep = obj.name_.endswith('_cuda')
    obj.has_bison_dep = obj.name_.endswith('_bison')
    for d in obj.depends_:
      if d.endswith('_thrift'):
        obj.has_thrift_dep = True
      elif d.endswith('_proto'):
        obj.has_proto_dep = True
      elif d.endswith('_cuda'):
        obj.has_cuda_dep = True
      elif d.endswith('_bison'):
        obj.has_bison_dep = True
      try:
        dep_obj = self.build_manager_.GetObjByName(d)
      except:
        if Path.IsStaticLib(d):
          d = d.replace(':', ':lib') + '.a'
          source.append(Path.GetAbsPath(d))
          continue
      d_lib = self._GetLibNameForObj(dep_obj)
      if self._HasCopt(dep_obj, 'always_link'):
        always_link_libs += ' %s' % d_lib

        # add explicit dependency since Scons could not figure out such dep
        # relationship for always link lib
        if obj.build_type_ in ['cc_test', 'cc_benchmark', 'cc_binary']:
          obj_name = Path.GetBuiltPath(obj.name_)
        elif (obj.build_type_ in ['cc_library']):
          obj_name = self._GetLibName(obj.name_)
        env.Depends(obj_name, d_lib)
      else:
        source.append(d_lib)

    # detect thrift / proto dependency
    if obj.has_thrift_dep:
      libs += ['thriftnb', 'thriftz', 'thrift', 'event']
      path.append(Path.GetAbsPath('libs/third_party/thrift'))
      path.append(Path.GetAbsPath('libs/third_party/libevent'))
    if obj.has_proto_dep:
      libs += ['protobuf']
      path.append(Path.GetAbsPath('libs/third_party/protobuf'))

    # for gtest
    if obj.build_type_ == 'cc_test':
      source += self._gtest_lib_source
    if obj.build_type_ == 'cc_benchmark':
      source += self._benchmark_lib_source

    link_flags = env['LINKFLAGS']
    if len(always_link_libs) > 0:
      link_flags += (' -Wl,--whole-archive%s -Wl,--no-whole-archive' %
                     always_link_libs)
    if 'link_flags' in obj.option_:
      link_flags += ' '
      link_flags += ' '.join(obj.option_['link_flags'])
    # add cuda .so to the tail fo source
    if obj.has_cuda_dep:
      cuda_lib_list = env['CUDA_LIB'].split()
      source += cuda_lib_list
    return source, libs, path, link_flags

  def BuildObject(self, env, obj):
    self._GetOpenedFiles(obj.path_)
    # convert to SCons dendency graph
    target = Path.GetBuiltPath(obj.name_)
    source = self._GetSourcePath(obj.sources_)
    relative_source = [Path.GetRelativePath(x) for x in obj.sources_]
    cpp_path = GetCppInclude(obj)
    lib_sources, libs, libpath, link_flags = self._GetFlags(obj, env)
    cc_flags = env['CCFLAGS']
    if 'cflags' in obj.option_:
      cc_flags += ' '
      cc_flags += ' '.join(obj.option_['cflags'])

    if obj.has_thrift_dep and self._GetGccVersion() >= '4.6':
      cc_flags += ' -Wno-return-type '

    CXX_value = env['CXX']

    if obj.build_type_ in ['cc_binary', 'cc_test', 'cc_benchmark']:
      if obj.build_type_ == 'cc_binary':
        self._binaries.add(Path.GetRelativePath(obj.name_))
      binary = env.Program(target = target,
                           source = source + lib_sources,
                           LIBS = libs,
                           LIBPATH = libpath,
                           CPPPATH = cpp_path,
                           LINKFLAGS = link_flags,
                           CCFLAGS = cc_flags,
                           CXX = CXX_value)
      if (obj.build_type_ == 'cc_test' and
          obj.name_ in self.build_manager_.GetTestTargets()):
        heapcheck_str = 'on'
        if self._HasCopt(obj, 'disable_heap_check'):
          print Util.BuildMessage('Not do heap check for %s' % obj.name_,
                                  'WARNING')
          heapcheck_str = ''
        timeout = 30
        if self._HasCopt(obj, 'large_test'):
          timeout = 300
        if self._always_test == 'on':
          os.system('rm -rf %s.%s' % (binary[0], self._test_suffix))
        env.UnitTest(binary,
                     CCTESTHEAPCHECKFLAGS = heapcheck_str,
                     CCTESTTIMEOUTFLAGS = '%d' % timeout)
    elif obj.build_type_ in ['cc_library']:
      result = env.StaticLibrary(target = target,
                                 source = source,
                                 CPPPATH = cpp_path,
                                 CCFLAGS = cc_flags,
                                 CXX = CXX_value)
      if (not self._HasCopt(obj, 'disable_dep_check') and
          self._check_lib_dep == 'on'):
        # add a dummy binary for dependency check,
        # to avoid missing dependency declaration in the cc_library
        dummy_target = target + '_dep_check_dummy'
        link_flags = link_flags.replace(self._pprof_link_flags, '')
        env.Program(target = dummy_target,
                    source = self._main_lib + lib_sources,
                    LIBS = libs,
                    LIBPATH = libpath,
                    LINKFLAGS = link_flags)
        env.Depends(dummy_target,
                    self._GetLibName(obj.name_))

  def Finish(self, env):
    self._StyleCheck()
    self._GenerateBuildingEnv(env)
