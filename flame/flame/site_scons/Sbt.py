#!/usr/bin/env python2.6

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

def sbt_library(name = None, srcs = [], deps = [], opt = {}, gen_cpp = '', gen_java = ''):
  RegisterObj(name, srcs, deps, opt, 'sbt_library')

def sbt_binary(name = None, srcs = [], deps = [], opt = {}, gen_cpp = '', gen_java = ''):
  RegisterObj(name, srcs, deps, opt, 'sbt_binary')

def sbt_web(name = None, srcs = [], deps = [], opt = {}, gen_cpp = '', gen_java = ''):
  RegisterObj(name, srcs, deps, opt, 'sbt_web')

class SbtBuilder(LanguageBuilder):
  """Sbt code builders"""
  def __init__(self):
    LanguageBuilder.__init__(self)

  def GetBuildRegisterers(self):
    return ['sbt_library', 'sbt_binary', 'sbt_web']

  def RegisterSConsBuilders(self):
    sbt_action = Action('$BUILDCMD', '$SBTCOMSTR')
    sbt_builder = Builder(action = sbt_action)
    return {'SbtBinary' : sbt_builder}

  def GenerateEnv(self, env):
    env['SBT_BIN'] = os.path.join(Path.GetBaseDir(), Flags.SBT_BIN_PATH)

  def BuildObject(self, env, obj):
    source_path = Path.GetSbtPath(obj.name_)
    target_path = Path.GetBuiltPath(obj.name_)

    env['SOURCE_PATH'] = source_path
    env['TARGET_PATH'] = target_path

    if env.GetOption('clean'):
      env['SBT_ACTION'] = Flags.SBT_CLEAN_ACTION
      env['BUILDCMD'] = """rm $TARGET_PATH -rf\n
        rm $TARGET_PATH/* -rf\n
        $SBT_BIN $SOURCE_PATH $SBT_ACTION\n
        exit 0"""
      return Action('$BUILDCMD', '$SBTCOMSTR').execute([], [], env)

    subdir = 'sub_project_dir'
    if subdir in obj.option_:
      sbt_output_dir = os.path.join(source_path, obj.option_[subdir], "target")
    else:
      sbt_output_dir = os.path.join(source_path, "target")

    if obj.build_type_ == 'sbt_library':
      env['SBT_ACTION'] = Flags.SBT_LIB_JAR_BUILD_ACTION
      env['SBT_ARTIFACTS'] = os.path.join(sbt_output_dir, 'scala*', '*-*.jar')
    elif obj.build_type_ == 'sbt_binary':
      env['SBT_ACTION'] = Flags.SBT_BIN_JAR_BUILD_ACTION
      env['SBT_ARTIFACTS'] = os.path.join(sbt_output_dir, '*-assembly-*.jar')
    elif obj.build_type_ == 'sbt_web':
      env['SBT_ACTION'] = Flags.SBT_WAR_BUILD_ACTION
      env['SBT_ARTIFACTS'] = os.path.join(sbt_output_dir, 'scala*', '*.war')

    env['BUILDCMD'] = """rm $TARGET_PATH -rf\n
      rm $TARGET_PATH/* -rf\n
      $SBT_BIN $SOURCE_PATH $SBT_ACTION || $SBT_BIN $SOURCE_PATH $SBT_ACTION\n
      mkdir -p $TARGET_PATH\n
      cp $SBT_ARTIFACTS $TARGET_PATH/\n
      exit 0"""

    env.SbtBinary([' '], [])
