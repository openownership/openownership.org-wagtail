from django.core.management.base import BaseCommand, CommandError

from ...models import FocusAreaTag, PublicationType, SectorTag


AREAS_OF_FOCUS = (
    'Law',
    'Policy',
    'Systems & data',
)

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

SECTORS = (
    'Banking',
    'Environment',
    'Extractives',
)


class Command(BaseCommand):
    """
    This can be run repeatedly and it won't create multiple objects,
    unless names of objects in the database have since been changed;
    then new objects will be created with the original names.
    """
    help = 'Populates PublicationType, FocusAreaTag and SectorTag with required data.'

    def handle(self, *args, **options):
        self._populate(FocusAreaTag, AREAS_OF_FOCUS)
        self._populate(PublicationType, PUBLICATION_TYPES)
        self._populate(SectorTag, SECTORS)

    def _populate(self, tag_class, names):
        num_created = 0

        for name in names:
            obj, created = tag_class.objects.get_or_create(name=name)

            if created:
                num_created += 1

        self.stdout.write(
            f' ✓ {tag_class.__name__}: {num_created} created and '
            f'{len(names) - num_created} not touched'
        )
