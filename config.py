# -*- coding: utf-8 -*-
import os
from google.appengine.ext import ndb

EXTS=['png','jpg','jpeg','bmp','gif','ico']
COPYRIGHT='3.0'
PARENT_NAME = 'default_xcmd'
def Gxcmd_key(parent_name=PARENT_NAME): 
	return ndb.Key('Xcmd', parent_name)
