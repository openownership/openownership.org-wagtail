import subprocess
from consoler import console
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    """REQUIRES PYTHON > 3.7
    """

    help = "Build the front end assets"

    def handle(self, **options):
        try:
            console.info('Building assets')
            result = subprocess.run(
                [
                    "npm",
                    "run",
                    "dev",
                    '--prefix',
                    "/usr/srv/app/assets"
                ],
                check=True, text=True
            )
        except subprocess.CalledProcessError as e:
            console.error('Asset build failed')
            print(e)
        except KeyboardInterrupt:
            print('Exited')
        else:
            console.success("Assets built")
