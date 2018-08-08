### Flame
- - -
Flame 是一个基于SCons的构建工具。期望的目标是强大且易用，把程序员从构建的繁琐中解放出来，将精力放到更重要的地方。  

**程序员更要懂得心疼程序员。**  
**Let the Makefile go to the hell ！**

关于目前我所了解的基于scons的构建系统，大部分是受到Google公司的官方博客所启发，Flame的原版本也是如此。原文链接（*需要翻墙*）：[云构建：构建系统是如何工作的](http://google-engtools.blogspot.hk/2011/08/build-in-cloud-how-build-system-works.html)



#### 声明
- - -
Flame的前身是作为鄙前公司内部开发使用的构建系统工具，在其基础上，我做了修改，并修复了部分遗留问题而制作出来。为表示对原作者工作的尊重，部分代码中依然保留了原作者名字。  

#### 扩展性
- - -
Flame是高度可扩展、支持多种编程语言的构建工具，不过目前对C++支持较完善，关于其他语言的构建，后续会添加python，至于其他语言，由于本人水平有限，并没有过多关注。  

#### 简洁性
- - -
并且在编译过程中，只输出了编译环境信息，最后会输出编译好的目标位置。大量具体的构建过程信息将会一闪而过，不需要程序员关心，避免每次编译都会被垃圾信息刷屏。最重要的是构建操作不会产生任何中间目标文件，使得整个工程代码树保持干净整洁。  

#### 易用性
* Flame整个系统使用构建描述脚本来获取目标信息，在构建脚本里，只需要声明要构建什么目标，目标的源代码，以及其直接依赖的其它目标（支持依赖已经编译好的第三方静态库）  
* Flame解决了依赖问题。 当你在构建某些目标时，文件有变化，会自动重新构建改动文件所影响的目标，而不会重新编译其他目标。  
* Flame还支持了用户只需要在编译命令上添加一个参数，就能把整个目录树的编译链接和单元测试全部搞定。
* 对于部分代码在编译或者链接阶段有要求的部分，Flame通过在编译描述文件中提供  copt=[...] 选项来实现允许用户自己控制编译连接参数。


#### Example:
----------------
原则上建议工程目录中，有源码的路径下，都要放置一个上述BUILD文件。并且，请将 flame 工具至于跟其他项目文件平级的层次。

示例工程代码结构

    flame/
		├── build
		├── builders
		├── SConstruct
		└── utils
	base/
		├── basictypes.h
		├── logging.cc
		├── logging.h
		├── thread.cc
		├── thread.h
		├── BUILD
	test/
		├── BUILD
		├── proto
		    ├── BUILD
		    └── test.proto
		├── test_cpp.cc
		├── test_fun.cc
		├── test_fun.h
		├── test_gflags.cc
		└── test_glog.cc

BUILD文件:

    cc_binary(name = 'test_cpp',
          	  srcs = ['test_cpp.cc'],
              deps = [':test_fun'],
			  copt = []
             )

    cc_binary(name = 'test_gflags',
              srcs = ['test_gflags.cc'],
              deps = ['//base:base']
             )

    cc_binary(name = 'test_glog',
              srcs = ['test_glog.cc'],
              deps = ['//base:base']
             )

    cc_library(name = 'test_fun',
               srcs = ['test_fun.cc'],
               deps = []
             )


当BUILD文件构造完成之后，在整个工程文件根路径下，便可如下操作：

  构建 -- debug 模式:

    flame/build t=test/test_cpp [c=dbg]

  构建 -- opt/release 模式:

    flame/build t=test/test_cpp c=opt

  清除所有已编译的目标:

    flame/build.sh t=test/test_cpp -c

  编译单元测试并执行:

    flame/build.sh t=test/unittest_name test=unittest_name


#### Todo

- [x]	enable opt model.
- [x] 	enable glog and gflags.
- [x] 	import base lib.
- [x] 	enable protobuf construction.
- [x] 	enable third party libs.
- [ ] 	enable execute built unittest binary automatic.
- [ ] 	enable thrift.

