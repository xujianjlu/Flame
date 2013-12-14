#!/usr/bin/python2.6

import sys
sys.path.append('flame/site_scons/')

from SCons.Script import ARGUMENTS

import glob
import hashlib
import inspect
import os
import re
import subprocess
import time

import Flags
import SCons


_verbose = int(ARGUMENTS.get('verbose', '0'))
def Log(msg, v = 3):
  if v > _verbose: return
  s = inspect.stack()
  prefix = ''
  if len(s) > 2:
    prefix = '%s:%d: ' % (os.path.basename(s[1][1]), s[1][2])
  print('%s%s' % (prefix, msg))


def BuildMessage(msg, msg_type = 'INFO'):
  message_head = highlight("[INFO]", 1, False)
  if msg_type == 'WARNING':
    message_head = highlight("[WARNING]", 2, False)
  if msg_type in ['TIMEOUT', 'FAIL']:
    message_head = highlight("[%s]" % msg_type, 2, False)
  if msg_type == 'PASS':
    message_head = highlight("[PASS]", 1, False)
  return "%s %s" % (message_head, msg)


def Abort(msg):
  print BuildMessage(msg, 'FAIL')
  sys.exit(-1)


def LogWithTimestamp(msg):
  # print '[%f]: %s' % (time.time(), msg)
  pass


def highlight(string, status, bold):
  if not sys.stdout.isatty() or os.environ.get('TERM') == 'dumb':
    return string
  attr = []
  if status == 1:
    # green
    attr.append('32')
  else:
    # red
    attr.append('31')
  if bold:
    attr.append('1')
  return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)


def MkDir(dir_path):
  """helper method to create the dir if it does not exists."""
  if os.path.exists(dir_path):
    assert os.path.isdir(dir_path), '%s should be a directory!' % dir_path
  else:
    os.spawnlp(os.P_WAIT, 'mkdir', 'mkdir', '-p', dir_path)


def EnsureBuildDir():
  def _GetHashedName():
    path = os.getcwd()
    m = hashlib.md5()
    m.update(path)
    return m.hexdigest()

  def _CreateDirs():
    path = os.path.join(Flags.LOCAL_BUILD_DIR, _GetHashedName())
    if not os.path.exists(path):
      try:
        os.mkdir(path)
      except:
        Abort('create %s failed, maybe no access?' % path)
    os.symlink(path, Flags.BUILD_OUT)
    MkDir(os.path.join(path, 'opt'))
    MkDir(os.path.join(path, 'dbg'))

  if not os.path.islink(Flags.BUILD_OUT):
    if os.path.exists(Flags.BUILD_OUT):
      print BuildMessage('Deleting the old output dir %s' % Flags.BUILD_OUT,
                         'WARNING')
      os.spawnlp(os.P_WAIT, 'rm', 'rm', '-rf', Flags.BUILD_OUT)
    if not os.path.exists(Flags.LOCAL_BUILD_DIR):
      Abort('No %s, please create it!' % Flags.LOCAL_BUILD_DIR)
    _CreateDirs()
    pass
  elif not os.path.exists(Flags.BUILD_OUT):
    os.remove(Flags.BUILD_OUT)
    _CreateDirs()
    pass


def RecursiveCopy(source, target):
  source_array = glob.glob(source + '/*')
  for source_object in source_array:
    target_path = os.path.join(target, os.path.basename(source_object))
    if not os.path.exists(target_path):
      assert(not os.spawnlp(os.P_WAIT, 'cp', 'cp', '-rf',
             source_object, target))
  pass


def MatchOnePattern(file_path, pattern, group_num = 1):
  result = []
  pattern_re = re.compile(pattern)
  for line in open(str(file_path), 'r'):
    m = pattern_re.match(line)
    if m:
      result.append(m.group(group_num))
  return result


def MatchMultiPatterns(file_path, patterns):
  """patterns is a list of (pattern_str, group_num) as used in MatchOnePattern.
  """
  result = {}
  res = {}
  for p in patterns:
    res[p[0]] = (re.compile(p[0]), p[1])
    result[p[0]] = []
  for line in open(str(file_path), 'r'):
    for pattern, pattern_re in res.items():
      m = pattern_re[0].match(line)
      if m:
        result[pattern].append(m.group(pattern_re[1]))
  return result


def QuietBuild(s, target, src, env):
  # Save real cmd to log file
  open(env['CMD_LOGFILE'], 'a').write('%s\n' % s);


