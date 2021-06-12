from json import loads,dumps,load
import argparse
import os
import sys
import requests

remote_server_url="http://mvdb-db.herokuapp.com/"
parser=argparse.ArgumentParser(
    prog="mvdb",
    usage="%(prog)s operation [options]",
    description="movie links database management toolset"
)

parser.add_argument("operation",help="type of operation that you want to run. [add,get,update,remove,init,list,search,rename,remote]",action="store")
parser.add_argument("-n","--name",help="specifies the name of the series or movie.",action="store")
parser.add_argument("-y","--year",help="specifies the year of release",action="store")
parser.add_argument("--sd",help="specifies the link for 480p media.",action="store")
parser.add_argument("--hd",help="specifies the link for 720p media.",action="store")
parser.add_argument("--fhd",help="specifies the link for 1080p media.",action="store")
parser.add_argument("--qhd",help="specifies the link for 1440p media.",action="store")
parser.add_argument("--uhd",help="specifies the link for 2160p media.",action="store")
parser.add_argument("--aio",help="specifies the link for all formats",action="store")
parser.add_argument("-f","--force",help="over writes the data if new media already existed.",action="store_true")
parser.add_argument("-i","--interactive",help="launches the app in Interactive mode",action="store_true")
parser.add_argument("--db",help="specifies the db file. default is `data.json`",action="store")
parser.add_argument("--newname",help="optional value required for rename operation",action="store")
parser.add_argument("--removeold",help="optional flag required for rename operation",action="store_true")
parser.add_argument("--checkupdate",help="optional flag for remote operation",action="store_true")
parser.add_argument("--update",help="optional flag for remote operation for updating the local database.",action="store_true")
parser.add_argument("--getdb",help="optional flag for remote operation for updating the local database to the given value",action="store")
parser.add_argument("--listall",help="optional flag for remote operation for listing all versions available on server.",action="store_true")
args=parser.parse_args()





def LoadJSONDb(conf):
    if conf.db==None:
        if os.path.exists(os.path.abspath("./data.json")):
            with open("./data.json") as f:
                return loads(f.read())
        else:
            print("[Error] No Database file found in this directory. Try to run `init` operation on this directory.")
            sys.exit(1)
    else:
        if os.path.exists(os.path.abspath(conf.db)):
            with open(os.path.abspath(conf.db)) as f:
                return loads(f.read())
        else:
            print("[Error] Database file `{}` doesn't exists.")
            sys.exit(1)

def DumpJSONDb(conf,data):
    with open("./meta.json") as f:
        meta=load(f)
    
    if conf.db==None:
        with open("./data.json","w") as f:
            f.write(dumps(data))
        meta["changed"]=True
        with open("./meta.json","w") as f:
            f.write(dumps(meta,indent=2))
    else:
        with open(os.path.abspath(conf.db),"w") as f:
            f.write(dumps(data))





def LaunchInteractiveMode(conf):
    if conf.operation=="add":
        InteractiveAdd(conf)
    elif conf.operation=="update":
        InteractiveUpdate(conf)
    elif conf.operation=="get":
        InteractiveGet(conf)
    elif conf.operation=="remove":
        InteractiveRemove(conf)
    else:
        print("[Error] operation `{}` is not a valid operation.".format(args.operation))
        parser.print_help()

def get(field,required):
    value=str(input("{}: ".format(field)))
    if value.strip()=="":
        if required:
            print("{} can't be empty.".format(field))
            return get(field,required)
        else:
            return None
    return value

def InteractiveAdd(conf):
    db=LoadJSONDb(conf)
    name=get("Name",True).strip()
    if name in db.keys() and not conf.force:
        print("[Error] Name `{}` already exists in the database.".format(name))
        sys.exit(1)
    
    year=get("Year [leave empty if unknown]",False)
    aiolink=get("AIO link[leave empty if unknown]",False)
    sdlink=get("480p link[leave empty if unknown]",False)
    hdlink=get("720p link[leave empty if unknown]",False)
    fhdlink=get("1080p link[leave empty if unknown]",False)
    qhdlink=get("1440p link[leave empty if unknown]",False)
    uhdlink=get("2160p link[leave empty if unknown]",False)
    
    if sdlink==None and hdlink==None and fhdlink==None and qhdlink==None and uhdlink==None and aiolink==None:
        print("[Warning] No link given. Operation terminated.")
        sys.exit(0)
    db[name]={
        "year":year,
        "links":{
            "480p":sdlink,
            "720p":hdlink,
            "1080p":fhdlink,
            "1440p":qhdlink,
            "2160p":uhdlink,
            "aio":aiolink
        }
    }
    DumpJSONDb(conf,db)
    print("[DONE] Added `{}` successfully to the database.".format(name))


