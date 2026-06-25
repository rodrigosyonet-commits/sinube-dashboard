import requests
import os

BASE_URL = "https://getpost.si-nube.appspot.com/getpost"

def execute_query(query):
    cursor = None
    results = []

    while True:
        q = query
        if cursor:
            q += f" CURSOR {cursor}"

        params = {
            "tipo": 3,
            "emp": os.getenv("SINUBE_EMP"),
            "suc": os.getenv("SINUBE_SUC"),
            "usu": os.getenv("SINUBE_USU"),
            "pas": os.getenv("SINUBE_PAS"),
            "cns": q
        }

        res = requests.post(BASE_URL, params=params)
        text = res.text

        from parser import parse_response
        rows, cursor = parse_response(text)

        results.extend(rows)

        if cursor == "&NullSiNube;":
            break

    return results
