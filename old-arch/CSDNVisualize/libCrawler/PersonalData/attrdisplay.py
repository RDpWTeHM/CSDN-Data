#!/usr/bin/env python3

"""
# file name: AttrDisplay.py
# Author   : Joseph Lin
# E-mail   : joseph.lin@aliyun.com
# 
###
###
"""

###
### import packages
###
import os, sys, io



"""
《Python 学习手册》 CH27 - 一种通用显示工具
Assorted class utilities and tools
"""
class AttrDisplay():
	"""
	Provides an inheritable print overload method that displays
	instances with their class names and name=value pair for
	each attribute stored on the instance itself (but not attrs
	inherited from its classes). Can be mixed into any class,
	and will work on any instance.
	"""
	def getherAttrs(self):
		attrs = []
		for key in sorted(self.__dict__):
			attrs.append('%s=%s' % (key, getattr(self, key)))
		return ', '.join(attrs)
	def __str__(self):
		return '[%s: %s]' % (self.__class__.__name__, self.getherAttrs())


### main -- tester!
def main():
	pass

if __name__ == '__main__':
	main()