def InteractiveUpdate(conf):
    db=LoadJSONDb(conf)
    name=get("Name",True).strip()
    if not (name in db.keys()):
        print("[Error] Name `{}` doesn't exist in the database. Can't update something that is unavailable.".format(name))
        sys.exit(1)
    
    year=get("Year [{}]".format(db[name]["year"]),False)
    aiolink=get("AIO link[{}]".format(db[name]["links"]["aio"]),False)
    sdlink=get("480p link[{}]".format(db[name]["links"]["480p"]),False)
    hdlink=get("720p link[{}]".format(db[name]["links"]["720p"]),False)
    fhdlink=get("1080p link[{}]".format(db[name]["links"]["1080p"]),False)
    qhdlink=get("1440p link[{}]".format(db[name]["links"]["1440p"]),False)
    uhdlink=get("2160p link[{}]".format(db[name]["links"]["2160p"]),False)
    
    db2={
        "year":year,
        "links":{
            "480p":sdlink or db[name]["links"]["480p"],
            "720p":hdlink or db[name]["links"]["720p"],
            "1080p":fhdlink or db[name]["links"]["1080p"],
            "1440p":qhdlink or db[name]["links"]["1440p"],
            "2160p":uhdlink or db[name]["links"]["2160p"],
            "aio":aiolink or db[name]["links"]["aio"]
        }
    }
    db[name]=db2
    DumpJSONDb(conf,db)
    print("[DONE] Successfully updated `{}`.".format(name))


def InteractiveRemove(conf):
    db=LoadJSONDb(conf)
    name=get("Name",True).strip()
    if not (name in db.keys()):
        print("[Error] Name `{}` doesn't exist in the database. Can't remove something that is unavailable.".format(name))
        sys.exit(1)
    del db[name]
    DumpJSONDb(conf,db)
    print("[DONE] Successfully removed `{}` from the database".format(name))

def InteractiveGet(conf):
    db=LoadJSONDb(conf)
    name=get("Name",True).strip()
    if not(name in db.keys()):
        print("[Error] Name `{}` was not found in database.".format(name))
        sys.exit(0)
    
    print("Name: ",name)
    print("Year: ",db[name]["year"] or "Unknown")
    print("Links: ")
    print("      480p:  ",db[name]["links"]["480p"] or "Unavailable")
    print("      720p:  ",db[name]["links"]["720p"] or "Unavailable")
    print("      1080p: ",db[name]["links"]["1080p"] or "Unavailable")
    print("      1440p: ",db[name]["links"]["1440p"] or "Unavailable")
    print("      2160p: ",db[name]["links"]["2160p"] or "Unavailable")
    print("      AIO:   ",db[name]["links"]["aio"] or "Unavailable")
    print("Software Developed by Nur Mahmud Ul Alam Tasin.")


def AddToDB(conf):
    if conf.name==None:
        print("[Error] Must provide a name.")
        sys.exit(1)
    db=LoadJSONDb(conf)
    if conf.name in db.keys() and not conf.force:
        print("[Error] Name `{}` already exists in the database.".format(name))
        sys.exit(1)
    if conf.sd==None and conf.hd==None and conf.fhd==None and conf.qhd==None and conf.fhd==None and conf.aio==None:
        print("[Warning] No link given. Operation terminated.")
        sys.exit(0)
    db[conf.name]={
        "year":conf.year,
        "links":{
            "480p":conf.sd,
            "720p":conf.hd,
            "1080p":conf.fhd,
            "1440p":conf.qhd,
            "2160":conf.uhd,
            "aio":conf.aio
        }
    }
    DumpJSONDb(conf,db)
    print("[DONE] Added `{}` successfully to the database.".format(conf.name))



def UpdateDB(conf):
    if conf.name==None:
        print("[Error] Must provide a name.")
        sys.exit(1)
    db=LoadJSONDb(conf)
    if not (conf.name in db.keys()):
        print("[Error] Name `{}` doesn't exist in the database. Can't update something that is unavailable.".format(conf.name))
        sys.exit(1)
    db2={
        "year":year,
        "links":{
            "480p":conf.sd or db[conf.name]["links"]["480p"],
            "720p":conf.hd or db[conf.name]["links"]["720p"],
            "1080p":conf.fhd or db[conf.name]["links"]["1080p"],
            "1440p":conf.qhd or db[conf.name]["links"]["1440p"],
            "2160p":conf.uhd or db[conf.name]["links"]["2160p"],
            "aio":conf.aio or db[conf.name]["links"]["aio"]
        }
    }
    db[conf.name]=db2
    DumpJSONDb(conf,db)
    print("[DONE] Successfully updated `{}`.".format(conf.name))

