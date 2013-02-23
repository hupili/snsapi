Unit Test Suite of SNSAPI
====

This is the Unit Test (UT) of SNSAPI. 

To run the UT, you need `nose` package. 
Then issue the command at the **CURRENT** directory of snsapi:

```
nosetests -sv
```

Convention of UT
----------------

   * After any upgrades, run the unit test suite to regress
   the project. This is to make sure new features do not break
   old features. 
   * Do not add test logic that can not be automated. 

Nitty-Gritties
--------------

   * The reason why we ask to run `nosetests` under current 
   directory is that we do not want to run tests from other 
   projects, e.g. tests introduced in `snsapi/third` directory.


