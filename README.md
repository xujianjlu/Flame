Flame
=====

Construct tools based on Scons

####Example:

  build -- debug model:

    flame/build.sh t=test/main [c=dbg]

  build -- opt model:

    flame/build.sh t=test/main c=opt

  clean built objects:

    flame/make.sh t=test/main -c

  build unittest and execute it:
    flame/build.sh t=test/unittest_name test=unittest_name

####TODO
	1. enable opt model.
	2. enable third party libs.
