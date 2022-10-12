from .base import BaseFormatter
from markdown import markdown

class Formatter(BaseFormatter):
    async def send(self, room: str, data: dict, headers: dict = {}, ignore_unverified=False):
        if "content" in data:
            await self._send_html(room, data["content"], markdown(data["content"]), ignore_unverified=ignore_unverified)

        if "embeds" in data:
            for i in data["embeds"]:
                await self.process_embed(room, i, data.get("content"), ignore_unverified)


    async def process_embed(self, room, e, content, ignore_unverified):
        if "video" in e:
            url = e["video"].get("url") or e["url"]
            await self._send_file(room, e.get("title") or url.split("/")[-1], url, ignore_unverified=ignore_unverified, width=e["video"].get("width"), height=e["video"].get("height"))

        elif "author" in e or "description" in e or "footer" in e or "title" in e or "provider" in e or "fields" in e:
            img_data = None
            if "thumbnail" in e:
                img_data = await self._send_file(room, e.get("title") or e["thumbnail"]["url"], e["thumbnail"]["url"], message=False, width=e["thumbnail"].get("width"), height=e["thumbnail"].get("height"))
            if "image" in e:
                img_data = await self._send_file(room, e.get("title") or e["image"]["url"], e["image"]["url"], message=False, width=e["image"].get("width"), height=e["image"].get("height"))

            image_html = ""
            if img_data:
                image_html = f"<br/><img src=\"{img_data['url']}\" width=\"{img_data['width']}\" height=\"{img_data['height']}\"/><br/>"

            fields_html = ""
            if "fields" in e and e["fields"] is not None:
                for i in e["fields"]:
                    if i.get("inline"):
                        fields_html += f"<br/>{i['name']}: {markdown(i['value'])}"
                    else:
                        fields_html += f"<br/><strong>{i['name']}</strong><br/>{markdown(i['value'])}"
                fields_html += "<br/>"

            author_html = ""
            if "author" in e:
                if "url" in e["author"]:
                    author_html = f"<h5>[<a href=\"{e['author']['url']}\">{e['author']['name']}</a>]</h5>"
                else:
                    author_html = f"<h5>[{e['author']['name']}]</h5>"

                if "avatar_url" in e:
                    author_html = f"<h5><img src=\"{e['avatar_url']}\" width=\"20\" height=\"20\"/>&nbsp;{author_html}"
                    
            provider_html = ""
            if "provider" in e:
                if "url" in e["provider"]:
                    provider_html = f"<h5>[<a href=\"{e['provider']['url']}\">{e['provider']['name']}</a>]</h5>"
                else:
                    provider_html = f"[<h5>{e['provider']['name']}]</h5>"

            footer_html = ""
            if "footer" in e:
                footer_html = f"<p><i><font data-mx-color=\"#707070\">{e['footer']['text']}</font></i></p>"

            title_html = ""
            if content is not None:
                title_html = f"<h3>{content}</h3>"
                if "title" in e:
                    title_html += f"<h4>{e['title']}</h4>"
            elif "title" in e:
                title_html = f"<h3>{e['title']}</h3>"

            url_html = ""
            if "url" in e:
                if "title" in e:
                    title_html = f"<a href=\"{e['url']}\">{title_html}</a>"
                else:
                    url_html = f"<br/><a href=\"{e['url']}\">{e['url']}</a>"

            description_html = ""
            if "description" in e:
                description_html = f"<p>{markdown(e['description'])}</p>"

            color_html_start = ""
            color_html_end = ""
            if "color" in e:
                code = '{0:06X}'.format(int(e['color']))
                color_html_start = f"<font data-mx-color=\"#{code}\">"
                color_html_end = "</font>"

            html = f"""
                <blockquote>
                    {color_html_start}
                        {author_html}
                        {title_html}
                    {color_html_end}
                    {provider_html}
                    {description_html}
                    {color_html_start}
                        {fields_html}
                    {color_html_end}
                    {image_html}
                    {footer_html}
                    {url_html}
                </blockquote>
            """

            await self._send_html(room, "", html, ignore_unverified=ignore_unverified)

        elif "image" in e:
            url = e["image"].get("url") or e["url"]
            await self._send_file(room, e.get("title") or url.split("/")[-1], url, ignore_unverified=ignore_unverified, width=e["image"].get("width"), height=e["image"].get("height"))

        elif "thumbnail" in e:
            url = e["thumbnail"].get("url") or e["url"]
            await self._send_file(room, e.get("title") or url.split("/")[-1], url, ignore_unverified=ignore_unverified, width=e["thumbnail"].get("width"), height=e["thumbnail"].get("height"))