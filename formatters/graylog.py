from .base import BaseFormatter

class Formatter(BaseFormatter):
    async def send(self, room: str, data: dict, headers: dict = {}, ignore_unverified=False):
        html = f"""
            <blockquote>
                <font data-mx-color="#FF6200">
                    <h3>{data.get("event_definition_title") or "Graylog Alert"}</h3>
                </font>

                <br/><strong>timestamp</strong><br/>{data["event"].get("timestamp") or "unknown"}
                <br/><strong>message</strong><br/>{data["event"].get("message") or "unknown"}
                <br/><strong>field message</strong><br/>{data["event"]["fields"].get("message") or "unknown"}
            </blockquote>
        """
        await self._send_html(room, "Graylog Alert", html, ignore_unverified=ignore_unverified)
