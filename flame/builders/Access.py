#!/usr/bin/python2.6


"""Check the file access.
"""


import os
import sys


class AccessChecker(object):
  cache_ = {}

  def CheckList(self, paths):
    for p in paths:
      if self.Check(p):
        return True
    return False

  def Check(self, path):
    if not os.path.isdir(path):
      path = os.path.dirname(path)
    return self.CheckDir(path)

  def CheckDir(self, d):
    if d in self.cache_:
      return self.cache_[d]
    result = False
    f = os.path.join(d, 'ACCESS')
    if os.path.exists(f):
      if 'internal' == open(f).read().split('#', 1)[0].strip():
        self.cache_[d] = True
        return True
    while not result:
      d = os.path.dirname(d)
      if len(d) == 0 or d == '/':
        break
      result = self.CheckDir(d)
    self.cache_[d] = result
    return result
