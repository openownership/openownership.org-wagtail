from django.core.management.base import BaseCommand, CommandError

from ...models import SectionTag, PrincipleTag


SECTIONS = (
    'About',
    'Impact',
    'Implement',
    'Research',
)

PRINCIPLES = (
    "Robust definition",
    "Comprehensive coverage",
    "Sufficient detail",
    "A central register",
    "Public access",
    "Structured data",
    "Verification",
    "Up to date and auditable",
    "Sanctions and enforcement",
)


class Command(BaseCommand):
    """
    This can be run repeatedly and it won't create multiple objects,
    unless names of objects in the database have since been changed;
    then new objects will be created with the original names.
    """
    help = 'Populates SectionTag, PrincipleTag with required data.'

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])

        self._populate(SectionTag, SECTIONS, verbosity)
        self._populate(PrincipleTag, PRINCIPLES, verbosity)

    def _populate(self, tag_class, names, verbosity):
        num_created = 0

        for name in names:
            obj, created = tag_class.objects.get_or_create(name=name)

            if created:
                num_created += 1

        if verbosity > 0:
            self.stdout.write(
                f' ✓ {tag_class.__name__}: {num_created} created and '
                f'{len(names) - num_created} not touched'
            )
