from django.shortcuts import render
from django.http import HttpResponse,JsonResponse, request
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from pathlib import Path
import os
from django.views.decorators.csrf import csrf_exempt
import sys
import subprocess

# That's disgusting code, i should ashamed of myself
# https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944

try:
    import sys
    sys.path.insert(1, str(Path(os.path.realpath(__file__)).parents[2]))
    import os
    import utilities.finder as finder
    from pathlib import Path, PurePath
    import forensics_solver.forensics as forensics
    import stega_solver.stega as stega
    import argparse
    from utilities.utilities import log
    import utilities.ctfd_scraper as ctfd_scraper
    import web_solver.web as web_solver
    import web_solver.util as web_util
    import crypto_solver.cryptodispatcher as crypto
    from multiprocessing import Pool, cpu_count
except Exception as e:
    print("Import error : views.py -> " + str(e))
    exit(0)


def home(request):
    return render(request,"index.html")

def ctf(request):
    return render(request,"ctf.html")

class dummy_args():
    def __init__(self,flag_format,verbose,url):
        self.flag_format=flag_format
        self.verbose=verbose
        self.url=url
        self.threads=0


@csrf_exempt
def upload(request):
    if request.POST:
        try:
            path=None
            if request.FILES:
                print("Its has files")
                if len(request.FILES)==1:
                    fileToSolve = request.FILES['file']
                    path=Path(Path.joinpath(Path(settings.MEDIA_ROOT),fileToSolve.name))
                    #print(path)
                    if path.is_file():
                        os.remove(path)
                    fs = FileSystemStorage()
                    filename=fs.save(fileToSolve.name,fileToSolve)
            
            if request.POST.get("format")=="":
                raise Exception("You haven't specified a flag format")
            if (not path) and request.POST.get("url")=="" and request.POST.get("text")=="":
                raise Exception("You haven't specified any input")
            if (request.POST.get("url")!="" and request.POST.get("text")!="") or (path and request.POST.get("url")!="") or (path and request.POST.get("text")!=""):
                raise Exception("Please specify only one input")

            command="python3 ../excalibur.py --chall -i"
            command+=" --flag '"+request.POST.get("format")+"'"
            command+=" -v" if request.POST.get("verbose")=="true" else ""

            command+=" -f" if request.POST.get("forensic")=="true" else ""
            command+=" -w" if request.POST.get("web")=="true" else ""
            command+=" -c" if request.POST.get("crypto")=="true" else ""
            command+=" -s" if request.POST.get("stega")=="true" else ""

            if request.POST.get("text")!="":
                command+=" -t '"+request.POST.get("text")+"'"
            elif request.POST.get("url")!="":
                command+=" -u '"+request.POST.get("url")+"'"
            elif path:
                command+=" -p '"+str(path)+"'"
            print("##",command)
            output=subprocess.run([command],shell=True,capture_output=True)
            context={"output":output.stdout.decode(),"error":output.stderr.decode()}
            print("####",context)
            """
            # flagged_plain = False

            # If text only
            if request.POST.get("text")!="":
                challenge = ctfd_scraper.Challenge(text=request.POST.get("text"))
                flagged_plain=finder.find_flag(args.flag_format, plaintext=request.POST.get("text"),challenge=challenge)
                print(challenge)
                if not flagged_plain:
                    if request.POST.get("crypto")!="true" and request.POST.get("forensic")!="true" and request.POST.get("web")!="true" and request.POST.get("stega")!="true":
                        raise Exception("You haven't chosen any category")
                    
                    challenge = ctfd_scraper.Challenge(text=request.POST.get("text"))

                    if request.POST.get("stega")=="true":
                        stega.solve(challenge, args)

                    if request.POST.get("crypto")=="true":
                        crypto.solve(challenge, args)
            
            if path: #if file only:
                if request.POST.get("crypto")!="true" and request.POST.get("forensic")!="true" and request.POST.get("web")!="true" and request.POST.get("stega")!="true":
                    raise Exception("You haven't chosen any category")
                challenge = ctfd_scraper.Challenge(file=path)

                if request.POST.get("forensic")=="true":
                    forensics.solve(challenge, args)

                if request.POST.get("stega")=="true":
                    stega.solve(challenge, args)

                if request.POST.get("crypto")=="true":
                    crypto.solve(challenge, args)
        
            # URL and web ticked
            if request.POST.get("url")!="":
                challenge = ctfd_scraper.Challenge(text=request.POST.get("urm"))
                url = web_util.extract_url(request.POST.get("url"))
                if url is None:
                    raise Exception("Bad format for URL")
                elif not web_util.check_if_up(url):
                    raise Exception("URL not responding!")
                web_solver.Web(url, args.flag_format, args.verbose, challenge, args.threads)#ptetre mettre la var url plutot que args.url, à tester

                
            try:
                with open(challenge.notefile_path,"r") as notefile:
                    context={'output': notefile.read()}
            except:
                context={'output': "Excalibur couldn't find anything..."}
            """
        except Exception as e:
            context={'error': "Excalibur ran into an error: "+str(e)}
        
        return JsonResponse(context)
    else:
        return HttpResponse("You didn't do a POST...")

@csrf_exempt
def uploadCTF(request):
    if request.POST and len(request.POST["url"]) != 0 and len(request.POST["Login"]) != 0 and len (request.POST["Pass"]) != 0 and len(request.POST["FlagForm"]) != 0:
        try:
            print(request.POST)
            command = ["python3", "../excalibur.py", "--ctf", request.POST["url"], "--login", request.POST["Login"], "--password", request.POST["Pass"], "--flag", request.POST["FlagForm"]]
            result = subprocess.Popen(command,stdout=subprocess.PIPE)
            tosend = result.stdout.read().decode("UTF-8")
            return JsonResponse({"output" : tosend})
        except:
            return JsonResponse({"output" : "Are you sure the entered information is correct?"})


    else:
        return HttpResponse("You didn't enter a valid query")
