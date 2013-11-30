#!/usr/bin/env python2.6

import BuildManager
import BuildingObject
import Flags
import Path
import Util

import os

"""Define base class of a language handler.
All language handlers should inherit this class.
"""

def _CheckList(l):
  assert isinstance(l, list)


def _CheckDict(l):
  assert isinstance(l, dict)


def RegisterObj(name = None, srcs = [], deps = [],
                option = {}, build_type = None):
  # check inputs
  if name == None or not isinstance(name, str) or name.find('/') != -1:
    Util.Abort('name should be a string and not contain "/": %s' % name)
  if build_type == None or not isinstance(build_type, str):
    Util.Abort('invalid build type')
  _CheckList(srcs)
  _CheckList(deps)
  _CheckDict(option)

  cur_dir = os.getcwd()
  full_name = Path.GetLogicalPath(cur_dir, name)
  build_manager = BuildManager.GetBuildManager()
  if build_manager.HasObj(full_name):
    return None
  # insert the object
  obj = BuildingObject.BuildingObject()
  if full_name.startswith(Flags.BUILD_FILE_PREFIX):
    obj.is_private_ = True
    full_name = full_name.replace(Flags.BUILD_FILE_PREFIX, '//')
  obj.name_ = full_name
  obj.path_ = os.path.join(cur_dir, name)
  obj.build_type_ = build_type
  for src in srcs:
    obj.sources_.append(Path.GetLogicalPath(cur_dir, src, adj_yb = True))
  obj.option_ = option
  # handle dependencies
  for dep in deps:
    if not dep.startswith('//') and not dep.startswith(':'):
      Util.Abort('Invalid dep %s(%s), need starts with "//" or ":"' %
                 (name, dep))
    dep_path = Path.GetLogicalPath(cur_dir, dep, adj_yb = True)
    obj.raw_depends_.append(dep_path)
    if dep_path not in obj.depends_:
      obj.depends_.append(dep_path)
    if Path.IsStaticLib(dep): continue
    dep_build_file = Path.GetBuildFilePath(dep_path)
    if os.path.exists(dep_build_file):
      build_manager.AddDependentBuildFile(dep_build_file)
    else:
      dep_build_file = Path.GetPrivateYbuildPath(dep_path)
      if not os.path.exists(dep_build_file):
        print Util.BuildMessage(
            'in %s: dep build file for obj %s not found.' %
            (obj.name_, dep_path), 'WARNING')
        continue
      build_manager.AddDependentBuildFile(dep_build_file)
    if Path.IsInDir(dep_build_file, Path.GetGlobalDir()):
      obj.is_on_global_ = True
  build_manager.AddObj(full_name, obj)
  return obj


class LanguageBuilder(object):
  def __init__(self):
    self.build_manager_ = BuildManager.GetBuildManager()

  def GetBuildRegisterers(self):
    """Gets the registerers for this language.
    A registerer is a method to register a build object in the build file.
    Note, the registerer should always register the type of the object as the
    same of its name.
    For example:  cc_binary should always register object's type as 'cc_binary'
    Return a list of name of the registerers.
    """
    return []

  def RegisterSConsBuilders(self):
    """Register builders into the SCons environment.
    Add SCons builders for language specific build that are not covered
    by the build-in builders.
    Return a dict of the builders, the key is the name of the builder,
    the value is the builder itself. For example:
      {'UnitTest': UnittestBuilder}
    """
    return {}

  def GenerateEnv(self, env):
    """Generate specific environment for the language.
    """
    return {}

  def PreProcessObject(self, env, obj):
    """Pre process the object.
    Here's a chance for the language builder to pre process the obj, to even
    comput dependency or any magic else.
    The order to preprocess the objects respect to their dependency
    relationship, say, if A depends on B, than B will be called before A.
    The input parameter obj is instance of BuildObj.BuildObj.
    Return value is not needed for this method.
    """
    pass

  def BuildObject(self, env, obj):
    """Build the object.
    The input parameter obj is instance of BuildObj.BuildObj.
    Return value is not needed for this method.
    """
    pass

  def Finish(self, env):
    """Interface called after all build is finished."""
    pass
