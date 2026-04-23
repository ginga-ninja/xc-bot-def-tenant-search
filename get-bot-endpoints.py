import json
import requests
from datetime import datetime

# Global vars
xc_api_key= "xxxxxxxxxxxxxxxxxxx"     #your XC API key
#namespace = "j-lockhart"
#lb_test = "airline-vk8s-app-lb"
tenant = "f5-emea-ent" #your tenant
#xc_api_url = "https://" + tenant + ".console.ves.volterra.io/api/config/namespaces/" + namespace + "/http_loadbalancers/" + lb_test
auth_header = 'Authorization: APIToken ' + xc_api_key

headers = {'accept': 'application/json', 'Authorization': 'APIToken ' + xc_api_key, 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'x-volterra-apigw-tenant': tenant}

#GET ALL NAMESPACES IN A TENANT
def get_namespaces():
    get_ns_api = "https://" + tenant + ".console.ves.volterra.io/api/web/namespaces"
    x = requests.get(get_ns_api, headers=headers)
    data = json.loads(x.text)
    #print (data)
    ns = []    #list for namespaces
    c=0
    for i in data['items']:
        c=c+1
        ns.append(i['name'])

    #print (lbs)
    print("There are " + str(c) + " namespaces ")
    return ns

# FUNCTION TO GET ALL LBs IN A NAMESPACE
def get_lbs_in_namespace(ns):
    get_lbs_api = "https://"+tenant+".console.ves.volterra.io/api/config/namespaces/"+ns+"/http_loadbalancers"
    x = requests.get(get_lbs_api, headers=headers)
    data = json.loads(x.text)
    #print(data)
    c=0
    lbs = []
    for i in data['items']:
        c=c+1
        lbs.append(i['name'])

    #print (lbs)
    #print("There are " + str(c) + " load balancers in the namespace " + ns)
    return lbs

# FUNCTION TO CHECK IF BOT DEFENSE IS ENABLED ON LOAD BALANCER
def check_bot_enabled(lb,ns):
    lb_config_api = "https://" + tenant + ".console.ves.volterra.io/api/config/namespaces/" + ns + "/http_loadbalancers/" + lb
    x = requests.get(lb_config_api, headers=headers)
    data = json.loads(x.text)
    #print(data)
    spec = data['spec']
    if "disable_bot_defense" in spec:
        #print("Bot Defense not enabled for " + lb)
        return
    elif "bot_defense" in spec:
        #print ("Bot Defense protected endpoints on " + lb + " lb:")
        print("Namespace: " + ns + ", Load Balancer: " + lb)
        get_endpoint_data(data)
    else:
        return

#GETS ENDPOINT PATH AND MITIGATION STATUS FOR LBs THAT HAVE BOT DEFENSE ENABLED
def get_endpoint_data(json_data):
    endpoints = json_data['spec']['bot_defense']['policy']['protected_app_endpoints']
    #print(endpoints)
    ep_data = []
    mitigation_status = []

    for q in endpoints:
        #c = q.get('collection')
        path = str(q['path'])    #get endpoint path
        ep_data.append(path)
        m = q['mitigation']    #get migitation json element
        #mit_status.append(mit)
        #print(ep_data)
        #print(mit)
        key = list(m.keys())
        if len(key) == 1:
            #print(key[0])
            mitigation_status.append(key[0])

    n=0
    for i in ep_data:
        print ("Endpoint " + str(n+1) + " = " + i + ", Mitigation Status: " + mitigation_status[n])
        n=n+1

    print ("Total Endpoints = " + str(n))

#main
ns = []
ns = get_namespaces()

# GET ALL LBs IN A NAMESPACE
for i in ns:
    #print(i)
    lbs = []
    lbs = get_lbs_in_namespace(i)
    if lbs:     #only check for bot def if there are lbs in the namespace
        #GET THE ENDPOINTS
        for j in lbs:
            check_bot_enabled(j,i)
    else:
        print("No LBs found in namespace: " + i)

print("Complete")