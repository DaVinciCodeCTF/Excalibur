# <editor-fold desc="Import">
try:
    from utilities.ctfd_scraper import Challenge
    CHALLENGE: Challenge = None
    VERBOSE = False
    TO_ANALYZE = ""
    FLAG_FORMAT = ""
    FLAGS = list()
    from web_solver.dirb import Dirb
    from web_solver.request import Request
    import web_solver.sql_injection as sql_injection
    from pathlib import Path
    import utilities.finder as finder
    from web_solver.git_dumper import GitDumper
    import web_solver.csp.csp as csp
    import web_solver.jwt as jwt
    import web_solver.cookies as cookies
except Exception as e:
    raise ImportError("web.py -> " + str(e))
# </editor-fold>


class Web:

    def __init__(self, base_url, flag_format, verbose, challenge: Challenge, threads=1):
        self.completeUrl = base_url
        global FLAG_FORMAT
        FLAG_FORMAT = flag_format
        global VERBOSE
        VERBOSE = verbose
        global CHALLENGE
        CHALLENGE = challenge
        global TO_ANALYZE
        TO_ANALYZE = ""
        self.threads = 1 if threads <= 0 else threads

        self.allRequest = list()

        self.solve()

    def solve(self):
        scanner = Dirb(self.completeUrl, 1, self.threads, 0.5)
        self.allRequest += scanner.scan()

        git_dumper = GitDumper(self, self.threads)
        git_dumper.dump()

        sql_injection.use_sql_map(self.allRequest, self.threads)

        csp.check_for_csp_headers(self.allRequest)

        cookies.check_for_cookies_injection(self.allRequest)

        self.markdown()

        if TO_ANALYZE != "":
            if finder.find_flag(FLAG_FORMAT, TO_ANALYZE, VERBOSE, CHALLENGE, False):
                CHALLENGE.log("Found a flag !", verbose=True, state=0)

    '''
    def scan_output(self, scan_result):
        file = codecs.open(Path.joinpath(CHALLENGE.directory, "scan.txt"), "w+", "utf-8")
        file.write(scan_result)
        file.close()
    '''

    def markdown(self):
        file = open(Path.joinpath(CHALLENGE.directory, "overview.md"), "w+")
        for r in self.allRequest:
            file.write("#### " + r.url_after_potential_redirection + " (" + r.method + " -> " + str(r.response_code) +
                       ")\n")
            for r2 in r.ressources:
                file.write("- " + r2 + "\n")

        file.close()
