#!/usr/bin/env python2.6


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


def proto_library(name = None, srcs = [], deps = [],
                  gen_cpp = '', gen_py = ''):
  if not name.endswith('_proto'):
    Util.Abort('proto lib\'s name should ends with "_proto"')
  if len(srcs) != 1 or not srcs[0].endswith('.proto'):
    Util.Abort('proto src should be only one .proto file')
  opt = {'gen_cpp':False, 'gen_py':False}
  if str(gen_cpp) == '1':
    opt['gen_cpp'] = True
  if str(gen_py) == '1':
    opt['gen_py'] = True
  RegisterObj(name, srcs, deps, opt, 'proto_library')


def _proto_cpp_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetProtoOutPath(), path)
  prefix = cpp_target.replace('.proto', '.pb.')
  target.append(prefix + 'cc')
  target.append(prefix + 'h')
  return target, source

def _proto_py_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetProtoOutPath(), path)
  prefix = cpp_target.replace('.proto', '.pb2.')
  target.append(prefix + 'py')
  return target, source

class ProtoBuilder(LanguageBuilder):
  """Proto code builders"""
  def __init__(self):
    LanguageBuilder.__init__(self)

  def GetBuildRegisterers(self):
    return ['proto_library']

  def RegisterSConsBuilders(self):
    proto_cpp_action = Action('$PROTOCCOM', '$PROTOCCOMSTR')
    proto_cpp_builder = Builder(action = proto_cpp_action,
                                emitter = _proto_cpp_emitter,
                                src_suffix = '.proto')
    proto_py_action = Action('$PROTOPYCCOM', '$PROTOPYCCOMSTR')
    proto_py_builder = Builder(action = proto_py_action,
                               emitter = _proto_py_emitter,
                               src_suffix = '.proto')
    return {'ProtoCppLibrary' : proto_cpp_builder,
            'ProtoPyLibrary' : proto_py_builder}

  def GenerateEnv(self, env):
    env['PROTO']       = Flags.PROTO_BIN
    env['PROTOCFLAGS'] = SCons.Util.CLVar('')
    if os.path.exists(Path.GetGlobalDir()):
      env['PROTOINCLUDE'] = ('-I%s -I%s -I%s' %
                             (Path.GetBaseDir(),
                              Path.GetGlobalDir(),
                              Path.GetAbsPath('third_party/protobuf/')))
    else:
      env['PROTOINCLUDE'] = ('-I%s -I%s' %
                             (Path.GetBaseDir(),
                              Path.GetAbsPath('third_party/protobuf/')))
    env['PROTOCOUTDIR'] = Path.GetProtoOutPath()
    env['PROTOCCOM'] = ('$PROTO $PROTOCFLAGS ${SOURCE.abspath} '
                      '--cpp_out=$PROTOCCPPOUTFLAGS$PROTOCOUTDIR $PROTOINCLUDE')
    # python
    env['PROTOPYCCOM'] = ('$PROTO $PROTOCFLAGS ${SOURCE.abspath} '
                      '--python_out=$PROTOCCPPOUTFLAGS$PROTOCOUTDIR $PROTOINCLUDE')
    pass

  def BuildObject(self, env, obj):
    if (not obj.option_['gen_cpp'] and not obj.option_['gen_py']):
      print Util.BuildMessage('%s: at least specify one generated '
                              'language(gen_cpp, gen_py)' % obj.name_,
                              'WARNING')
    source = [Path.GetAbsPath(x) for x in obj.sources_]
    if obj.option_['gen_cpp']:
      cpp_source = env.ProtoCppLibrary([], source)
      cpp_path = Cpp.GetCppInclude(obj)
      target = Path.GetBuiltPath(obj.name_)
      env.StaticLibrary(target = target,
                        source = cpp_source,
                        CPPPATH = cpp_path)
    if obj.option_['gen_py']:
      py_source = env.ProtoPyLibrary([], source)
