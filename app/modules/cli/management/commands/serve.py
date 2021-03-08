import subprocess
from consoler import console
from django.core.management import call_command
from django.core.management.base import BaseCommand
import threading


class Command(BaseCommand):

    """REQUIRES PYTHON > 3.7

    call_command("runserver", "0.0.0.0:5000")
    """

    help = "Build the front end assets"

    def __init__(self):
        self.assets = AssetsThread()

    def handle(self, **options):
        try:
            self.assets.start()
            call_command("runserver", "0.0.0.0:5000")
        except KeyboardInterrupt:
            self.assets.interrupt_main()
            print("Exited process")


class AssetsThread(threading.Thread):

    def __init__(self):
        self.thread_running = False
        super().__init__()

    def check(self):
        result = subprocess.run('ps', check=True, text=True, capture_output=True)
        if 'node_modules' in result.stdout:
            return False
        return True

    def run(self):
        if not self.check():
            return False

        command = "npm run dev --prefix /usr/srv/app/assets".split()
        if not self.thread_running:
            try:
                console.info("Building assets")
                self.thread_running = True
                subprocess.run(
                    command,
                    check=True,
                    text=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                print("Asset watching aborted")
            except KeyboardInterrupt:
                self.interrupt_main()
                print("Exited subprocess")
