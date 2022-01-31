try:
    import web_solver.web as web
    import re
except Exception as e:
    raise ImportError("jwt.py -> " + str(e))


def search_jwt(responses):
    jwts = list()
    for response in responses:
        for cookie_value in response.cookies.get_dict().values():
            if re.match(r"[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+[/a-zA-Z0-9-_]+$", cookie_value):
                if cookie_value not in jwts:
                    web.CHALLENGE.log("Find a JWT : `" + cookie_value + "`", state=0, verbose=True)
                    jwts.append(cookie_value)
    return jwts
