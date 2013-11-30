#!/usr/bin/python2.6


class BuildingObject(object):
  def __init__(self):
    self.name_ = ''
    self.path_ = ''
    self.sources_ = []
    self.depends_ = []
    self.outputs_ = []
    self.raw_depends_ = []
    self.option_ = {}
    self.build_type_ = ''
    self.is_private_ = False
    self.is_on_global_ = False
    pass

  def __str__(self):
    result = '<build obj(%s)' % self.name_
    if self.sources_:
      result += ', src: %s' % str(self.sources_)
    if self.outputs_:
      result += ', outputs: %s' % str(self.outputs_)
    if self.depends_:
      result += ', dep: %s' % str(self.depends_)
    if self.option_:
      result += ', option: %s' % str(self.option_)
    if self.is_private_:
      result += ', private'
    else:
      result += ', public'
    if self.is_on_global_:
      result += ', on_global>'
    else:
      result += '>'
    return result

