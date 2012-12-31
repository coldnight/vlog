#!/usr/bin/env python
#-*- coding:utf-8  -*-
#
# Author : cold
# E-mail : wh_linux@126.com
#
import os
import unittest
from pprint import pprint
from config import ROOT_PATH, UTEST

utest_path = os.path.join(ROOT_PATH, UTEST.replace('.', '/'))

def get_all_utest():
    modules = [m.split('.')[0]  for m in os.listdir(utest_path)
               if m.startswith('test_')]
    return [__import__('utest.{0}'
            ''.format(m)).__dict__['utest'].__dict__[m] for m in modules]

def load_all_utest():
    umodules = get_all_utest()
    loader = unittest.TestLoader()
    suites = [loader.loadTestsFromModule(m) for m in umodules]
    suites = [s for s in suites if s._tests]
    utests = []
    for suite in suites:
        [utests.extend(s._tests)for s in suite._tests if list(s)]

    result = dict()
    for utest in utests:
        key = '{0}.{1}.{2}'.format(utest.__module__,
                                   utest.__class__.__name__,
                                   utest._testMethodName)
        result[key] = utest

    return result

def run_utest(utest = None):
    utests = load_all_utest()
    if not utest:
        pprint(utests.keys())
        return

    ut = utests.get(utest)

    if not ut:
        print 'UnitTest: {0} not found'.format(utest)

    suite = unittest.TestSuite()
    suite.addTest(ut)

    runner = unittest.TextTestRunner(verbosity = 2)
    runner.run(suite)