def GetFromDB(conf):
    if conf.name==None:
        print("[Error] Must provide a name.")
        sys.exit(1)
    db=LoadJSONDb(conf)
    if not (conf.name in db.keys()):
        print("[Error] Name `{}` doesn't exist in the database.".format(conf.name))
        sys.exit(1)
    print("Name: ",conf.name)
    print("Year: ",db[conf.name]["year"] or "Unknown")
    print("Links: ")
    print("      480p:  ",db[conf.name]["links"]["480p"] or "Unavailable")
    print("      720p:  ",db[conf.name]["links"]["720p"] or "Unavailable")
    print("      1080p: ",db[conf.name]["links"]["1080p"] or "Unavailable")
    print("      1440p: ",db[conf.name]["links"]["1440p"] or "Unavailable")
    print("      2160p: ",db[conf.name]["links"]["2160p"] or "Unavailable")
    print("      AIO:   ",db[conf.name]["links"]["aio"] or "Unavailable")
    print("Software Developed by Nur Mahmud Ul Alam Tasin.")


def RemoveFromDB(conf):
    if conf.name==None:
        print("[Error] Must provide a name.")
        sys.exit(1)
    db=LoadJSONDb(conf)
    if not (conf.name in db.keys()):
        print("[Error] Name `{}` doesn't exist in the database.".format(conf.name))
        sys.exit(1)
    del db[conf.name]
    DumpJSONDb(conf,db)
    print("[DONE] `{}` removed successfully from the database.".format(conf.name))
    
def Init(conf):
    if os.path.exists(os.path.abspath("./data.json")):
        print("[Warning] Database file exists in this directory.")
    else:
        print("Creating the database....")
        with open(os.path.abspath("./data.json"),"a+") as f:
            f.write(dumps({}))
        print("[Done] File Created at {} successfully.".format(os.path.abspath("./data.json")))
    
    if os.path.exists(os.path.abspath("./meta.json")):
        print("[Warning] Metadata file exists in this directory.")
    else:
        print("Creating the metadata....")
        with open(os.path.abspath("./meta.json"),"a+") as f:
            f.write(dumps({"current_version":"0.0.0","changed":False}))
        print("[Done] File Created at {} successfully.".format(os.path.abspath("./meta.json")))
    
def ListDB(conf):
    db=LoadJSONDb(conf)
    count=1
    dbkeys=list(db.keys())
    for name in dbkeys:
        print("{}. {} | {}".format(count,name,db[name]["year"] or "Unknown"))
        count+=1

def SearchDB(conf):
    db=LoadJSONDb(conf)
    if conf.name==None:
        print("[Error] Search query must be passed by --name flag.")
        sys.exit(1)
    found=[]
    dbkeys=list(db.keys())
    dbkeys.sort()
    for each in dbkeys:
        if conf.name.lower() in each.lower():
            found.append((each,db[each]["year"]))
    if len(found)>0:
        counter=1
        print("Total {} results found".format(len(found)))
        for each in found:
            print("{}. {} | {}".format(counter,each[0],each[1]))
            counter+=1
        sys.exit(0)
    print("No results found.")
    sys.exit(0)

def RenameDB(conf):
    if conf.name==None:
        print("[Error] Old Field name must be passed via --name flag")
        sys.exit(1)
    db=LoadJSONDb(conf)
    if not conf.name in db.keys():
        print("[Error] The name `{}` doesn't exists.".format(conf.name))
        sys.exit(1)
    if conf.newname==None:
        print("[Error] --newname not given.")
        sys.exit(1)
    db[conf.newname]=db[conf.name]
    if conf.removeold:
        del db[conf.name]
    DumpJSONDb(conf,db)
    print("[DONE] `{}` renamed to `{}` successfully.".format(conf.name,conf.newname))

def CheckUpdateDB(conf):
    with open("./meta.json") as f:
        meta=load(f)
    update_check=requests.post(remote_server_url+"check/",json={
        "version":meta["current_version"]
    },timeout=10)
    if update_check.status_code == 200:
        if update_check.json()["updateAvailable"]:
            print(update_check.json()["msg"])
        else:
            print(update_check.json()["msg"])
    else:
        print("Update Checking Failed.")

