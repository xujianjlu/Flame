#!/usr/bin/env python2.6


from SCons.Script import ARGUMENTS

import os
import re

import Flags
import Util


_base_dir = os.path.normpath(ARGUMENTS.get('base_dir'))
def GetBaseDir():
  """root dir of the code base."""
  return _base_dir


_global_dir = os.path.realpath(
    ARGUMENTS.get('global', '/usr/local/build/global_client'))
_use_global_dir = (ARGUMENTS.get('use_global_dir', 'off') == 'on')
def GetGlobalDir():
  return _global_dir


def GetOutputDir():
  """Get '.flame-out/opt' or '.flame-out/dbg'"""
  strategy = ARGUMENTS.get('c', 'dbg')
  return os.path.join(GetBaseDir(), Flags.BUILD_OUT, strategy)


def GetBuildFilePath(logical_path):
  """'//base:base' --> '.../$ROOT/base/BUILD'"""
  assert logical_path.startswith('//') and logical_path.find(':') != -1
  ybuild_path = os.path.join(logical_path.split(':')[0], Flags.BUILD_NAME)
  return GetAbsPath(ybuild_path, abort = False)


def IsInDir(file_path, dir_path):
  dir_path = os.path.normpath(dir_path) + '/'
  return file_path.startswith(dir_path)


def GetLogicalPath(cur_dir, path, adj_build = False):
  """('~/$ROOT/base', 'foo') --> '//base:foo'
  @adj_build: if to adjust the path for build file.
  """
  if path.startswith('//'):
    return path
  if path.startswith(':'):
    assert path.find('/') == -1
    abs_path = os.path.join(cur_dir, path[1:])
  elif os.path.isdir(path):
    path = os.path.normpath(path)
    path = os.path.join(path, os.path.basename(path))
    abs_path = os.path.join(cur_dir, path)
  else:
    abs_path = os.path.join(cur_dir, path)
  result = os.path.dirname(abs_path) + ':' + os.path.basename(abs_path)
  if IsInDir(abs_path, GetBaseDir()):
    result = '//%s' % os.path.relpath(result, GetBaseDir())
  elif _use_global_dir and IsInDir(abs_path, GetGlobalDir()):
    result = '//%s' % os.path.relpath(result, GetGlobalDir())
  else:
    Util.Abort('invalid path: (%s, %s)' % (cur_dir, path))
  if adj_build and result.startswith(Flags.BUILD_FILE_PREFIX):
    result = result.replace(Flags.BUILD_FILE_PATH, '', 1)
  return result


def GetRelativePath(path):
  if not (path.startswith('//') or path.startswith('/')):
    return path
  if (path.startswith(GetBaseDir())):
    return os.path.relpath(path, GetBaseDir())
  elif (_use_global_dir and path.startswith(GetGlobalDir())):
    return os.path.relpath(path, GetGlobalDir())
  else:
    return path[2:].replace(':', '/')


def GetAbsPath(path, abort = True):
  "path should be logical path or relative path"
  assert path.startswith('//') or not path.startswith('/')
  if path.startswith('//'):
    path = GetRelativePath(path)
  result = os.path.join(GetBaseDir(), path)
  if os.path.exists(result):
    return result
  if _use_global_dir:
    result = os.path.join(GetGlobalDir(), path)
    if os.path.exists(result):
      return result
  if abort:
    Util.Abort('can not find absolute path for %s' % path)
  else:
    return ''


def GetThriftOutPath():
  return os.path.join(GetOutputDir(), Flags.THRIFT_OUT)


def GetProtoOutPath():
  return os.path.join(GetOutputDir(), Flags.PROTO_OUT)


def GetJavaOutPath():
  return os.path.join(GetOutputDir(), Flags.JAVA_BASE_DIR)


def GetJavaPackagePath():
  return os.path.join(GetOutputDir(), Flags.JAVA_PACKGE_BASE)


