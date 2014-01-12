// Copyright 2011  Inc. All Rights Reserved.
// Author: meixuancao@.com (Meixuan Cao)

#include "base/env.h"

#include <map>

#include "base/logging.h"

DEFINE_bool(is_unit_test, false, "");

namespace base {

static std::map<std::string, std::string> g_building_env;

bool is_unit_test() {
  return FLAGS_is_unit_test;
}

bool GetBuildingEnv(const std::string &key, std::string *value) {
  std::map<std::string, std::string>::const_iterator it = g_building_env.find(key);
  if (it == g_building_env.end())
    return false;
  *value = it->second;
  return true;
}

void ListBuildingEnvs(std::vector<std::pair<std::string, std::string> > *vec) {
  vec->clear();
  for (std::map<std::string, std::string>::const_iterator it = g_building_env.begin();
       it != g_building_env.end(); ++it) {
    vec->push_back(make_pair(it->first, it->second));
  }
}

void SetBuildingEnv(const std::string &key, const std::string &value) {
  g_building_env[key] = value;
}

}  // namespace base
