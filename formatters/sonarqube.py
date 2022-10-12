from .base import BaseFormatter

class Formatter(BaseFormatter):
    async def send(self, room: str, data: dict, headers: dict = {}, ignore_unverified=False):
        html = f"""
            <blockquote>
                <font data-mx-color="#{'00ff00' if data['status'] == 'SUCCESS' else 'ff0000'}">
                    <h3><a href="{data['project']['url']}">{data["project"]["name"]}</a> on {data['branch']['name']}: {data['status']}</h3>
                </font>
            </blockquote>
        """
        await self._send_html(room, "Sonarqube Status", html, ignore_unverified=ignore_unverified)