def GetCustomizedOutputPath(obj = None):
  outDir = ''
  target = ARGUMENTS.get('t')
  if (target == 'mobile/mob_frontend' or
     target == 'mobile/mob_prod'):
    outDir = 'mobile'
  elif (target == 'mobilesearch/mobsearch_frontend' or
     target == 'mobilesearch/mobsearch_prod'):
    outDir = 'mobilesearch'
  elif (target == 'frontend/mobilesearchwap/wwwroot' or
     target == 'frontend/mobilesearchwap/prod'):
    outDir = 'frontend/mobilesearchwap'
  elif (target == 'frontend/weiboreaderm/wwwroot' or
     target == 'frontend/weiboreaderm/prod'):
    outDir = 'frontend/weiboreaderm'
  elif (target == 'searchmblog/smblog_frontend' or
     target == 'searchmblog/smblog_prod'):
    outDir = 'searchmblog'
  elif (target == 'frontend/wwwroot' or
     target == 'frontend/prod'):
    outDir = 'frontend'
  elif (target == 'app/app_frontend' or
     target == 'app/app_prod'):
    outDir = 'app'
  elif (target == 'frontend/yyreader/wwwroot' or
     target == 'frontend/yyreader/prod'):
    outDir = 'frontend/yyreader'
  elif (target == 'frontend/yysso/wwwroot' or
     target == 'frontend/yysso/prod'):
    outDir = 'frontend/yysso'
  elif (target == 'sinasearch/sinasearch_frontend' or
     target == 'sinasearch/sinasearch_prod'):
    outDir = 'sinasearch'
  elif (target == 'frontend/yyoauth/wwwroot' or
     target == 'frontend/yyoauth/prod'):
    outDir = 'frontend/yyoauth'

  return os.path.join(GetOutputDir(), outDir)

def GetFrontendFakeTarget(obj = None):
  target = obj.name_.replace('//', '').replace(':', '_').replace('/', '_') + '.FAKE';
  return os.path.join(GetCustomizedOutputPath(obj), 'FAKE_FILES/' + target)

# Default php code path hack.
_PHP_CODE_PREFIX = 'php/yr'
# Tweak php src file path to start with php/yr
def GetPhpYrPath(src):
  pos = src.find(_PHP_CODE_PREFIX)
  if pos == -1:
    return src
  else:
    return src[pos:]

def GetCustomizedThriftPhpOutPath(obj):
  return os.path.join(GetCustomizedOutputPath(obj), 'php/thrift-out')


def GetModulePath(obj):
  return os.path.join(GetCustomizedOutputPath(obj), Flags.MODULE_DIR)


def GetModuleResultsPath(obj):
  return os.path.join(GetCustomizedOutputPath(obj), Flags.MODULE_RESULTS_DIR)


def GetBuiltPath(path):
  """Given a logical path, give out its building path"""
  assert path.startswith('//')
  # TODO(xujian): hard code the static libs path to 'third_party/'.
  # if path.startswith(Flags.BUILD_FILE_PREFIX):
  #   path = path.replace(Flags.BUILD_FILE_PREFIX, Flags.STATIC_LIB_PREFIX)
  return os.path.join(GetOutputDir(), path[2:]).replace(':', '/')


def GetBaseName(name):
  idx = name.index(':')
  return name[idx+1:]


def GetPrivateYbuildPath(path):
  """Returns the abs path of the private ybuild file path."""
  return GetBuildFilePath(path.replace('//', Flags.BUILD_FILE_PREFIX))


def IsStaticLib(lib_name):
  if lib_name.startswith(Flags.STATIC_LIB_PREFIX):
    return True
  if not lib_name.startswith('//'):
    path = GetLogicalPath(os.getcwd(), lib_name)
    return IsStaticLib(path)
  return False


def GetGlobalYbuildPath(path):
  if path.startswith('/'):
    rel_path = GetRelativePath(path)
  path = os.path.join(_global_dir, rel_path)
  if os.path.exists(path):
    return path
  path = os.path.join(_global_dir, Flags.BUILD_FILE_PATH, rel_path)
  if os.path.exists(path):
    return path
  return None


def IsSVNClient():
  return os.path.exists(os.path.join(GetBaseDir(), '.svn'))


def IsGITClient():
  return os.path.exists(os.path.join(GetBaseDir(), '.git'))


def GetSbtPath(name):
  idx = name.index(':')
  path = name[:idx]
  return GetAbsPath(path);

def GetBisonOutPath():
  return os.path.join(GetOutputDir(), Flags.BISON_OUT)

