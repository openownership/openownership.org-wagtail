from django.core.management.base import BaseCommand, CommandError
from ...models.categories import PublicationType


PUBLICATION_TYPES = (
    'Blog post',
    'Briefing',
    'Case study',
    'Consultation',
    'Country profile',
    'Guidance',
    'Job',
    'News article',
    'Press link',
    'Report',
    'Tool',
)

class Command(BaseCommand):
    """
    This can be run repeatedly and it won't create multiple objects,
    unless names of objects in the database have since been changed;
    then new objects will be created with the original names.
    """
    help = 'Populates PublicationType with required data.'

    # def add_arguments(self, parser):
    #     parser.add_argument('my_arg', nargs='+', type=int)

    def handle(self, *args, **options):
        self._create_publication_types()

    def _create_publication_types(self):

        num_created = 0

        for name in PUBLICATION_TYPES:
            obj, created = PublicationType.objects.get_or_create(name=name)

            if created:
                num_created += 1

        self.stdout.write(
            f' ✓ PublicationType: {num_created} created and '
            f'{len(PUBLICATION_TYPES) - num_created} updated'
        )
