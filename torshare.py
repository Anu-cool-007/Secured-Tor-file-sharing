import os
import shutil
import multiprocessing

from stem.control import Controller
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html", filename=app.config.get("FILE_NAME"), filesize=app.config.get("FILE_SIZE"))


@app.route('/download')
def download():
    return send_from_directory(app.config.get("FILE_DIR"), app.config.get("FILE_NAME"), as_attachment=True)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


class TorShare:
    def __init__(self):
        self.controller = None  # type: Controller
        self.control_ports = [9051, 9151]
        self.hostname = None
        self.hidden_service_dir = None
        self.app_process = None

    def connect(self):
        for controlport in self.control_ports:
            try:
                self.controller = Controller.from_port(port=controlport)
            except Exception as e:
                print(e)

    def authenticate(self):
        self.controller.authenticate()

    def is_connected(self):
        return self.controller is not None

    def create_service(self, filepath):
        self.hidden_service_dir = os.path.join(self.controller.get_conf('DataDirectory', '/tmp'), 'torshare')
        result = self.controller.create_hidden_service(self.hidden_service_dir, 80, target_port=5000)
        self.hostname = result.hostname
        self._set_file_config(filepath)
        self.app_process = multiprocessing.Process(target=app.run, name="app")
        self.app_process.start()

    def stop_service(self):
        self.controller.remove_hidden_service(self.hidden_service_dir)
        shutil.rmtree(self.hidden_service_dir)
        self.controller.close()

    def _set_file_config(self, filepath):
        app.config["FILE_DIR"] = os.path.dirname(filepath)
        app.config["FILE_NAME"] = os.path.basename(filepath)
        app.config["FILE_SIZE"] = os.path.getsize(filepath)


if __name__ == '__main__':
    app.run()
