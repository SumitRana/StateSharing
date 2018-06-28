// Author : Sumit | Sam
let dbruiClient = (function(){
    var instance = null;
    var StateManager = function(){

    }

    return {
        getClient = function(){
            if(instance != null){
                return instance;
            }
            else{
                instance = new StateManager();
                return instance;
            }
        }
    }
})();

// OR

let globalState = {};

let StateManager = new function(){
    this.source = null;
    this.protocol = "http";
    this.host = null;
    this.port = 80;
    this.appName = null;
    this.listener = null;

    this.addUpdateListener = function(listener){
        this.listener = listener;
    };

    this.registerSource = function(){
        this.source = new EventSource(this.protocol+"://"+this.host+":"+this.port+"/"+this.appName+"/");
        this.source.addEventListener('message',messageListener);
    };

    this.messageListener = function(e){
        var data = JSON.parse(e.data);
        
        // At Last - After Updation
        if(this.listener != null){
            listener();
        }
    };
    
    this.addHandler = function(list){
        let i = 0;
        for(i=0;i<list.length;i++){
            let temp = globalState;
            let paths = list[i].path.split(">")
            for(k=0;k<paths.length-1;k++){
                temp = temp[paths[k].toString()];
            } 
            temp[paths[paths.length]] = list[i].value;
        }
    };

    this.deleteHandler = function(list){
        let i = 0;
        for(i=0;i<list.length;i++){
            let temp = globalState;
            let paths = list[i].path.split(">")
            for(k=0;k<paths.length-1;k++){
                temp = temp[paths[k].toString()];
            } 
            delete temp[paths[paths.length]];
        }
    };

    this.modifyHandler = function(list){
        let i = 0;
        for(i=0;i<list.length;i++){
            let temp = globalState;
            let paths = list[i].path.split(">")
            for(k=0;k<paths.length-1;k++){
                temp = temp[paths[k].toString()];
            } 
            temp[paths[paths.length]] = list[i].value;
        }
    };
    
};