def RemoteUpdateDBCore(conf):
    with open("./meta.json") as f:
        meta=load(f)
    if meta["changed"]:
        choice=str(input("Changes were made to your local database. Updating it may lose your changes. Do you want to continue anyway?[Y/N]")).lower()
        if choice=="n":
            print("Canceling update....")
            sys.exit(0)
    dbFileContent=requests.get(remote_server_url+"get/",timeout=10)
    if dbFileContent.status_code==200:
        return dbFileContent.text
    else:
        print("Updating Database Failed!!")
        sys.exit(1)


def RemoteUpdateDBSafe(conf):
    with open("./meta.json") as f:
        meta=load(f)
    
    update_check=requests.post(remote_server_url+"check/",json={
        "version":meta["current_version"]
    },timeout=10)
    if update_check.status_code == 200:
        if update_check.json()["updateAvailable"]:
            content=RemoteUpdateDBCore(conf)
            with open("./data.json","w") as f:
                f.write(content)
            meta["current_version"]=update_check.json()["available_version"]
            meta["changed"]=False
            with open("./meta.json","w") as f:
                f.write(dumps(meta,indent=2))
            print("Updated Database successfully.")
            sys.exit(0)
            
        else:
            if meta["changed"]:
                content=RemoteUpdateDBCore(args)
                with open("./data.json",'w') as f:
                    f.write(content)
                meta["changed"]=False
                with open('./meta.json','w') as f:
                    f.write(dumps(meta,indent=2))
                print("Updated Database successfully.")
                sys.exit(0)
            else:
                print(update_check.json()["msg"])
    else:
        print("Update Checking Failed.")
        sys.exit(1)

def RemoteListVersions(conf):
    availableVers=requests.get(remote_server_url+"list/",timeout=10)
    if availableVers.status_code==200:
        counter=1
        for ver in availableVers.json()["versions"]:
            print("{}. {}".format(counter,ver))
            counter+=1
        sys.exit(0)
    else:
        print("[Error] Unable to fetch data")
        sys.exit(1)

def RemoteUpdateDBExactVersion(conf):
    with open("./meta.json") as f:
        meta=load(f)
    if meta["changed"]:
        choice=str(input("Changes were made to your local database. Updating it may lose your changes. Do you want to continue anyway?[Y/N]")).lower()
        if choice=="n":
            print("Canceling update....")
            sys.exit(0)
    
    if conf.getdb==meta["current_version"] and not conf.force and not meta["changed"]:
        print("You already have that version.")
        sys.exit(0)
    dbContent=requests.post(remote_server_url+"versions/",json={
        "version":conf.getdb
    })
    if dbContent.status_code==404:
        print("[Error] Version {} doesn't exists on the remote server.".format(conf.getdb))
        sys.exit(1)
    if dbContent.status_code==200:
        with open("./data.json","w") as f:
            f.write(dbContent.text)
        meta["current_version"]=conf.getdb
        meta["changed"]=False
        with open("./meta.json","w") as f:
            f.write(dumps(meta,indent=2))
        print("Database switched to version {}".format(conf.getdb))
        sys.exit(0)
    
    print("[Error] Couldn't switch database to version {}. Unknown Error.".format(conf.getdb))
    sys.exit(1)


if __name__=="__main__":
    if args.interactive:
        LaunchInteractiveMode(args)
    else:
        if args.operation=="add":
            AddToDB(args)
        elif args.operation=="update":
            UpdateDB(args)
        elif args.operation=="get":
            GetFromDB(args)
        elif args.operation=="remove":
            RemoveFromDB(args)
        elif args.operation=="init":
            Init(args)
        elif args.operation=="list":
            ListDB(args)
        elif args.operation=="search":
            SearchDB(args)
        elif args.operation=="rename":
            RenameDB(args)
        elif args.operation=="remote":
            if args.checkupdate:
                try:
                    CheckUpdateDB(args)
                except:
                    print("[Error] Connection wasn't eshtablished! Connect to the internet and try again.")
                    sys.exit(1)
            elif args.update:
                try:
                    RemoteUpdateDBSafe(args)
                except Exception as e:
                    print("[Error] Connection wasn't eshtablished! Connect to the internet and try again.")
                    print(e)
                    sys.exit(1)
            elif args.listall:
                try:
                    RemoteListVersions(args)
                except Exception as f:
                    print("[Error] Connection wasn't eshtablished! Connect to the internet and try again.")
                    sys.exit(1)
            
            elif not args.getdb == None:
                try:
                    RemoteUpdateDBExactVersion(args)
                except Exception as e:
                    print("[Error] Connection wasn't eshtablished! Connect to the internet and try again.")
                    sys.exit(1)
            else:
                print("[Error] Remote operation requires atleast one optional flag")
        else:
            print("[Error] operation `{}` is not a valid operation.".format(args.operation))
            parser.print_help()