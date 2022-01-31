try:
    import subprocess
    import web_solver.request as request
    import web_solver.web as web
    import re
    from pathlib import *
    import sys
    import os
    sys.path.insert(1, str(Path(os.path.realpath(__file__)).parents[1]))
except Exception as e:
    raise ImportError("csp.py -> " + str(e))


def check_for_csp_headers(all_requests):
    web.CHALLENGE.log("checking for CSP vulnerabilities", state=2, verbose=True)
    for r in all_requests:
        if "Content-Security-Policy" in r.headers:
            vulns = use_csp_evaluator(r.headers["Content-Security-Policy"])
            if vulns is not None:
                web.CHALLENGE.log("there is a CSP vulnerability, check it out !\n```json\n" + vulns + "```\n", state=0,
                                  verbose=True)
                break


def use_csp_evaluator(csp_header):
    directory = Path(__file__).parent.absolute()
    with open(str(directory) + '/csp.js', 'r') as file:
        data = file.readlines()

    data[4] = "var rawCsp = \"" + csp_header + "\";\n"

    with open(str(directory) + '/csp.js', 'w') as file:
        file.writelines(data)

    output = str(subprocess.run("node " + str(directory) + "/csp.js", capture_output=True, text=True, shell=True).stdout)
    severity = re.findall(r"severity: ([^,]*)", output)
    if len([i for i in ["10", "30", "40", "50"] if i in severity]) != 0:
        return output
    else:
        return None
