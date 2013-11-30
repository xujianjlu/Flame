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


def bison_library(name = None, srcs = [], deps = [], bison_opt=""):
  if not name.endswith('_bison'):
    Util.Abort('bison lib\'s name should ends with "_bison"')
  if len(srcs) != 1 or not srcs[0].endswith('.y'):
    Util.Abort('bison src should be only one .y file')
  opt = {}
  opt['bison_opt'] = bison_opt
  RegisterObj(name, srcs, deps, opt, 'bison_library')


def _bison_cpp_emitter(target, source, env):
  path = Path.GetRelativePath(str(source[0]))
  cpp_target = os.path.join(Path.GetBisonOutPath(), path)
  prefix = cpp_target[:-2] + '.tab.'
  target.append(prefix + 'cc')
  target.append(prefix + 'h')
  return target, source


class BisonBuilder(LanguageBuilder):
  """Bison code builders"""
  def __init__(self):
    LanguageBuilder.__init__(self)

  def GetBuildRegisterers(self):
    return ['bison_library']

  def RegisterSConsBuilders(self):
    bison_cpp_action = Action('$BISON_COM', '$BISONCOMSTR')
    bison_cpp_builder = Builder(action = bison_cpp_action,
                                emitter = _bison_cpp_emitter,
                                src_suffix = '.y')
    return {'BisonCppLibrary' : bison_cpp_builder}

  def GenerateEnv(self, env):
    env['BISON_BIN']        = Path.GetAbsPath(Flags.BISON_BIN, abort = False)
    env['BISON_DIR']        = Path.GetAbsPath(Flags.BISON_DIR, abort = False)
    env['BISON_OUTDIR']     = Path.GetBisonOutPath()
    env['BISON_PKGDATADIR'] = env['BISON_DIR'] + '/share/bison/'
    env['BISON_LOCALEDIR']  = env['BISON_DIR'] + '/share/locale/'
    env['M4']               = env['BISON_DIR'] + '/bin/m4'
    env['BISON_COM'] = (
        "$MKDIR "
        "BISON_PKGDATADIR=$BISON_PKGDATADIR "
        "BISON_LOCALEDIR=$BISON_LOCALEDIR "
        "M4=$M4 "
        "$BISON_BIN ${SOURCE.abspath} "
        "--output=$BISON_OUTDIR/$OUT_SRC "
        "--defines=$BISON_OUTDIR/$OUT_HEAD "
        "$OTHER_OPT")
    pass

  def BuildObject(self, env, obj):
    rel_path = Path.GetRelativePath(obj.sources_[0])
    abs_path = Path.GetAbsPath(obj.sources_[0])
    yfilename = rel_path[:-2]  # remove .y
    ccfile = yfilename  + ".tab.cc"
    headfile = yfilename  + ".tab.h"
    out_detail_dir = os.path.join(Path.GetBisonOutPath(),
                                  os.path.dirname(rel_path))
    mkdir_cmd = ''
    if not os.path.isdir(out_detail_dir):
       mkdir_cmd = "mkdir -p %s && " % (out_detail_dir, )

    cpp_source = env.BisonCppLibrary(
        [],
        abs_path,
        OUT_SRC = ccfile,
        OUT_HEAD = headfile,
        MKDIR = mkdir_cmd,
        OTHER_OPT = obj.option_['bison_opt'],
        )
    cpp_path = Cpp.GetCppInclude(obj)
    target = Path.GetBuiltPath(obj.name_)
    env.StaticLibrary(target = target,
                      source = cpp_source,
                      CPPPATH = cpp_path)
