#!/usr/bin/python
#
# Copyright 2010 Inc. All Rights Reserved.

from SCons.Script import ARGUMENTS

import Path
import SCons.Script
import Util

import glob
import os

"Add new language build here"
_Languages = ('CopyAndZip Cpp Cuda Proto Python Sbt Thrift')

class BuildManager(object):
  """Object that manages all build for all languages."""
  def __init__(self, env):
    self.env_ = env

    # objects used to analysis dependencies and hold object info
    self.obj_maps_ = {}
    self.dependent_builds_ = []
    self.processed_builds_ = set()
    self.building_objs_ = []

    self.build_targets_ = []
    self.test_targets_ = []

    # objects for builder info
    self.builders_ = {}
    self.lang_builders_ = []
    pass

  def _LoadBuildFile(self, build_path):
    command = self._GenerateRegistererCommand()
    try:
      exec(command)
    except:
      Util.Abort('exec failed: %s.' % command)
    try:
      os.chdir(os.path.dirname(build_path))
      f = file(build_path, 'r')
    except:
      Util.Abort('No BUILD file: %s' % build_path)
    exec f

  def _LoadTargets(self, target):
    self.dependent_builds_.append(Path.GetBuildFilePath(target))
    while len(self.dependent_builds_) > 0:
      build_file = self.dependent_builds_.pop(0)
      if not build_file in self.processed_builds_:
        self.processed_builds_.add(build_file)
        self._LoadBuildFile(build_file)
    # */... means build all objects under the directory
    if target.endswith(':...'):
      path = Path.GetAbsPath(target[:-4])
      for obj in self.obj_maps_.itervalues():
        if os.path.dirname(obj.path_) == path:
          self.build_targets_.append(obj.name_)
    else:
      self.build_targets_.append(target)
    test = ARGUMENTS.get('test', None)
    if test:
      for target in self.build_targets_:
        target_path = Path.GetRelativePath(target)
        if test == 'all' or target_path.find(test) != -1:
          self.test_targets_.append(target)
    pass

  def _GetAllObjs(self, targets):
    obj_list = [[x,x] for x in targets]
    obj_set = []
    for t in targets:
      obj_set.append(t)
    idx = 0
    # get all objs
    while idx < len(obj_list):
      obj_name = obj_list[idx][0]
      if Path.IsStaticLib(obj_name) and not self.HasObj(obj_name):
        idx += 1
        continue
      if not self.HasObj(obj_name):
        Util.Abort('Not defined obj "%s" in "%s"' %
                   (obj_name, obj_list[idx][1]))
      idx += 1
      obj = self.GetObjByName(obj_name)
      for dep in obj.depends_:
        if dep not in obj_set:
          obj_list.append([dep, obj_name])
          obj_set.append(dep)
    return [x[0] for x in obj_list]

  def _TopologySort(self, obj_list):
    out_map = {}
    dep_map = {}
    objs = [] + obj_list
    result = []
    for item in obj_list:
      if Path.IsStaticLib(item) and not self.HasObj(item):
        out_map[item] = 0
        dep_map[item] = []
      else:
        obj = self.GetObjByName(item)
        out_map[item] = len(obj.depends_)
        dep_map[item] = obj.depends_
    for i in range(len(obj_list)):
      found = False
      for idx in range(len(objs) - 1, -1, -1):
        if out_map[objs[idx]] == 0:
          found = True
          break
      if not found:
        # found loop, now remove all leaf nodes
        sz = 0
        while (sz != len(out_map)):
          sz = len(out_map)
          keys = out_map.keys()
          for dep in keys:
            dep_num = 0
            for obj_name in keys:
              if (obj_name == dep or
                  (Path.IsStaticLib(obj_name) and not self.HasObj(obj_name))):
                continue
              if dep in self.GetObjByName(obj_name).depends_:
                dep_num += 1
            if dep_num == 0:
              del out_map[dep]
        Util.Abort('Found dependency loop: %s' % ' '.join(out_map.keys()))
      key = objs[idx]
      result.append(key)
      for k in out_map.iterkeys():
        if key in dep_map[k]:
          out_map[k] -= 1
      del out_map[key]
      objs.pop(idx)
    result.reverse()
    return result

  def _GetAllDependents(self, targets):
    obj_list = self._GetAllObjs(targets)
    result = self._TopologySort(obj_list)
    # updates the dependencies
    dep_idx = len(result) - 1
    while dep_idx > 0:
      dep_obj_name = result[dep_idx]
      if not self.HasObj(dep_obj_name):
        dep_idx -= 1
        continue
      dep_obj = self.GetObjByName(dep_obj_name)
      obj_idx = dep_idx - 1
      while obj_idx >= 0:
        obj_name = result[obj_idx]
        if not self.HasObj(obj_name):
          obj_idx -= 1
          continue
        obj = self.GetObjByName(obj_name)
        if (dep_obj_name in obj.depends_):
          for d in dep_obj.depends_:
            if d in obj.depends_:
              obj.depends_.remove(d)
            obj.depends_.append(d)
        obj_idx -= 1
      dep_idx -= 1
    result.reverse()
    return result

  def _PreProcessObjs(self):
    for obj_name in self.building_objs_:
      try:
        obj = self.GetObjByName(obj_name)
        # for private module, just link it as library, no need to compile
        if obj.is_private_:
          continue
      except:
        continue
      try:
        builder = self.builders_[obj.build_type_]
      except:
        Util.Abort('invalid build type: %s' % obj.build_type_)
      builder.PreProcessObject(self.env_, obj)

  def _BuildObjs(self):
    os.chdir(Path.GetBaseDir())
    for obj_name in self.building_objs_:
      try:
        obj = self.GetObjByName(obj_name)
        # for private module, just link it as library, no need to compile
        if obj.is_private_:
          continue
      except:
        continue
      try:
        builder = self.builders_[obj.build_type_]
      except:
        Util.Abort('invalid build type: %s' % obj.build_type_)
      builder.BuildObject(self.env_, obj)
    pass

  def _AddBuilders(self):
    for lang in _Languages.split():
      command = 'from %s import %sBuilder; lang_builder = %sBuilder()' % (
          lang, lang, lang)
      try:
        exec(command)
      except:
        Util.Abort('exec failed: %s.' % command)
      self.lang_builders_.append((lang, lang_builder))
      registers = lang_builder.GetBuildRegisterers()
      for r in registers:
        self.builders_[r] = lang_builder
      builders = lang_builder.RegisterSConsBuilders()
      if len(builders) > 0:
        self.env_.Append(BUILDERS = builders)
      lang_builder.GenerateEnv(self.env_)

  def _GenerateRegistererCommand(self):
    result = ''
    for lang, lang_builder in self.lang_builders_:
      registers = lang_builder.GetBuildRegisterers()
      for r in registers:
        result += 'from %s import %s\n' % (lang, r)
    return result

  def AddDependentBuildFile(self, build_file):
    assert os.path.exists(build_file)
    if not build_file in self.processed_builds_:
      self.dependent_builds_.append(build_file)
    pass

  def HasObj(self, name):
    return self.obj_maps_.has_key(name)

  def GetObjByName(self, name):
    return self.obj_maps_[name]

  def AddObj(self, name, obj):
    self.obj_maps_[name] = obj

  def GetBuildTargets(self):
    """Get the build target names."""
    return self.build_targets_

  def GetTestTargets(self):
    """Get the test target names."""
    return self.test_targets_

  def Build(self, target):
    Util.LogWithTimestamp('before add builder')
    self._AddBuilders()
    Util.LogWithTimestamp('before load targets')
    self._LoadTargets(target)
    print Util.BuildMessage('building target(s): %s' % str(self.build_targets_))
    if len(self.test_targets_) > 0:
      print Util.BuildMessage('testing target(s): %s' % str(self.test_targets_))
    Util.LogWithTimestamp('before comput depends')
    self.building_objs_ = self._GetAllDependents(self.build_targets_)
    Util.LogWithTimestamp('before preprocess')
    self._PreProcessObjs()
    Util.LogWithTimestamp('before build')
    self._BuildObjs()
    Util.LogWithTimestamp('after build')
    for lang, builder in self.lang_builders_:
      builder.Finish(self.env_)
    pass


class BuildManagerFactory(object):
  _build_manager = None
  def GetBuildManager(self, env = None):
    if BuildManagerFactory._build_manager == None:
      assert isinstance(env, SCons.Script.Environment)
      BuildManagerFactory._build_manager = BuildManager(env)
    return BuildManagerFactory._build_manager


def GetBuildManager(env = None):
  build_manager_factory = BuildManagerFactory()
  return build_manager_factory.GetBuildManager(env)
