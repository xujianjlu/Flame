#!/usr/bin/env python


from LanguageBuilder import LanguageBuilder
from LanguageBuilder import RegisterObj
from SCons.Script import Action
from SCons.Script import Builder

import os

import Cpp
import Flags
import Path
import SCons.Util
import Util

def thrift_library(name = None, srcs = [], deps = [],
                   gen_cpp = '', gen_php = '', gen_py = ''):
  if not name.endswith('_thrift'):
    Util.Abort('thrift lib\'s name should ends with "_thirft": %s' % name)
  if len(srcs) != 1 or not srcs[0].endswith('.thrift'):
    Util.Abort('thrift src should be only one .thrift file: %s' % str(srcs))
  opt = {'gen_cpp':False, 'gen_php':False, 'gen_py':False}
  if str(gen_cpp) == '1':
    opt['gen_cpp'] = True
  if str(gen_php) == '1':
    opt['gen_php'] = True
  if str(gen_py) == '1':
    opt['gen_py'] = True
  RegisterObj(name, srcs, deps, opt, 'thrift_library')


def _GetServiceNames(file_path):
  r = Util.MatchOnePattern(file_path,
      r'^service\s+(\S+)(\s+extends\s+\S+)?\s+({)?(\s*})?$')
  return r


def _thrift_cpp_emitter(target, source, env):
  rel_path = Path.GetRelativePath(str(source[0]))
  path = os.path.join(Path.GetThriftOutPath(),
                      os.path.dirname(rel_path),
                      'gen-cpp',
                      os.path.basename(rel_path))
  prefix = path.replace('.thrift', '')
  target.append(prefix + '_types.cpp')
  target.append(prefix + '_types.h')
  target.append(prefix + '_constants.cpp')
  target.append(prefix + '_constants.h')
  path = os.path.dirname(prefix)
  for service_name in _GetServiceNames(str(source[0])):
    target.append(path + '/' + service_name + '.cpp')
    target.append(path + '/' + service_name + '.h')
  return target, source


def _thrift_php_emitter(target, source, env):
  name = os.path.basename(str(source[0])).replace('.thrift', '')
  path = os.path.join(env['THRIFTPHPOUTDIR'], 'packages')
  path = os.path.join(path, name)
  target.append(os.path.join(path, name + '_types.php'))
  for service_name in _GetServiceNames(str(source[0])):
    target.append(os.path.join(path, service_name + '.php'))
  return target, source

def _thrift_py_emitter(target, source, env):
  rel_path = Path.GetRelativePath(str(source[0]))
  path = os.path.join(Path.GetThriftOutPath(),
                      os.path.dirname(rel_path),
                      'gen-py',
                      os.path.basename(rel_path))
  path = path.replace('.thrift', '')
  target.append(os.path.join(path, 'ttypes.py'))
  target.append(os.path.join(path, 'constants.py'))
  target.append(os.path.join(path, '__init__.py'))
  for service_name in _GetServiceNames(str(source[0])):
    target.append(os.path.join(path, service_name + '.py'))
    target.append(os.path.join(path, service_name + '-remote'))
  return target, source

