from abc import ABC
import json
import os
import subprocess
from typing import Union

import aiofiles.os
import aiohttp
import magic
from nio import AsyncClient, UploadResponse
from PIL import Image


class BaseFormatter(ABC):
    def __init__(self, client: AsyncClient) -> None:
        super().__init__()
        self._client = client

    async def send(self, room: str, data: dict, headers: dict = {}, ignore_unverified=False):
        raise NotImplementedError



    async def _send_text(self, room: str, content: str, notice=False, ignore_unverified=False):
        return await self._client.room_send(
            room_id=room,
            message_type="m.room.message",
            content={"msgtype": "m.notice" if notice else "m.text", "body": content},
            ignore_unverified_devices=ignore_unverified
        )

    async def _send_html(self, room: str, text: str, html: str, notice=False, ignore_unverified=False):
        return await self._client.room_send(
            room_id=room,
            message_type="m.room.message",
            content={"msgtype": "m.notice" if notice else "m.text", "body": text, "formatted_body": html, "format": "org.matrix.custom.html"},
            ignore_unverified_devices=ignore_unverified
        )

    async def _send_file(self, room: str, name: str, filename: str, message=True, ignore_unverified=False, width=None, height=None) -> Union[bool,dict]:
        remove_file = False
        if filename.startswith("http"):
            remove_file = True
            filename = await self.__download_file(filename)
        
        mime_type = magic.from_file(filename, mime=True)
        data = await self._upload_file(name, filename, mime_type)
        if data == False:
            if remove_file:
                os.remove(filename)
            return False

        if mime_type.startswith("image/"):
            im = Image.open(filename)
            (w, h) = im.size
            if message:
                ret = await self.__send_image(room, name, data["url"], width or w, height or h, mime_type, data["size"], ignore_unverified=ignore_unverified)
            else:
                ret = {"url": data["url"], "size": data["size"], "width": width, "height": height, "mime_type": mime_type}
        elif mime_type.startswith("audio/"):
            probe = self.__ffprobe(filename, is_video=False)
            if message:
                ret = await self.__send_audio(room, name, data["url"], round(float(probe["duration"])), mime_type, data["size"], ignore_unverified=ignore_unverified)
            else:
                ret = {"url": data["url"], "size": data["size"], "duration": round(float(probe["duration"])), "mime_type": mime_type}
        elif mime_type.startswith("video/"):
            probe = self.__ffprobe(filename, is_video=True)
            if message:
                ret = await self.__send_video(room, name, data["url"], width or int(probe["width"]), height or int(probe["height"]), int(probe["duration_ts"]), mime_type, data["size"], ignore_unverified=ignore_unverified)
            else:
                ret = {"url": data["url"], "size": data["size"], "duration": int(probe["duration_ts"]), "width": int(probe["width"]), "height": int(probe["height"]), "mime_type": mime_type}
        else:
            if message:
                ret = await self.__send_generic(room, name, data["url"], mime_type, data["size"], ignore_unverified=ignore_unverified)
            else:
                ret = {"url": data["url"], "size": data["size"], "mime_type": mime_type}

        if remove_file:
            os.remove(filename)
        return ret



    async def __send_image(self, room: str, name: str, image_url: str, width: int, height: int, mime_type: str, size: int, ignore_unverified=False):
        content = {
            "body": name,
            "info": {
                "size": size,
                "mimetype": mime_type,
                "w": width,
                "h": height,
            },
            "msgtype": "m.image",
            "url": image_url,
        }
        return await self._client.room_send(room, message_type="m.room.message", content=content, ignore_unverified_devices=ignore_unverified)

    async def __send_audio(self, room: str, name: str, url: str, duration: int, mime_type: str, size: int, ignore_unverified=False):
        content = {
            "body": name,
            "info": {
                "size": size,
                "mimetype": mime_type,
                "duration": duration,
            },
            "msgtype": "m.audio",
            "url": url,
        }
        return await self._client.room_send(room, message_type="m.room.message", content=content, ignore_unverified_devices=ignore_unverified)

    async def __send_video(self, room: str, name: str, url: str, width: int, height: int, duration: int, mime_type: str, size: int, ignore_unverified=False):
        content = {
            "body": name,
            "info": {
                "size": size,
                "mimetype": mime_type,
                "duration": duration,
                "width": width,
                "height": height
            },
            "msgtype": "m.video",
            "url": url,
        }
        return await self._client.room_send(room, message_type="m.room.message", content=content, ignore_unverified_devices=ignore_unverified)
        
    async def __send_generic(self, room: str, name: str, url: str, mime_type: str, size: int, ignore_unverified=False):
        content = {
            "body": name,
            "info": {
                "size": size,
                "mimetype": mime_type,
            },
            "msgtype": "m.file",
            "url": url,
        }
        return await self._client.room_send(room, message_type="m.room.message", content=content, ignore_unverified_devices=ignore_unverified)

    async def _upload_file(self, name: str, filename: str, mime_type: str) -> Union[None, dict]:
        file_stat = await aiofiles.os.stat(filename)
        async with aiofiles.open(filename, "r+b") as f:
            resp, maybe_keys = await self._client.upload(
                f,
                content_type=mime_type,
                filename=name,
                filesize=file_stat.st_size,
            )
        if isinstance(resp, UploadResponse):
            return {"size": file_stat.st_size, "url": resp.content_uri}
        else:
            return None
            
    async def __download_file(self, url: str) -> str:
        name = url.split("/")[-1]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                assert resp.status == 200
                data = await resp.read()
        f = "./"+name
        async with aiofiles.open(f, "wb") as outfile:
            await outfile.write(data)
        return f

    async def __ffprobe(self, filename, is_video=True):
        result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams {"v" if is_video else "a"}:0 -of json "{filename}"',
            shell=True).decode()
        fields = json.loads(result)['streams'][0]
        return fields