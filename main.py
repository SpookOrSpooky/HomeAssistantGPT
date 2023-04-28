import json
import requests

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

CONFIG = {
    "home_assistant_url": "https://basicallyjarvis.duckdns.org:8123",
    "access_token": "uwGdfMFi1FdCEQvRr7nfdo_hCHEGPftyBVWc0JqDFVA",
}

HEADERS = {
    "Authorization": f"Bearer {CONFIG['access_token']}",
    "content-type": "application/json",
}

def get_home_assistant_url(endpoint):
    return f"{CONFIG['home_assistant_url']}{endpoint}"

@app.post("/lights/<string:entity_id>/<string:status>")
async def change_light_status(entity_id, status):
    if status not in ["on", "off"]:
        return quart.Response(response="Invalid status. Accepted values: on, off", status=400)

    url = get_home_assistant_url(f"/api/services/light/turn_{status}")
    data = {"entity_id": entity_id}
    response = requests.post(url, headers=HEADERS, json=data)

    if response.status_code == 200:
        return quart.Response(response="OK", status=200)
    else:
        return quart.Response(response="Error changing light status", status=500)

@app.get("/lights")
async def discover_lights():
    url = get_home_assistant_url("/api/states")
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        states = response.json()
        lights = [state for state in states if state["entity_id"].startswith("light.")]
        return quart.Response(response=json.dumps(lights), status=200)
    else:
        return quart.Response(response="Error discovering lights", status=500)

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/plugin_manifest.yaml")
async def plugin_manifest_yaml():
    host = request.headers['Host']
    with open("plugin_manifest.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
