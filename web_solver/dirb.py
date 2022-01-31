try:
    import requests
    import re
    import time
    from web_solver.request import Request
    import web_solver.util as util
    import web_solver.web as web
    from threading import Thread
    from queue import Queue, Empty
    from pathlib import *
    import sys
    import os
    sys.path.insert(1, str(Path(os.path.realpath(__file__)).parents[1]))
except Exception as e:
    raise ImportError("dirb.py -> " + str(e))


class Worker(Thread):
    def __init__(self, dirb):
        Thread.__init__(self, daemon=True)
        self.dirb = dirb
        self.queue = self.dirb.queue
        self.running = True

    def terminate(self):
        self.running = False

    def run(self):
        while self.running:
            if not self.queue.empty():
                try:
                    url = self.queue.get(timeout=1)
                    url = url.replace('\n', '')
                    if not re.findall(r"https?:/", url):
                        url = self.dirb.domain + url
                    domain = util.get_domain(url)
                    if (not self.dirb.url_already_test(url)) and domain == self.dirb.domain:
                        self.dirb.try_url(
                            url, self.dirb.get_method_allowed(url), domain)
                    self.queue.task_done()
                except Empty:
                    return
                except Exception as e:
                    self.queue.task_done()


class Dirb:
    DEFAULT_METHOD = ["GET", "POST"]
    BACKUP_EXTENSIONS = [".backup", ".bck", ".old", ".save", ".bak", ".sav", "~", ".copy", ".old", ".tmp", ".txt",
                         ".back", ".bkp", ".bac", ".tar", ".gz", ".tar.gz", ".zip", ".rar"]

    def __init__(self, base_url, timeout, thread, delay):
        self.base_url = base_url
        self.domain = util.get_domain(base_url)
        if self.domain is None:
            web.CHALLENGE.log("Can't find domain for URL : " + base_url, state=4, verbose=True)
            exit(0)
        self.timeout = timeout
        self.thread = thread
        self.delay = delay
        self.all_request_done = list()

        # self.queue = [base_url] -> Remplacé par to_download dans scan()
        self.queue = Queue()

    def scan(self):
        web.CHALLENGE.log("starting scan for " + self.base_url, state=2, verbose=web.VERBOSE,
                          no_verbose_output="starting scan for " + self.base_url)
        to_download = list()
        to_download.append(self.base_url)
        directory = Path(__file__).parent.absolute()
        with open(str(directory) + '/common_url.txt', 'r') as file:
            for line in file.readlines():
                if self.base_url[-1] != "/":
                    to_download.append(self.base_url + "/" + line)
                else:
                    to_download.append(self.base_url + line)

        workers = list()
        for x in range(self.thread):
            worker = Worker(self)
            worker.start()
            workers.append(worker)

        while to_download:
            self.queue.put((to_download.pop()), timeout=1)

        # Ajouté afin de pouvoir Ctrl-C
        while True:
            if not self.queue.empty():
                time.sleep(1)
            else:
                break

        self.queue.join()

        for worker in workers:
            worker.terminate()

        return self.keep_only_successful_requests()

    def try_url(self, url, methods, domain):
        for method in methods:
            web.CHALLENGE.log(url + " -> " + method,
                              state=2, verbose=web.VERBOSE)

            req = Request(url, method, domain, self.timeout)

            self.all_request_done.append(req)

            for ressource in req.ressources:
                self.queue.put(ressource, timeout=1)

            if req.backup and req.is_successful:
                self.backup_file(req.url_after_potential_redirection)

            time.sleep(self.delay)

    def backup_file(self, url):
        url = util.remove_all_get_parameters_in_url(url)

        if url[-1] != "/" and url + "/" != self.domain:
            for extension in Dirb.BACKUP_EXTENSIONS:
                self.queue.put((url + extension), timeout=1)

    def get_method_allowed(self, url):
        default = Dirb.DEFAULT_METHOD
        if util.is_backup(url):
            default = ["GET"]
        try:
            req = requests.options(url, timeout=self.timeout)
        except requests.Timeout:
            req = None
            web.CHALLENGE.log(url + " -> OPTIONS : TimeOut",
                              verbose=web.VERBOSE, state=4)
        if req is None or req.status_code != 200:
            return default
        if 'Allow' in req.headers:
            a = req.headers['Allow'].replace(" ", "")
            allowed = a.split(',')
            if "OPTIONS" in allowed:
                allowed.remove("OPTIONS")
            allowed = list(set(allowed))
            return allowed
        else:
            return default

    def url_already_test(self, url):
        already_test = False
        for r in self.all_request_done:
            if r.base_url == url or r.url_after_potential_redirection == url:
                already_test = True
                break
        return already_test

    def keep_only_successful_requests(self):
        successful_requests = list()
        for r in self.all_request_done:
            if r.is_successful:
                successful_requests.append(r)

        return successful_requests

