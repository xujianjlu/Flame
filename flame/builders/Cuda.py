#!/usr/bin/env python

from LanguageBuilder import LanguageBuilder
from LanguageBuilder import RegisterObj
from SCons.Script import Action
from SCons.Script import Builder
from SCons.Script import ARGUMENTS

import os
import Cpp
import Flags
import Path
import SCons.Util
import Util

def cuda_library(name = None, srcs = [], deps = [],
                  gen_cpp = ''):
  if not name.endswith('_cuda'):
    Util.Abort('cuda lib\'s name should ends with "_cuda"')

  opt = {}
  RegisterObj(name, srcs, deps, opt, 'cuda_library')

def _cuda_emitter(target, source, env):
  cpp_target = os.path.join(Path.GetOutputDir(), str(source[0]))
  obj_target = cpp_target.replace('.cu', '.o')
  target.append(obj_target)
  return target, source


class CudaBuilder(LanguageBuilder):
  """Proto code builders"""
  def __init__(self):
    LanguageBuilder.__init__(self)

  def GetBuildRegisterers(self):
    return ['cuda_library']

  def RegisterSConsBuilders(self):
    cuda_action = Action('$CUDACOM', '$CUDACOMSTR')
    cuda_builder = Builder(action = cuda_action,
                           emitter = _cuda_emitter,
                           src_suffix = '.cu')
    return {'CudaLibrary' : cuda_builder}

  def GenerateEnv(self, env):
    env['ENV']['PATH'] += ':%s' % Flags.CUDA_BIN_DIR
    env['NVCC'] = Flags.CUDA_NVCC_BIN
    env['CUDA_INC'] = Flags.CUDA_INC
    env['CUDA_SDK_COMMON_INC'] = Flags.CUDA_SDK_COMMON_INC
    env['CUDA_SDK_SHARED_INC'] = Flags.CUDA_SDK_SHARED_INC
    env['CUDACOM'] = ('$NVCC $NVCC_FLAGS -I. -I $CUDA_INC -I $CUDA_SDK_COMMON_INC '
                      '-I $CUDA_SDK_SHARED_INC -c -o $CUDAOUTOBJ ${SOURCES}')
    env['CUDAOUTOBJ'] = ""
    build_strategy = ARGUMENTS.get('c', 'dbg')
    if build_strategy == 'dbg':
      env['NVCC_FLAGS'] = ' ';
    elif build_strategy == 'opt':
      env['NVCC_FLAGS'] = '-O2 -DNDEBUG';
    # else:
    #   assert False, 'wrong build strategy: %s' % build_strategy

  def BuildObject(self, env, obj):
    #TODO: add python support
    source = [Path.GetRelativePath(x) for x in obj.sources_]
    obj_target_list = []
    print source
    for src in source:
      cpp_target = os.path.join(Path.GetOutputDir(), str(src))
      obj_target = cpp_target.replace('.cu', '.o')
      obj_target_list.append(obj_target)
      cpp_source = env.CudaLibrary([], src,
                        CUDAOUTOBJ = obj_target)

    cpp_path = Cpp.GetCppInclude(obj)
    target = Path.GetBuiltPath(obj.name_)
    env.StaticLibrary(target = target,
                      source = obj_target_list,
                      CPPPATH = cpp_path)

