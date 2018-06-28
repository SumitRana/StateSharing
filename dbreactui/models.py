# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import json
import hashlib
from datetime import datetime

def pass_hash(t):
	hash_object = hashlib.md5(t)
	return hash_object.hexdigest()

# for bottom-up serialization of models
class Serialize:
	@classmethod
	def serializeDjangoModel(cls,row_object):
		try:
			lcs = row_object._meta.local_fields
			local_column_names = []
			jdata = dict()
			for lc in lcs:
				value = getattr(row_object,str(lc.name))
				jdata[str(lc.name)] = cls.serializeDjangoModel(value)
			return jdata
		except Exception:
			return str(row_object)

# Create your models here.

class SharedData(models.Model):
	appname = models.CharField(max_length=250,null=False,blank=False,default="qwerty")
	data = models.TextField(max_length=20000,null=False,blank=False,default=json.dumps({}))
	state_hash = models.TextField(max_length=50,null=False,blank=False,default="")
	updated_states = models.TextField(max_length=10000,null=False,blank=False,default=json.dumps({}))
	creation_time = models.DateTimeField(default=datetime.now())
	expiry_time = models.DateTimeField(default=datetime.now())

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		# self.password = pass_hash(self.password)
		super(SharedData, self).save(force_insert, force_update, using, update_fields)

	def serialize(self):
		return Serialize.serializeDjangoModel(this)