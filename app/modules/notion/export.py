from modules.notion.models import CountryTag
import csv


def generate_countries_csv():

    with open('countries.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'notion_id', 'name', "iso2", "committed", "involved", "involvement", "central",
            "public", "all_sectors", "commitment_level", "commitments_html", "capital_lat",
            "capital_lon", "any_online_register", "any_data_in_oo_register", "last_updated"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in CountryTag.objects.exclude(deleted=True, archived=True).all():
            row = {
                'notion_id': item.notion_id,
                'name': item.name,
                "iso2": item.iso2,
                "committed": item.committed,
                "involved": item.involved,
                "involvement": item.involvement,
                'central': item.combined_commitments['central'],
                'public': item.combined_commitments['public'],
                'all_sectors': item.combined_commitments['all_sectors'],
                'commitment_level': item.combined_commitments['level'],
                'commitments_html': item.combined_commitments['html'],
                "capital_lat": item.lat,
                "capital_lon": item.lon,
                "any_online_register": any(
                    (regime.public_access_register_url is not None) for regime in item.regimes),
                "any_data_in_oo_register": any(
                    (regime.on_oo_register is True) for regime in item.regimes),
                "last_updated": item.last_updated
            }
            writer.writerow(row)
