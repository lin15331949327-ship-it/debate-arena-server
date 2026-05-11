import requests
r = requests.get("https://aip.baidubce.com/oauth/2.0/token",
    params={"grant_type":"client_credentials",
            "client_id":"cU1FVPe08DJzqWw2K4degUo2",
            "client_secret":"lRi6wCvgppdnIdA71ZsRNK3EUTCNlEmZ"}, timeout=10)
print(f"Status: {r.status_code}")
d = r.json()
token = d.get("access_token", "")
print(f"Token: {token[:30]}..." if token else f"Error: {d}")
