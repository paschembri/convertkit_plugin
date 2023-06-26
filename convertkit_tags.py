import sublime
import sublime_plugin
import http.client
import threading
import json


class ConvertKitManageTagsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        public_api_key = sublime.load_settings(
            "ConvertKit.sublime-settings"
        ).get("public_api_key")
        if not public_api_key:
            sublime.error_message(
                "Please set your ConvertKit API key in the settings file."
            )
            return

        def get_tags():
            conn = http.client.HTTPSConnection("api.convertkit.com")
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            conn.request(
                "GET", "/v3/tags?api_key=" + public_api_key, headers=headers
            )
            res = conn.getresponse()
            data = res.read()
            tags = json.loads(data.decode("utf-8"))["tags"]
            return tags

        def copy_tag(tag_id):
            sublime.set_clipboard(tag_id)

        def show_tags():
            tags = get_tags()
            tag_names = [
                tag['name'] + " (id: " + str(tag['id']) + ")" for tag in tags
            ]

            def on_done(index):
                if index != -1:
                    tag_id = str(tags[index]['id'])
                    copy_tag(tag_id)

            self.view.window().show_quick_panel(tag_names, on_done)

        threading.Thread(target=show_tags).start()


class ConvertKitCreateTagCommand(sublime_plugin.WindowCommand):
    def run(self):
        public_api_key = sublime.load_settings(
            "ConvertKit.sublime-settings"
        ).get("public_api_key")
        if not public_api_key:
            sublime.error_message(
                "Please set your ConvertKit API key in the settings file."
            )
            return

        def create_tag(tag_name):
            conn = http.client.HTTPSConnection("api.convertkit.com")
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = {"tag": {"name": tag_name}}
            conn.request(
                "POST",
                "/v3/tags?api_key=" + public_api_key,
                body=json.dumps(payload),
                headers=headers,
            )
            res = conn.getresponse()
            data = res.read()
            tag = json.loads(data.decode("utf-8"))["tag"]
            sublime.message_dialog(
                "Tag '{}' created successfully.".format(tag['name'])
            )

        self.window.show_input_panel(
            "Enter tag name:", "", create_tag, None, None
        )
