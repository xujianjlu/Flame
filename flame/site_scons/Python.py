#!/usr/bin/env python


from LanguageBuilder import LanguageBuilder
from LanguageBuilder import RegisterObj
from SCons.Script import Action
from SCons.Script import Builder
from SCons.Script import ARGUMENTS

import os
import Flags
import Path

def py_binary(name, srcs, deps=[], paths=[]):
    opt = {}
    opt['paths'] = paths
    assert len(srcs) == 1
    RegisterObj(name, srcs, deps, opt, 'py_binary')

class PythonBuilder(LanguageBuilder):
    """Python code builder"""
    def __init__(self):
        LanguageBuilder.__init__(self)
        self._build_mode = ARGUMENTS.get('c', 'dbg')

    def GetBuildRegisterers(self):
        return ['py_binary']

    def RegisterSConsBuilders(self):
        action = Action('$PYTHONCOM', '$PYTHONCOMSTR')
        builder = Builder(action = action)
        return {'PythonBuilder' : builder}

    def GenerateEnv(self, env):
        env['PYTHONCOM'] = ('python $PY_BUILD_MODE $PYINSTALLER_MAKER -F $PY_SOURCE $OPTIONS -o $SPEC_DIR -n $NAME > $SPEC_DIR/log 2>&1 &&'
                            'python $PY_BUILD_MODE $PYINSTALLER_BUILDER $SPEC_FILE >> $SPEC_DIR/log 2>&1 &&'
                            'exit 0 ||'
                            'cat $SPEC_DIR/log && exit 1 ||'
                            'exit 2')
        env['PYINSTALLER_MAKER'] = Path.GetAbsPath(Flags.PYINSTALLER_MAKER)
        env['PYINSTALLER_BUILDER'] = Path.GetAbsPath(Flags.PYINSTALLER_BUILDER)

    def PreProcessObject(self, env, obj):
        self._CheckSpecialDependency(obj)
        self._GenerateConfiguration()

    def BuildObject(self, env, obj):
        source = Path.GetAbsPath(obj.sources_[0])
        target = Path.GetBuiltPath(obj.name_)
        target_dir = os.path.dirname(target)

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        basename = Path.GetBaseName(obj.name_)
        build_mode = ''
        spec_dir = os.path.dirname(Path.GetBuiltPath(obj.name_))
        spec_file = os.path.join(spec_dir, '%s.spec' % basename)
        options = []
        if obj.option_['paths']:
            options.append('-p %s' % self._GetImportPaths(obj.option_['paths']))
        if self._build_mode == 'dbg':
            pass
        elif self._build_mode == 'opt':
            build_mode = '-O'
        else:
            Util.Abort('wrong build strategy: %s' % self._build_mode)
        tmp_binary = os.path.join(spec_dir, 'dist', basename)

        env.PythonBuilder(None,  # pyinstaller check the mtime between source and target
                          source,
                          PY_BUILD_MODE = build_mode,
                          PY_SOURCE = source,
                          PY_TARGET = target,
                          NAME = basename,
                          BINARY = tmp_binary,
                          OPTIONS = ' '.join(options),
                          SPEC_DIR = spec_dir,
                          SPEC_FILE = spec_file)

    def _GetImportPaths(self, paths):
        abs_paths = []
        for path in paths:
            abs_paths.append(Path.GetAbsPath(path))
        return ':'.join(abs_paths)

    def _GenerateConfiguration(self):
        abs_script = Path.GetAbsPath(Flags.PYINSTALLER_CONFIURE)
        build_mode = ''
        if self._build_mode == 'opt':
            build_mode = '-O'
        assert os.system('python %s %s > /dev/null 2>&1' % (build_mode, abs_script)) == 0

    def _CheckSpecialDependency(self, obj):
        dep_paths = set()
        has_thrift_dep = False
        for d in obj.depends_:
            if d.endswith('_thrift'):
                has_thrift_dep = True
                path = os.path.join(Path.GetThriftOutPath(), Path.GetRelativePath(d))
                path = os.path.join(os.path.dirname(path), 'gen-py')
                dep_paths.add(Path.GetRelativePath(path))
                dep_obj = self.build_manager_.GetObjByName(d)
                dep_obj.option_['gen_cpp'] = False
                dep_obj.option_['gen_php'] = False
                dep_obj.option_['gen_py'] = True
        if has_thrift_dep:
            obj.option_['paths'].extend(dep_paths)

        dep_paths = set()
        has_proto_dep = False
        for d in obj.depends_:
            if d.endswith('_proto'):
                has_proto_dep = True
                path = os.path.join(Path.GetProtoOutPath(), Path.GetRelativePath(d))
                path = os.path.dirname(path)
                dep_paths.add(Path.GetRelativePath(path))
                dep_obj = self.build_manager_.GetObjByName(d)
                dep_obj.option_['gen_cpp'] = False
                dep_obj.option_['gen_php'] = False
                dep_obj.option_['gen_py'] = True
        if has_proto_dep:
            obj.option_['paths'].extend(dep_paths)
            obj.option_['paths'].append(Flags.PROTO_PY_INC)
