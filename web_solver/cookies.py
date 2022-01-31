try:
    import web_solver.web as web
    import requests
    import web_solver.util as util
    import utilities.finder as finder
except Exception as e:
    raise ImportError("cookies.py -> " + str(e))


def check_for_cookies_injection(all_request):
    cookies = dict()
    testing = False
    for request in all_request:
        if len(request.cookies) != 0:
            if not testing:  # just for a better log
                web.CHALLENGE.log("Testing different cookies", state=2, verbose=web.VERBOSE)
                testing = True
            c = request.cookies
            for name, value in c.items():
                if str(value) == "0":
                    cookies[name] = "1"
                elif str(value) == "1":
                    cookies[name] = "0"
                elif str(value).lower() == "true":
                    cookies[name] = "false"
                elif str(value).lower() == "false":
                    cookies[name] = "true"
                elif str(value).isalnum():
                    cookies[name] = "admin"
    if len(cookies) != 0:
        for request in all_request:
            if "Content-Type" in request.headers and request.method.upper() == "GET":
                if "text/html" in request.headers["Content-Type"].lower():
                    response = requests.get(request.url_after_potential_redirection, cookies=cookies)
                    if util.is_successful_requests(response.status_code, len(response.text),
                                                   request.url_after_potential_redirection):
                        if finder.find_flag(web.FLAG_FORMAT, response.text, web.VERBOSE, web.CHALLENGE, False):
                            web.CHALLENGE.log("Found a flag in " + request.url_after_potential_redirection +
                                              " when changing cookies into : " + str(cookies) + " !", verbose=True,
                                              state=0)
