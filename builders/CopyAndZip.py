#!/usr/bin/env python


from LanguageBuilder import LanguageBuilder
from LanguageBuilder import RegisterObj
from SCons.Script import ARGUMENTS
from SCons.Script import Action
from SCons.Script import Builder

import Flags
import Path
import Util

import os


def _copy_and_zip_object_internal(name, srcs, dest, do_zip, deps, build_type):
  build_strategy = ARGUMENTS.get('c', 'dbg')
  # Do not zip in dbg mode.
  if (build_strategy == 'dbg'):
    do_zip = 0;

  opt = {}
  opt['do_zip'] = do_zip
  opt['dest'] = dest
  assert dest != None
  RegisterObj(name, srcs, deps, opt, build_type)


def copy_and_zip(name = None, srcs = [], dest = None, do_zip = 0, deps = []):
  _copy_and_zip_object_internal(name, srcs, dest, do_zip, deps, 'copy_and_zip')


class CopyAndZipBuilder(LanguageBuilder):
  """Copy and zip builder.
  In dbg mode, this builder creates symbolic links in the dest directory for
  files specified in srcs.
  In opt mode, it copies from files specified in srcs to the dest directory.
  And creates corresponding .gz files if zip option is set to 1.
  """
  def __init__(self):
    LanguageBuilder.__init__(self)


  def GetBuildRegisterers(self):
    return ['copy_and_zip']


  def RegisterSConsBuilders(self):
    copy_and_zip_builder = Builder(
        action = Action('$COPYANDZIPCMD', '$COPYANDZIPCMDSTR'))
    return {'CopyAndZip' : copy_and_zip_builder}


  def GenerateEnv(self, env):
    pass


  def BuildObject(self, env, obj):
    sources = [Path.GetRelativePath(x) for x in obj.sources_]
    dest = os.path.join(Path.GetOutputDir(), obj.option_['dest'])
    Util.MkDir(dest)

    build_strategy = ARGUMENTS.get('c', 'dbg')
    if (build_strategy == 'opt'):
      cmd = 'cp $COPYANDZIPSRCS $DEST'
    else:
      cmd = 'ln -f -s $COPYANDZIPSRCS $DEST'

    zip_cmd = ''
    if (obj.option_['do_zip'] == 1):
      zip_cmd = os.path.join(Path.GetBaseDir(), 'frontend/tools/make_gz.py')
      zip_cmd += ' $DEST;'
    env['COPYANDZIPCMD'] = cmd + ';$ZIPCMD'

    for dep in obj.raw_depends_:
      dep_obj = self.build_manager_.GetObjByName(dep)
      if (hasattr(dep_obj, 'outputs_')):
        sources.extend(dep_obj.outputs_)

    srcs = ''
    for filename in sources:
      srcs += ' ' + os.path.join(Path.GetBaseDir(), filename)
    targets = [os.path.join(dest, os.path.basename(x)) for x in sources]
    obj.sources_ = sources
    obj.outputs_ = targets
    fake_target = Path.GetFrontendFakeTarget(obj)
    targets.append(fake_target)
    zip_cmd += 'touch ' + fake_target + ';'
    # NOTE(xinghuaan): The reason why we make dest and zipcmd standalone
    # paramaters is when multiple copy_and_zip are executed, they
    # share the same env variable. So we have to use placeholder here.
    env.CopyAndZip(targets, sources,
                   COPYANDZIPSRCS = srcs,
                   DEST = dest,
                   ZIPCMD = zip_cmd)
