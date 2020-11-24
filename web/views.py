import json
from django.http.response import JsonResponse
from django.shortcuts import render
from ldap3 import MODIFY_REPLACE, Server, Connection

import logging


logger = logging.getLogger(__name__)


SERVER = ""
USERDN = ""
USERPASSWORD = ""
CONTAINERNAME = ""


def index(request):
    context = dict()
    return render(request, template_name="index.html", context=context)


def ldapSearchWithUsername(request):
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


def ldapSearchWithFullname(request):
    context = dict()
    context["success"] = False
    try:
        fullname: str = request.POST["fullname"]
        server = Server(SERVER)
        conn = Connection(server, USERDN,
                          USERPASSWORD, auto_bind=True)
        conn.bind()
        logger.info(f"Sorgulanan kullanıcı adı:{fullname}")

        # fullname = "ishakdolek"
        # Türkçe karakterlere dikkat etmek lazım i > I olarak dönüşmesi lazım
        fullname = fullname.upper()

        search_strings = f"(&(objectclass=person)(cn={fullname}))"
        status = conn.search(CONTAINERNAME, search_strings, attributes=[
                             "cn", "sn", "uid"])
        if status:
            context["success"] = True
            entries = conn.response_to_json()
            entries = json.loads(entries)
            # print(entries)
            tmpList = []
            for i in range(len(entries["entries"])):
                # print(entries)
                entriesDict = {}
                entriesDict["fullname"] = entries["entries"][i]["attributes"]["cn"][0]
                entriesDict["username"] = entries["entries"][i]["attributes"]["uid"][0]
                tmpList.append(entriesDict)
            context["persons"] = tmpList
        else:
            context["message"] = "Kullancı adı bulunamadı!"

        conn.unbind()
    except Exception as ex:
        logger.error(ex)
        context["message"] = "LDAP bağlantı hatası oluştu!"

    return JsonResponse(context)


def ldapUpdate(request):
    """
    For update use this tutorial: #https://ldap3.readthedocs.io/en/latest/tutorial_operations.html#update-an-entry 

    """

    context = dict()
    context["success"] = False
    try:

        pk = request.POST["pk"]
        if pk is None:
            return JsonResponse(context)
        vlan_id = request.POST["vlan_id"]
        server = Server(SERVER)
        conn = Connection(server, USERDN,
                          USERPASSWORD, auto_bind=True)
        conn.bind()
        logger.info(f"Sorgulanan Vlan adı:{vlan_id}")
        status = conn.modify(f'uid={"username"},ou=personel,{CONTAINERNAME}', {
                             'radiusTunnelPrivateGroupId': [(MODIFY_REPLACE, [vlan_id])]})
        if status:
            context["success"] = True
        else:
            context["message"] = "Kullancı adı bulunamadı!"

        conn.unbind()
    except Exception as ex:
        logger.error(ex)
        context["message"] = "LDAP bağlantı hatası oluştu!"

    return JsonResponse(context)
