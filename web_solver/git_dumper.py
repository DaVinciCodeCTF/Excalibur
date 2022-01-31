"""

Python implementation of https://github.com/internetwache/GitTools/

"""
try:
    import os
    import requests
    import re
    import zlib
    from binascii import hexlify
    import web_solver.web as web
    from pathlib import Path
    from threading import Thread
    from queue import Queue, Empty
    import utilities.finder as finder
    import time
except Exception as e:
    raise ImportError("git_dumper.py -> " + str(e))


class Worker(Thread):

    def __init__(self, queue):
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.running = True

    def terminate(self):
        self.running = False

    def run(self):
        while self.running:
            if not self.queue.empty():
                try:
                    url, git_dumper, file = self.queue.get(timeout=1)
                    self.download_item(url, git_dumper, file)
                    self.queue.task_done()
                except Empty:
                    return
                except Exception as e:
                    self.queue.task_done()

    def download_item(self, url, git_dumper, file):
        full_url = url + file
        hashes = list()
        packs = list()

        target = str(Path.joinpath(git_dumper.directory, file))

        # Si le fichier est deja telecharge, on s'arrete
        if file in git_dumper.DOWNLOADED:
            return

        res = re.findall(r"^(.*)[/|\\]", target)
        temp = None
        if len(res) > 0:
            temp = res[0]

        if not os.path.exists(target) and temp is not None:
            os.makedirs(temp, exist_ok=True)

        git_dumper.DOWNLOADED.append(file)

        try:
            req = requests.get(full_url, timeout=1)
        except requests.Timeout:
            web.CHALLENGE.log("Git dumper TimeOut -> " + full_url, state=4, verbose=web.VERBOSE)
            return

        # Si la page n'existe pas, on s'arrete
        if str(req.status_code)[0] == "4":
            return

        f = open(target, 'wb')
        f.write(req.content)
        f.close()

        if not os.path.exists(target):
            web.CHALLENGE.log('Error while downloading {}'.format(file), verbose=web.VERBOSE, state=4)
            return

        web.CHALLENGE.log('Git file {} was downloaded successfully'.format(file), verbose=web.VERBOSE, state=2)

        if len(re.findall(r"[a-f0-9]{2}/[a-f0-9]{38}", file)) > 0:
            try:
                compressed = open(target, 'rb').read()
                decompressed = zlib.decompress(compressed)

                decompressed_file = open(target + ".txt", 'wb')
                decompressed_file.write(decompressed)
                decompressed_file.close()

                if decompressed.startswith(b'blob') or decompressed.startswith(b'commit'):
                    decompressed = str(decompressed)
                    hashes.extend(re.findall(r"([a-f0-9]{40})", decompressed))
                else:
                    res = re.findall(b'\d+ .*?\x00(.{20})', decompressed, re.MULTILINE)
                    for hash in res:
                        hashes.append(hexlify(hash).decode("utf-8"))
                    decompressed = str(hexlify(decompressed))
                    hashes.extend(re.findall(r"00([a-f0-9]{40})", decompressed))
            except:
                return

        # On regarde si le fichier contient des references d'objets
        with open(target, 'r') as f:
            try:
                lines = f.readlines()
                for line in lines:
                    hashes.extend(re.findall(r"([a-f0-9]{40})", line))
                    packs.extend(re.findall(r"(pack-[a-f0-9]{40})", line))
            except:
                pass

        if len(re.findall(r"objects[/|\\][a-f0-9]{2}", target)) > 0:
            with open(target + ".txt", 'r') as f:
                try:
                    if finder.find_flag(web.FLAG_FORMAT, ''.join(f.readlines()), web.VERBOSE, web.CHALLENGE,
                                        False):
                        web.CHALLENGE.log("Found a flag in git_dumper !", verbose=web.VERBOSE, no_verbose_output="",
                                          state=0)
                except:
                    pass
        else:
            with open(target, 'r') as f:
                try:
                    if finder.find_flag(web.FLAG_FORMAT, ''.join(f.readlines()), web.VERBOSE, web.CHALLENGE,
                                        False):
                        web.CHALLENGE.log("Found a flag in git_dumper !", verbose=web.VERBOSE, no_verbose_output="",
                                          state=0)
                except:
                    pass

        for hash in hashes:
            self.queue.put((url, git_dumper, 'objects/{}/{}'.format(hash[0:2], hash[2:])), timeout=1)
        for pack in packs:
            self.queue.put((url, git_dumper, 'objects/pack/{}.pack'.format(pack)), timeout=1)
            self.queue.put((url, git_dumper, 'objects/pack/{}.idx'.format(pack)), timeout=1)


class GitDumper:

    def __init__(self, web_, threads):
        self.web_ = web_
        self.threads = threads
        self.directory = Path.joinpath(web.CHALLENGE.directory, "git_dumper")
        self.threads = threads
        self.QUEUE = None
        self.TO_DOWNLOAD = None
        self.DOWNLOADED = None

    def dump(self):
        url = self.check_if_git_directory_exist()
        if url is not None:
            web.CHALLENGE.log("dumping git repository at : " + url, state=2,
                              no_verbose_output="dumping git repository at : " + url)
            self.download(url)
    
    def check_if_git_directory_exist(self):
        try:
            url = self.web_.completeUrl
            response = requests.get(url + "/.git", timeout=1)
            if str(response.status_code)[0] == "2" or response.status_code == 403:
                return response.url
        except requests.Timeout:
            pass
        return None

    def clean(self):
        objects_dir = Path.joinpath(self.directory, Path('objects/'))
        try:
            dirs = os.listdir(str(objects_dir))
            for dir in dirs:
                temp_dir = Path.joinpath(objects_dir, Path(dir))
                if len(os.listdir(str(temp_dir))) == 0:
                    os.rmdir(str(temp_dir))
        except FileNotFoundError:
            pass

    def download(self, url):
        self.QUEUE = Queue()
        self.TO_DOWNLOAD = list()
        self.DOWNLOADED = list()

        self.TO_DOWNLOAD.append('HEAD')
        self.TO_DOWNLOAD.append('objects/info/packs')
        self.TO_DOWNLOAD.append('description')
        self.TO_DOWNLOAD.append('config')
        self.TO_DOWNLOAD.append('COMMIT_EDITMSG')
        self.TO_DOWNLOAD.append('index')
        self.TO_DOWNLOAD.append('packed-refs')
        self.TO_DOWNLOAD.append('refs/heads/master')
        self.TO_DOWNLOAD.append('refs/remotes/origin/HEAD')
        self.TO_DOWNLOAD.append('refs/stash')
        self.TO_DOWNLOAD.append('logs/HEAD')
        self.TO_DOWNLOAD.append('logs/refs/heads/master')
        self.TO_DOWNLOAD.append('logs/refs/remotes/origin/HEAD')
        self.TO_DOWNLOAD.append('info/refs')
        self.TO_DOWNLOAD.append('info/exclude')
        self.TO_DOWNLOAD.append('refs/wip/index/refs/heads/master')
        self.TO_DOWNLOAD.append('refs/wip/wtree/refs/heads/master')

        workers = list()
        for x in range(self.threads):
            worker = Worker(self.QUEUE)
            worker.start()
            workers.append(worker)

        while self.TO_DOWNLOAD:
            self.QUEUE.put((url, self, self.TO_DOWNLOAD.pop()), timeout=1)

        # Ajouté afin de pouvoir Ctrl-C
        while True:
            if not self.QUEUE.empty():
                time.sleep(1)
            else:
                break
            
        self.QUEUE.join()

        for worker in workers:
            worker.terminate()

        self.clean()
