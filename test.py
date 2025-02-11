import http.client

conn = http.client.HTTPSConnection("api.talkdeskstg.com")

payload = "{\n  \"name\": \"zero_shot_classification\",\n  \"version\": \"1\",\n  \"parameters\": {\n    \"text_to_be_replaced\": \"1+1\"\n  }\n}"

headers = {
    'X-Request-Product': "",
    'X-Request-Interaction-ID': "",
    'Content-Type': "application/json",
    'Accept': "application/json",
    'Authorization': "Bearer 123"
}

conn.request("POST", "/ai-platform/template-based-generator", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))