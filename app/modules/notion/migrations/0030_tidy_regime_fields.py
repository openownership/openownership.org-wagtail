from django.db import migrations, models

####################################################################################################
# Convert stringly-typed DisclosureRegime fields to proper types.
#
# threshold: CharField holding a number-as-string (or '', 'None') -> Decimal.
# The five data-feature fields: CharField holding 'Yes'/'No'/'' -> tri-state Boolean.
#
# The data conversion runs in the same step as the column-type change via a
# Postgres USING cast, so existing values are preserved rather than dropped.
####################################################################################################

TABLE = "notion_disclosureregime"

BOOL_COLUMNS = [
    "structured_data",
    "api_available",
    "bulk_data_available",
    "data_in_bods",
    "on_oo_register",
]


def _bool_forwards(column):
    return (
        f"ALTER TABLE {TABLE} ALTER COLUMN {column} DROP DEFAULT, "
        f"ALTER COLUMN {column} DROP NOT NULL, "
        f"ALTER COLUMN {column} TYPE boolean USING ("
        f"CASE lower({column}) WHEN 'yes' THEN true WHEN 'no' THEN false ELSE NULL END);"
    )


def _bool_backwards(column):
    return (
        f"ALTER TABLE {TABLE} ALTER COLUMN {column} TYPE varchar(255) USING ("
        f"CASE {column} WHEN true THEN 'Yes' WHEN false THEN 'No' ELSE '' END), "
        f"ALTER COLUMN {column} SET DEFAULT '', "
        f"ALTER COLUMN {column} SET NOT NULL;"
    )


THRESHOLD_FORWARDS = (
    f"ALTER TABLE {TABLE} ALTER COLUMN threshold DROP DEFAULT, "
    f"ALTER COLUMN threshold DROP NOT NULL, "
    f"ALTER COLUMN threshold TYPE numeric(5, 2) USING ("
    f"CASE WHEN threshold ~ '^[0-9]+(\\.[0-9]+)?$' THEN threshold::numeric ELSE NULL END);"
)

THRESHOLD_BACKWARDS = (
    f"ALTER TABLE {TABLE} ALTER COLUMN threshold TYPE varchar(255) USING ("
    f"COALESCE(threshold::text, '')), "
    f"ALTER COLUMN threshold SET DEFAULT '', "
    f"ALTER COLUMN threshold SET NOT NULL;"
)


class Migration(migrations.Migration):

    dependencies = [
        ("notion", "0029_disclosureregime_agency_type"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="disclosureregime",
                    name="threshold",
                    field=models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        verbose_name="Threshold",
                    ),
                ),
                migrations.AlterField(
                    model_name="disclosureregime",
                    name="structured_data",
                    field=models.BooleanField(blank=True, null=True, verbose_name="Structured data"),
                ),
                migrations.AlterField(
                    model_name="disclosureregime",
                    name="api_available",
                    field=models.BooleanField(blank=True, null=True, verbose_name="API available"),
                ),
                migrations.AlterField(
                    model_name="disclosureregime",
                    name="bulk_data_available",
                    field=models.BooleanField(
                        blank=True, null=True, verbose_name="Bulk data available"
                    ),
                ),
                migrations.AlterField(
                    model_name="disclosureregime",
                    name="data_in_bods",
                    field=models.BooleanField(
                        blank=True, null=True, verbose_name="Data published in BODS"
                    ),
                ),
                migrations.AlterField(
                    model_name="disclosureregime",
                    name="on_oo_register",
                    field=models.BooleanField(blank=True, null=True, verbose_name="On OO Register"),
                ),
            ],
            database_operations=[
                migrations.RunSQL(sql=THRESHOLD_FORWARDS, reverse_sql=THRESHOLD_BACKWARDS),
                *[
                    migrations.RunSQL(sql=_bool_forwards(c), reverse_sql=_bool_backwards(c))
                    for c in BOOL_COLUMNS
                ],
            ],
        ),
    ]
