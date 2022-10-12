#!/usr/local/bin/python3

import yaml
from aiohttp import web
from formatters import get_formatter
from client import get_client

with open("/data/config.yaml") as f:
    config = yaml.full_load(f)

app = web.Application()
routes = web.RouteTableDef()

connected_users = {}

@routes.post('/{url:.*}')
async def variable_handler(request):
    path = request.match_info['url']
    if path in config["bots"]:
        cfg = config["bots"][path]
        if cfg["user"] in connected_users:
            client = connected_users[cfg["user"]]
        else:
            client = await get_client(config["matrix"]["homeserver"], cfg["user"], cfg["password"], config["matrix"]["device_id"], config["matrix"]["store_path"])
            connected_users[cfg["user"]] = client

        resp = await get_formatter(cfg["formatter"])(client).send(cfg["room"], await request.json(), request.headers, ignore_unverified=cfg.get("ignore_unverified"))
        if resp:
            return web.json_response(resp)
        else:
            return web.json_response({"status": "ok"})
    else:
        return web.json_response({"status": "error", "description": "no matching webhook found"})

app.add_routes(routes)
web.run_app(app)
