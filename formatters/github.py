from .base import BaseFormatter

class Formatter(BaseFormatter):
    async def send(self, room: str, data: dict, headers: dict = {}, ignore_unverified=False):
        url = await self._send_file(room, data["sender"]["login"], data["sender"]["avatar_url"], message=False, width=20, height=20)

        title, desc, color = self.get_data(headers.get("X-GitHub-Event"), data)
        if title is None:
            return

        html = f"""
            <blockquote>
                <font data-mx-color="#{color}">
                    <h5><img src="{url['url']}" width="20" height="20"/>&nbsp;<a href="{data["sender"]["html_url"]}">{data["sender"]["login"]}</a></h5>

                    <h3>{title}</h3><br/>

                    <p>
                        {desc}
                    </p>
                </font>
            </blockquote>
        """
        await self._send_html(room, "Github Info", html, ignore_unverified=ignore_unverified)

    def get_data(self, evt, data):
        if evt == "push":
            # push
            desc = "<ul>"
            for i in data['commits']:
                desc += f"<li><a href=\"{i['url']}\">{i['id'][0:12]}</a> - {i['message']}</li>"
            desc += "</ul>"
            return [
                f"<a href=\"{data['repository']['html_url']}/compare/{data['before'][0:12]}...{data['after'][0:12]}\">[{data['repository']['name']}:{data['ref'].split('/')[-1]}] {len(data['commits'])} new commits</a>",
                desc,
                "7289DA"
            ]
        elif evt == "code_scanning_alert" or evt == "dependabot_alert":
            # code scanner alert
            return [f"<a href=\"{data['alert']['html_url']}\">Code Scanning Alert</a> for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>", "<p>" + data["alert"]["rule"]["full_description"] if "rule" in data["alert"] else data["alert"]["security_advisory"]["summary"] + "</p>", "FC2929"]
        elif evt == "issue_comment":
            # issue comment
            return [
                f"New comment for <a href=\"{data['comment']['html_url']}\">issue #{data['issue']['number']}</a>",
                f"<p>{data['comment']['body']}</p>",
                "E68D60"
                ]
        elif evt == "commit_comment":
            # commit comment
            return [
                f"New comment for commit <a href=\"{data['comment']['html_url']}\">{data['comment']['commit_id'][0:12]}</a>",
                f"<p>{data['comment']['body']}</p>",
                "7289DA"
            ]
        elif evt == "create":
            # create tag
            return [f"New tag created for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>: <a href=\"{data['repository']['html_url']}/tree/{data['ref']}\">{data['ref']}</a>", "", "009800"]
        elif evt == "delete":
            # delete tag
            return [f"Tag deleted for <a href=\"{data['repository']['html_url']}</a>: {data['ref']}", "", "FC2929"]
        elif evt == "deploy_key":
            if data["action"] == "created":
                # add deploy key
                return [f"Deploy key added for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>: {data['key']['title']}", "", "009800"]
            else:
                # remove deploy key
                return [f"Deploy key removed for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>: {data['key']['title']}", "", "FC2929"]
        elif evt == "deployment_status":
            # deployment status
            return [f"Deployment #<a href=\"{data['deployment']['statuses_url']}\">{data['deployment']['id']}</a> on {data['deployment']['environment']} for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>: {data['deployment_status']['state']}", f"<p>{data['deployment_status']['description']}</p>", "009800" if data['deployment_status']['state'] == 'success' else "FC2929"]
        elif evt == "deployment":
            # new deployment
            return [f"Deployment #<a href=\"{data['deployment']['statuses_url']}\">{data['deployment']['id']}</a> on {data['deployment']['environment']} for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>", "", "009800"]
        elif evt == "fork":
            # new fork
            return [
                f"<a href=\"{data['forkee']['html_url']}\">{data['forkee']['name']}</a> forked from <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                "",
                "7289DA"
            ]
        elif evt == "issue":
            # new issue
            return [
                f"Issue {data['action']}: <a href=\"{data['issue']['html_url']}\">{data['issue']['title']}</a> for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                f"<p>{data['issue']['body']}</p>",
                "EB6420"
            ]
        elif evt == "pull_request_review_comment":
            # pr comment
            return [
                f"New comment on PR <a href=\"{data['pull_request']['html_url']}\">{data['pull_request']['number']}</a> for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                f"<p>{data['comment']['body']}</p>",
                "7289DA"
            ]
        elif evt == "pull_request_review":
            # pr review
            return [
                f"Review {data['action']} for PR <a href=\"{data['pull_request']['html_url']}\">{data['pull_request']['number']}</a> for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                "",
                "7289DA"
            ]
        elif evt == "pull_request":
            # pr action
            return [
                f"PR {data['action']}: <a href=\"{data['pull_request']['html_url']}\">{data['pull_request']['number']}</a> for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                f"<p>{data['comment']['body']}</p>",
                "7289DA"
            ]
        elif evt == "release":
            if data['action'] in ["created", "published"]:
                # ingore these as there is already the "released" action
                return None, "", ""
            # release action
            return [
                f"Release {data['action']}: <a href=\"{data['release']['html_url']}\">{data['release']['name'] or data['release']['tag_name']}</a> for <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                f"<p>{data['release']['body']}</p>",
                "FC2929" if data["action"] == "deleted" else "009800"
            ]
        elif evt == "star":
            # release action
            return [
                f"<a href=\"{data['sender']['html_url']}\">{data['sender']['login']}</a> starred <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                "",
                "7289DA"
            ]
        elif evt == "workflow_run":
            # workflow action
            color = "009800"
            if data['workflow_run']['status'] == 'failed':
                color = "FC2929"
            if data['workflow_run']['status'] in ['queued', 'in_progress']:
                color = "FF6200"

            return [
                f"Workflow Run <a href=\"{data['workflow_run']['html_url']}\">#{data['workflow_run']['id']}</a> {data['action']} for {data['workflow']['name']} of <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>: {data['workflow_run']['status']}",
                "",
                color
            ]
        elif evt == "repository":
            # repo action
            return [
                f"Repository {data['action']}: <a href=\"{data['repository']['html_url']}\">{data['repository']['name']}</a>",
                "",
                "7289DA"
            ]
        
        return None, "", ""