def ColorfulBuild(env, log_in_one_line):
  ctl = {}
  ctl['cyan']   = '\033[96m'
  ctl['purple'] = '\033[95m'
  ctl['blue']   = '\033[94m'
  ctl['green']  = '\033[92m'
  ctl['yellow'] = '\033[93m'
  ctl['end']    = '\033[0m'
  ctl['moveon'] = '\033[1A\033[K'
  if not log_in_one_line:
    ctl['moveon'] = ''

  # If the output is not a terminal, remove the ctl
  if not sys.stdout.isatty() or os.environ.get('TERM') == 'dumb':
    for key, value in ctl.iteritems():
      ctl[key] = ''
  elif log_in_one_line:
    env['SPAWN'] = EchoSpawn

  cc_test_message = ('%s%sTesting Unittest %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  compile_source_message = ('%s%sCompiling %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  compile_shared_source_message = ('%s%sCompiling shared %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  link_program_message = ('%s%sLinking Program %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  link_library_message = ('%s%sLinking Static Library %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  ranlib_library_message = ('%s%sRanlib Library %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  link_shared_library_message = ('%s%sLinking Shared Library %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  java_library_message = ('%s%sCreating Java Archive %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  gen_cpp_message = ('%s%sGenerating C++ file from %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  gen_java_message = ('%s%sGenerating java file from %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  gen_php_message = ('%s%sGenerating php file from %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  gen_python_message = ('%s%sGenerating python file from %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  gen_soy_message = ('%s%sGenerating _soy.js file from %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))
  compile_js_module_message = ('%s%sCompiling js module %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  compile_js_module_binary_message = ('%s%sCompiling js module binary%s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  build_sbt_message = ('%s%sBuilding Scala project %s==> %s$SBT_TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  copy_and_zip_message = ('%s%sCopying/zipping files %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  css_message = ('%s%sBuilding css files %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  install_message = ('%s%sInstalling files %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  android_message = ('%s%sBuilding android files %s==> %s$TARGET%s' %
      (ctl['moveon'], ctl['blue'], ctl['purple'], ctl['yellow'], ctl['end']))
  build_python_message = ('%s%sBuild binary from python script %s==> %s$SOURCE%s' %
      (ctl['moveon'], ctl['green'], ctl['purple'], ctl['yellow'], ctl['end']))

  env['CXXCOMSTR'] = compile_source_message
  env['CCCOMSTR'] = compile_source_message
  env['CCTESTCOMSTR'] = cc_test_message
  env['SHCCCOMSTR'] = compile_shared_source_message
  env['SHCXXCOMSTR'] = compile_shared_source_message
  env['ARCOMSTR'] = link_library_message
  env['RANLIBCOMSTR'] = ranlib_library_message
  env['SHLINKCOMSTR'] = link_shared_library_message
  env['LINKCOMSTR'] = link_program_message
  env['JARCOMSTR'] = java_library_message
  env['JAVACCOMSTR'] = compile_source_message
  env['PROTOCCOMSTR'] = gen_cpp_message
  env['PROTOPYCCOMSTR'] = gen_python_message
  env['PROTOJAVACOMSTR'] = gen_java_message
  env['THRIFTCCOMSTR'] = gen_cpp_message
  env['THRIFTJAVACOMSTR'] = gen_java_message
  env['THRIFTPHPCOMSTR'] = gen_php_message
  env['THRIFTPYCOMSTR'] = gen_python_message
  env['SOYCOMSTR'] = gen_soy_message
  env['JAVASCRIPTCOMSTR'] = compile_source_message
  env['JSMODULECOMSTR'] = compile_js_module_message
  env['JSMODULEBINARYCOMSTR'] = compile_js_module_binary_message
  env['PHPCOMSTR'] = gen_php_message
  env['CUDACOMSTR'] = compile_source_message
  env['SBTCOMSTR'] = build_sbt_message
  env['COPYANDZIPCMDSTR'] = copy_and_zip_message
  env['CSSCMDSTR'] = css_message
  env['INSTALLSTR'] = install_message
  env['ANDROIDCMDSTR'] = android_message
  env['ANDROIDTESTSTR'] = android_message
  env['BISONCOMSTR'] = gen_cpp_message
  env['PYTHONCOMSTR'] = build_python_message


def EchoSpawn(sh, escape, cmd, args, env):
  p = subprocess.Popen(' '.join(args),
                       env = env,
                       stderr = subprocess.PIPE,
                       stdout = subprocess.PIPE,
                       shell = True,
                       universal_newlines = True)
  (stdout, stderr) = p.communicate()

  if len(stdout) > 0:
    sys.stdout.write(stdout + '\n')
  if len(stderr) > 0:
    sys.stderr.write(stderr + '\n')
  return p.returncode


def PrepareEnv(env):
  log = ARGUMENTS.get('log', 'vs')
  if log == 'q':
    env['CMD_LOGFILE'] = os.path.join(Flags.BUILD_OUT, 'build.log')
    env['PRINT_CMD_LINE_FUNC'] = QuietBuild
    print('%s        %s' %
          (highlight('Build log:', 1, False), env['CMD_LOGFILE']))
    if os.path.exists(env['CMD_LOGFILE']):
      os.remove(env['CMD_LOGFILE'])
  elif log == 's':
    ColorfulBuild(env, False)
  elif log == 'vs':
    ColorfulBuild(env, True)
