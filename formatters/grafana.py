from __future__ import annotations
from .base import BaseFormatter

class Formatter(BaseFormatter):
    async def send(self, room: str, data: dict, headers: dict = {}, ignore_unverified=False):
        print(data)
        for i in data["alerts"]:
            links = ""
            if i["dashboardURL"] != "":
                links += f"<a href=\"{i['dashboardURL']}\">Dashboard</a>&nbsp;"
            if i["panelURL"] != "":
                links += f"<a href=\"{i['panelURL']}\">Panel</a>&nbsp;"
            if i["silenceURL"] != "":
                links += f"<a href=\"{i['silenceURL']}\">Silence</a>&nbsp;"
            if links != "":
                links = "<br/><strong>Links</strong><br/>"+links

            annotations = ""
            if len(i["annotations"]) > 0:
                annotations = "<br/><strong>Annotations</strong><br/><ul>"
                for k,v in i["annotations"].items():
                    annotations += f"<li>{k}: <i>{v}</i></li>"
                annotations += "</ul>"

            value = "unknown"
            pos = i["valueString"].find('value=')+6
            if pos >= 6:
                if i["valueString"][pos] == "'":
                    value = i["valueString"][pos+1:i["valueString"].find("'", pos+1)]
                else:
                    value = i["valueString"][pos:i["valueString"].find(" ", pos)]

            html = f"""
                <blockquote>
                    <font data-mx-color="#{'ff0000' if i["status"] == "firing" else '00ff00'}">
                        <h3>[{i["status"]}] {i["labels"]["alertname"]}</h3>
                    </font>
                    <br/><strong>Triggered At</strong><br/>{i["startsAt"]}
                    <br/><strong>Value</strong><br/>{value}
                    {links}
                    {annotations}
                </blockquote>
            """
            await self._send_html(room, "Grafana Alert", html, ignore_unverified=ignore_unverified)
