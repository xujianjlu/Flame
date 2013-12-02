// Copyright [2013] <xujiantjdx@126.com / xujiantjdx@gmail.com>

#include <stdio.h>
#include <iostream>

#include "test/test_fun.h"


int main(int argc, char **argv) {
  // test stander io
  printf("a test \n");
  std::cout << "test iostream" << std::endl;
  fun();

  // test proto
  //Person person;
  //person.set_id(100);
  //person.set_name("a person");
  //std::cout << "id : " << person.id() << std::endl;
  //std::cout << "name : " << person.name() << std::endl;
  return 0;
}
