import json
from django.http.response import JsonResponse
from django.shortcuts import render
from ldap3 import Server, Connection


def index(request):
    context = dict()
    return render(request, template_name="index.html", context=context)


def ldapSearchUser(request):
    """
    https://ldap3.readthedocs.io/en/latest/tutorial_searches.html
    
    """
    context = dict()
    context["success"] = False
    try:
        username = request.POST["username"]
        server = Server("SERVER")
        conn = Connection(server, "USERDN", "USERPASSWORD", auto_bind=True)
        conn.bind()

        search_strings = f"(&(objectclass=person)(uid={username}))"
        status = conn.search("CONTAINERNAME", search_strings,
                             attributes=["cn", "sn", "uid"])
        if status:
            context["success"] = True
            entries = conn.response_to_json()
            entries = json.loads(entries)
            # print(entries)
            context["fullname"] = entries["entries"][0]["attributes"]["cn"][0]
            context["username"] = entries["entries"][0]["attributes"]["uid"][0]
        else:
            context["message"] = "Kullancı adı bulunamadı!"
    except Exception as ex:
        context["message"] = "LDAP bağlantı hatası oluştu!"

    return JsonResponse(context)
