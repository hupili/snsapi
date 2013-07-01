Test Suite of SNSAPI
====

To test SNSAPI, you need `nose` package. 
Then issue the command at the root directory of snsapi:

```
nosetests -sv
```

github的测试不需要`nose`

测试方法如下：

	假设目录结构为
	
	project
		\snsapi
			\.git
			\app
			\auxiliary
			\doc
			\snsapi
				\...
			\tests
				\...
				\test_github.py
				\...
			\...
	
	1、首先cd 到 project 目录
	2、再 python -m snsapi.tests.test_github 即可
	
	注意：snsapi 目录下要有__init__.py
		 tests  目录下要有__init__.py
		 -m 后参数 snsapi 为目录名，如果你的目录名为其他则做相应修改
		 强调：是 test_github 而非 test_github.py
	