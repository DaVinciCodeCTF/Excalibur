try:
    import requests
    from bs4 import BeautifulSoup
    import json
    import re
    from web_solver.form import Form
    import web_solver.web as web
    import web_solver.util as util
    import web_solver.jwt as jwt
    import utilities.finder as finder
except Exception as e:
    raise ImportError("request.py -> " + str(e))


def css_parser(text):
    if text is not None and len(text) != 0:
        # url(...)
        return re.findall(r"url\s*\(\s*[\"']?([^)\" '\n]*)", text) + link_finder(text)
    else:
        return []


def js_parser(text):
    if text is not None and len(text) != 0:
        links = link_finder(text)
        # webpack .map
        links += re.findall(r"sourceMappingURL\s*=\s*([^)\"' \n]*)", text)
        return links
    else:
        return []


def link_finder(text):
    if text is not None and len(text) != 0:
        # http.://
        return re.findall(r"http[s]?://[^)\"' \n]*", text)
    else:
        return []


def get_cookies(cookies):
    res = ""
    for name, value in cookies.items():
        res += name + " : " + value + "\n"
    return res


def get_source_code(response):
    source_code = ""
    if "Content-Type" in response.headers and "image" not in response.headers["Content-Type"].lower():
        source_code = response.text
    return source_code


def get_headers(response):
    headers = response.headers
    res = ""
    for name, value in headers.items():
        res += name + " : " + value + "\n"
    return res


def get_json(response):
    j = json.dumps(response.json()) + "\n"
    return j


def soup(text):
    return BeautifulSoup(text, "lxml")


def html_parser(s, html_text):
    links = list()

    # TODO :srcset and archive may have multiple url, case not implemented
    attributs = ["href", "codebase", "cite", "background", "action", "longdesc", "src",
                 "profile", "usemap", "classid", "data", "formaction", "icon", "manifest",
                 "poster", "srcset", "archive"]

    for link in s.find_all(["link", "a", "applet", "area", "base", "blockquote", "body",
                            "del", "form", "frame", "head", "iframe", "img", "input", "ins",
                            "link", "object", "q", "script", "audio", "button", "command",
                            "embed", "html", "input", "source", "track", "video"]):
        for att in attributs:
            links.append(link.get(att))

    for tag in s.find_all():
        if tag.get("style") is not None:
            links += css_parser(tag.get("style"))

    for css in s.find_all("style"):
        links += css_parser(css.string)

    for js in s.find_all("script"):
        links += js_parser(js.string)

    links += link_finder(html_text)
    return links


def get_all_responses(response):
    responses = [response]
    return responses + response.history


def get_request_content(response):
    content = ""
    for r in get_all_responses(response):
        content += get_headers(r)
        content += get_cookies(response.cookies.get_dict())
        if "Content-Type" in r.headers and r.headers["Content-Type"] == "application/json":
            content += get_json(r)
        else:
            content += get_source_code(r)

    return content


class Request:

    def __init__(self, url, method, domain, timeout):
        self.base_url = url
        self.timeout = timeout
        self.method = method
        self.domain = domain
        self.ressources = list()
        self.forms = list()
        response = self.get_method()
        self.raw_data_size = len(response.text) if response is not None else 0
        self.headers = response.headers if response is not None else []
        self.cookies = response.cookies.get_dict() if response is not None else {}
        self.url_after_potential_redirection = response.url if response is not None else None
        self.path = self.get_path() if response is not None else None
        self.response_code = response.status_code if response is not None else -1
        self.backup = self.potential_backup() if response is not None else False
        self.is_successful = util.is_successful_requests(self.response_code, self.raw_data_size, self.base_url) \
            if response is not None else False

        if self.is_successful:
            if not self.url_after_potential_redirection[-5:] == ".git/":
                self.get_ressources(response.text)
                self.form_finder(response.text)

            if finder.find_flag(web.FLAG_FORMAT, get_request_content(response), web.VERBOSE, web.CHALLENGE, False):
                web.CHALLENGE.log("Found a flag in " + self.base_url + " data !", verbose=True, state=0)

            jwt.search_jwt(get_all_responses(response))

    def get_method(self):
        req = None
        try:
            if self.method == 'GET':
                req = requests.get(self.base_url, timeout=self.timeout)
            elif self.method == 'POST':
                req = requests.post(self.base_url, timeout=self.timeout)
            elif self.method == 'PUT':
                req = requests.put(self.base_url, timeout=self.timeout)
            elif self.method == 'PATCH':
                req = requests.patch(self.base_url, timeout=self.timeout)
            elif self.method == 'HEAD':
                req = requests.head(self.base_url, timeout=self.timeout)
            elif self.method == 'DELETE':
                req = requests.delete(self.base_url, timeout=self.timeout)
            else:
                pass
        except (requests.Timeout, requests.ConnectionError) as exception:
            web.CHALLENGE.log(self.base_url + " -> " + self.method + " : " + str(exception), verbose=web.VERBOSE,
                              state=4)
        return req

    # JS, CSS, Images, Font
    def get_ressources(self, text):
        links = list()

        if "Content-Type" in self.headers:
            if "text/html" in self.headers["Content-Type"].lower():
                links += html_parser(soup(text), text)
            elif "text/css" in self.headers["Content-Type"].lower():
                links += css_parser(text)
            elif "javascript" in self.headers["Content-Type"].lower():
                links += js_parser(text)

        links = [x for x in links if (x is not None) and (len(x) != 0)]

        for i in range(len(links)):
            links[i] = self.url_sanitizer(links[i])

        links = list(set(links))
        self.ressources += links

    def url_sanitizer(self, url):
        if len(url) < 4 or url[:4] != "http":
            if len(url) != 0 and url[0] == "/":
                url = self.domain + url[1:]
            else:
                url = self.path + url
        # remove #.... in url
        if "#" in url:
            url = re.findall(r".[^#]*", url)[0]

        return url

    def get_path(self):
        if self.domain not in self.url_after_potential_redirection:
            self.url_after_potential_redirection += "/"

        index = len(self.url_after_potential_redirection) - 1
        while self.url_after_potential_redirection[index] != "/":
            index -= 1
        return self.url_after_potential_redirection[:index] + "/"

    def form_finder(self, text):
        s = soup(text)

        for f in s.find_all("form"):
            parameters = list()
            for p in f.find_all("input"):
                parameters.append((p.get("name"), p.get("type")))
            for p in f.find_all("button"):
                if p.get("name") and p.get("type"):
                    parameters.append((p.get("name"), p.get("type")))
            action_url = f.get("action") if f.get("action") is not None else ""
            form = Form(self.url_sanitizer(action_url), f.get("method"), parameters)
            self.forms.append(form)

    def potential_backup(self):
        content_type = self.headers["Content-Type"].lower() if "Content-Type" in self.headers else ""
        return ("html" in content_type or "javascript" in content_type) and \
            not self.base_url[-9:] == ".404-page" and \
            not util.is_backup(self.url_after_potential_redirection)
