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


def proto_library(name = None, srcs = [], deps = [], plugin = [],
                  gen_cpp = '', gen_py = '', gen_rpc = ''):
  if not name.endswith('_proto'):
    Util.Abort('proto lib\'s name should ends with "_proto"')
  if len(srcs) != 1 or not srcs[0].endswith('.proto'):
    Util.Abort('proto src should be only one .proto file')

  opt = {'gen_cpp':False, 'gen_py':False, 'gen_rpc':False, 'plugin': []}

  if str(gen_cpp) == '1':
    opt['gen_cpp'] = True
  if str(gen_py) == '1':
    opt['gen_py'] = True
  if str(gen_rpc) == '1':
    if not name.endswith('_service_proto'):
        Util.Abort('proto grpc lib\'s name should ends with "_service_proto"')
    opt['gen_rpc'] = True

  if len(plugin) > 0:
      opt['plugin'] = plugin

  RegisterObj(name, srcs, deps, opt, 'proto_library')


def _proto_cpp_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetProtoOutPath(), path)
  prefix = cpp_target.replace('.proto', '.pb.')
  target.append(prefix + 'cc')
  target.append(prefix + 'h')
  return target, source


def _proto_rpc_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetProtoOutPath(), path)
  # xujian: add gen rpc sources for cpp.
  prefix = cpp_target.replace('.proto', '.grpc.pb.')
  target.append(prefix + 'cc')
  target.append(prefix + 'h')

  return target, source


def _proto_py_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetProtoOutPath(), path)
  prefix = cpp_target.replace('.proto', '.pb2.')
  target.append(prefix + 'py')

  return target, source

def _proto_cpp_plugin_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetProtoOutPath(), path)
  prefix = cpp_target.replace('.proto', '.pb.')
  target.append(prefix + 'cc')
  target.append(prefix + 'h')
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
    proto_cpp_plugin_action = Action('$PROTOCPPPLUGINCCOM', '$PROTOCPPPLUGINCCOMSTR')
    proto_cpp_plugin_builder = Builder(action = proto_cpp_plugin_action,
                                       emitter = _proto_cpp_plugin_emitter,
                                       src_suffix = '.proto')

    # proto_rpc_action = Action('$PROTORPCCCOM', '$PROTORPCCCOMSTR')
    # proto_rpc_builder = Builder(action = proto_rpc_action,
    #                             emitter = _proto_rpc_emitter,
    #                             src_suffix = '.proto')

    return {'ProtoCppLibrary' : proto_cpp_builder,
            'ProtoPyLibrary' : proto_py_builder,
            'ProtoCppPluginLibrary': proto_cpp_plugin_builder,
 #           'ProtoRpcLibrary': proto_rpc_builder
            }

  def GenerateEnv(self, env):
    env["PRECMD"] = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/:%s:%s" % (Path.GetAbsPath(Flags.PROTO_LIB), Path.GetAbsPath(Flags.CPP_PPROF_LIB_PATH))
    env['PROTO']       = "%s;%s" % (env["PRECMD"], Flags.PROTO_BIN)
    env['PROTOCFLAGS'] = SCons.Util.CLVar('')

    if os.path.exists(Path.GetGlobalDir()):
      env['PROTOINCLUDE'] = ('-I%s -I%s -I%s -I%s' %
                             (Path.GetBaseDir(),
                              Path.GetGlobalDir(),
                              Path.GetAbsPath(Flags.PROTO_INC),
                              Path.GetAbsPath(Flags.IDICT_INC),
                             ))
    else:
      env['PROTOINCLUDE'] = ('-I%s -I%s -I%s' %
                             (Path.GetBaseDir(),
                              Path.GetAbsPath(Flags.PROTO_INC),
                              Path.GetAbsPath(Flags.IDICT_INC),
                             ))

    env['PROTO_PY_INC'] = ('-I%s -I%s' %
                         (Path.GetBaseDir(),
                          Path.GetAbsPath(Flags.PROTO_PY_INC),
                         ))

    env['PROTOCOUTDIR'] = Path.GetProtoOutPath()

    env['PROTOCCOM'] = ('$PROTO $PROTOCFLAGS ${SOURCE.abspath} '
                      '--cpp_out=$PROTOCCPPOUTFLAGS$PROTOCOUTDIR $PROTOINCLUDE')

    env['PROTOCPPPLUGINCCOM'] = ('$PROTO $PROTOCFLAGS ${SOURCE.abspath} '
                                 '--cpp_out=$PROTOCCPPOUTFLAGS$PROTOCOUTDIR $PROTOINCLUDE')

    env['PROTOPYCCOM'] = ('$PROTO $PROTOCFLAGS ${SOURCE.abspath} '
                      '--python_out=$PROTOCCPPOUTFLAGS$PROTOCOUTDIR $PROTO_PY_INC')

    # for grpc
    # env['PROTOPLUGIN'] = Path.GetAbsPath(Flags.GRPC_PLUGIN_CPP)
    # env['PROTOGOOGLEAPI'] = ('-I%s' % Path.GetAbsPath(Flags.PROTO_GOOGLE_API_INC))
    # env['PROTORPCCCOM'] = ('$PROTO $PROTOCFLAGS ${SOURCE.abspath} '
    #                        '--plugin=protoc-gen-grpc=$PROTOPLUGIN '
    #                        '--grpc_out=$PROTOCCPPOUTFLAGS$PROTOCOUTDIR $PROTOINCLUDE')
    pass


  def BuildObject(self, env, obj):
    if (not obj.option_['gen_cpp'] and not obj.option_['gen_py']):
      print Util.BuildMessage('%s: at least specify one generated '
                              'language(gen_cpp, gen_py)' % obj.name_,
                              'WARNING')
    source = [Path.GetAbsPath(x) for x in obj.sources_]
    if obj.option_['gen_cpp']:
      cpp_source = env.ProtoCppLibrary([], source)
      cc_flags = []

      if len(obj.option_['plugin']) > 0:
        plugin_source = env.ProtoCppPluginLibrary([], source)
        cpp_source += plugin_source

      for plg in obj.option_['plugin']:
        plg_segs = plg.split('=')
        if len(plg_segs) != 2: continue
        out_param = plg_segs[0].replace('protoc-gen-', '')
        plg_bin = plg_segs[0] + '=' + Path.GetAbsPath(plg_segs[1])
        env['PROTOCPPPLUGINCCOM'] += ' --%s_out=%s --plugin=%s  ' % (out_param, '$PROTOCCPPOUTFLAGS$PROTOCOUTDIR', plg_bin)

      # if obj.option_['gen_rpc']:
      #   rpc_source = env.ProtoRpcLibrary([], source)
      #   cpp_source += rpc_source
      #   cc_flags = ['-std=c++11']

      cpp_path = Cpp.GetCppInclude(obj)
      target = Path.GetBuiltPath(obj.name_)
      ret = env.StaticLibrary(target = target,
                        source = cpp_source,
                        CPPPATH = cpp_path,
                        CCFLAGS = cc_flags)
    if obj.option_['gen_py']:
      py_source = env.ProtoPyLibrary([], source)
