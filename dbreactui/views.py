# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from .models import SharedData, pass_hash
import json
import random

# Create your views here.


class StateManagement:
    #State string protocol : 
    # {'path':'a>b>c','status':'deleted|added|updated','value': 'value'}

    __appName = None
    __delete_buffer = []
    __add_buffer = []
    __modified_buffer = []

    def __init__(self,app):
        self.__appName = app
        shapp = SharedData(appname=app)
        shapp.save()
        return None
    
    def getUpdatedPaths(self,previous_state,new_state,parent_path=""):
        updated_path_list = []
        pkeys = previous_state.keys()
        nkeys = new_state.keys()
        deleted_keys = list(set(pkeys).difference(set(nkeys)))
        added_keys = list(set(nkeys).difference(set(pkeys)))
        common_keys = list(set(pkeys).intersection(set(nkeys)))
        modified_keys = []

        # updating deleted keys
        path = ""
        for key in deleted_keys:
            path = parent_path+">"+str(key)
            self.__delete_buffer.append({
                'path': path[1:],
                'value': previous_state[str(key)]
            })
        
        # updating added keys
        path = ""
        for key in added_keys:
            path = parent_path+">"+str(key)
            self.__add_buffer.append({
                'path': path[1:],
                'value': new_state[str(key)]
            })
        
        # updating modified keys
        path = ""
        for key in common_keys:
            path = parent_path+">"+str(key)
            if type(new_state[str(key)]) == dict:
                self.getUpdatedPaths(previous_state[str(key)],new_state[str(key)],path)
            else:
                if previous_state[str(key)] != new_state[str(key)]:
                    self.__modified_buffer.append({
                        'path': path[1:],
                        'value': str(new_state[str(key)])
                    })

        return 200
    
    def managePathUpdate(self,p,n):
        self.getUpdatedPaths(p,n)
        print "Deleted keys :" 
        print self.__delete_buffer
        print "\n\nAdded keys :"
        print self.__add_buffer
        print "\n\nmodifies keys :"
        print self.__modified_buffer
        rd = {
            "deleted": self.__delete_buffer,
            "added": self.__add_buffer,
            "updated": self.__modified_buffer
        }
        self.__delete_buffer = []
        self.__add_buffer = []
        self.__modified_buffer = []
        return rd
    
    def updateState(self,state):
        if self.__appName is not None:
            d = SharedData.objects.get(appname=str(self.__appName))
            updated_states = self.managePathUpdate(json.loads(d.data),state)
            d.data = json.dumps(state)
            d.updated_states = json.dumps(updated_states)
            d.state_hash = pass_hash(json.dumps(state))
            d.save()
        return 200


# global url - /dbrui/appname/
# main app url - /dbrui/
class AppDataPusherInterface:
    
    def appInitiation(self,request,app):
        result = dict()
        status = 200
        try:
            result['data'] = json.loads(SharedData.objects.get(appname=app).data)
            result['result'] = "SUCCESS"
            response = JsonResponse(result,status=status)
            response.set_cookie("dbrui-appName",app)            
        except Exception as e:
            status = 500
            result['result'] = "FAILURE"

        response['status'] = status
        return response
    
    def updatePusher(self,request):
        result = dict()
        status = 200
        try:
            app = request.COOKIES['dbrui-appName']                
            result['data'] = json.loads(SharedData.objects.get(appname=app).updated_states)
            result['result'] = "SUCCESS"
        except Exception as e:
            status = 500
            result['error'] = str(e)
            result['result'] = "FAILURE"
        
        data = "data:"+json.dumps(result)+"\n\n"
        response = HttpResponse(data)
        response['Content-Type'] = "text/event-stream"
        response['Cache-Control'] = "no-cache"
        return response