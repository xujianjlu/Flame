Flame
=====

Construct tools based on Scons

Example:

build -- debug model:
    flame/make.sh t=test/main
    
build -- opt model:
    flame/make.sh t=test/main c=opt

clean builded objects:
    flame/make.sh t=test/main -c