class ThriftBuilder(LanguageBuilder):
  """Thrift code builders"""
  def __init__(self):
    LanguageBuilder.__init__(self)

  def GetBuildRegisterers(self):
    return ['thrift_library']

  def RegisterSConsBuilders(self):
    thrift_cpp_action = Action('$THRIFTCCOM', '$THRIFTCCOMSTR')
    thrift_cpp_builder = Builder(action = thrift_cpp_action,
                                 emitter = _thrift_cpp_emitter,
                                 src_suffix = '.thrift'
                                 )
    thrift_php_action = Action('$THRIFTPHPCOM', '$THRIFTPHPCOMSTR')
    thrift_php_builder = Builder(action = thrift_php_action,
                                 emitter = _thrift_php_emitter,
                                 src_suffix = '.thrift'
                                 )
    thrift_py_action = Action('$THRIFTPYCOM', '$THRIFTPYCOMSTR')
    thrift_py_builder = Builder(action = thrift_py_action,
                                emitter = _thrift_py_emitter,
                                src_suffix = '.thrift'
                                )
    return {'ThriftCppLibrary' : thrift_cpp_builder,
            'ThriftPhpLibrary' : thrift_php_builder,
            'ThriftPyLibrary' : thrift_py_builder}

  def GenerateEnv(self, env):
    env['THRIFT'] = Path.GetAbsPath(Flags.THRIFT_BIN)
    env['THRIFTSOURCEDIR'] = ('-I %s -I %s' %
                              (Path.GetBaseDir(), Path.GetGlobalDir()))
    env['THRIFTOUTDIR'] = Path.GetThriftOutPath()
    env['THRIFTPHPOUTDIR'] = Path.GetCustomizedThriftPhpOutPath(self)
    env['THRIFTCFLAGS'] = ':include_prefix'
    env['THRIFTPHPFLAGS'] = ':server'
    env['THRIFTPYFLAGS'] = ':new_style'
    env['THRIFTCCOM'] = ('$THRIFT $THRIFTSOURCEDIR --gen '
                         'cpp$THRIFTCFLAGS -o $THRIFTOUTDIR $SOURCES')
    env['THRIFTPHPCOM'] = ('$THRIFT $THRIFTSOURCEDIR --gen '
                           'php$THRIFTPHPFLAGS -o $THRIFTOUTDIR $SOURCES;'
                           'mkdir -p $THRIFTOUTDIR/packages;'
                           '$THRIFTPHPMVCMD')
    env['THRIFTPYCOM'] = ('$THRIFT $THRIFTSOURCEDIR --gen '
                           'py$THRIFTPYFLAGS -o $THRIFTOUTDIR $SOURCES;')

  def _GetOutputDir(self, obj):
    return os.path.join(Path.GetThriftOutPath(),
                        os.path.dirname(Path.GetRelativePath(obj.name_)))

  def PreProcessObject(self, env, obj):
    if obj.option_['gen_py']:
      for d in obj.depends_:
        dep_obj = self.build_manager_.GetObjByName(d)
        dep_obj.option_['gen_py'] = True

  def BuildObject(self, env, obj):
    if (not obj.option_['gen_cpp'] and
        not obj.option_['gen_php'] and
        not obj.option_['gen_py']):
      print Util.BuildMessage('%s: at least specify one generated '
                              'language(gen_cpp,gen_php, gen_py)' % obj.name_,
                              'WARNING')
    source = [Path.GetAbsPath(x) for x in obj.sources_]
    if obj.option_['gen_cpp']:
      cpp_outdir = self._GetOutputDir(obj)
      cpp_sources = env.ThriftCppLibrary([], source,
                                         THRIFTOUTDIR = cpp_outdir)
      cpp_path = Cpp.GetCppInclude(obj)
      target = Path.GetBuiltPath(obj.name_)
      cc_flags = env['CCFLAGS']
      cc_flags += " -Wno-return-type "
      env.StaticLibrary(target = target,
                        source = cpp_sources,
                        CPPPATH = cpp_path,
                        CCFLAGS = cc_flags)
    if obj.option_['gen_php']:
      php_outdir = os.path.join(self._GetOutputDir(obj), 'gen-php')
      php_cmd = 'mkdir -p $THRIFTPHPOUTDIR/packages;'
      php_cmd += 'mkdir -p $THRIFTPHPOUTDIR/protocol;'
      php_cmd += 'mkdir -p $THRIFTPHPOUTDIR/transport;'
      for src in source:
        path = os.path.basename(str(src)).replace('.thrift', '')
        php_cmd += 'cp -r $THRIFTOUTDIR/gen-php/' + path + ' $THRIFTOUTDIR/packages/;'
        php_cmd += 'cp -rf $THRIFTOUTDIR/gen-php/' + path + ' $THRIFTPHPOUTDIR/packages/;'
        php_cmd += 'rm -rf $THRIFTOUTDIR/gen-php/' + path + ';'
        php_cmd += 'cp -f $THRIFTOUTDIR/protocol/*.php $THRIFTPHPOUTDIR/protocol;'
        php_cmd += 'cp -f $THRIFTOUTDIR/transport/*.php $THRIFTPHPOUTDIR/transport;'
        php_cmd += 'cp -f $THRIFTOUTDIR/Thrift.php $THRIFTPHPOUTDIR/;'
      php_sources = env.ThriftPhpLibrary([], source,
                                         THRIFTOUTDIR = php_outdir,
                                         THRIFTPHPMVCMD = php_cmd)
      # TODO: use SCons Copy to do it.
      Util.MkDir(php_outdir)
      Util.RecursiveCopy(Path.GetAbsPath(Flags.PHP_THRIFT_DIR), php_outdir)

    if obj.option_['gen_py']:
      py_outdir = self._GetOutputDir(obj)
      target = Path.GetBuiltPath(obj.name_)
      py_sources = env.ThriftPyLibrary(target, source,
                                       THRIFTOUTDIR = py_outdir)
      # TODO: use SCons Copy to do it.
      py_thrift_dir = os.path.join(py_outdir, 'gen-py', 'thrift')
      Util.MkDir(py_thrift_dir)
      Util.RecursiveCopy(Path.GetAbsPath(Flags.PY_THRIFT_DIR), py_thrift_dir)
