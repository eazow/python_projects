# -*- coding:utf-8 -*-


class MyClass(object):
    __slots__ = ['name', 'identifier']

    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier


x = [MyClass(1, 2) for i in xrange(1000000)]