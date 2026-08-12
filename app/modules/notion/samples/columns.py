"""
notion.samples.columns

The column names and ids of each Notion database, as they stood when this was
captured. The sync matches columns by id, so this is what the schema tests check
their declared ids against.

Refresh it with `manpy notion_columns` when a tracker changes shape.
"""

SCHEMAS = {
    'countries': {
        'title': 'Country',  # title
        'qBTx': 'Disclosure regimes',  # relation
        'UL2g': 'GDrive Folder',  # url
        '%3Eu%3DR': "HubSpot 'Deal'",  # url
        'H%24!6': 'ISO2',  # rich_text
        'owyd': 'Last changed (commitments)',  # rollup
        'XemL': 'Last changed (disclosure)',  # rollup
        '.mEX': 'Last edited',  # last_edited_time
        '%26%40gf': 'Last reviewed',  # date
        'B-sl': 'Lead',  # people
        '%2FEH.': 'Memberships',  # multi_select
        'k%5DAy': 'ODA 2024 status',  # select
        '%5DkJL': 'OGP Membership & NAP cycle',  # select
        '%25%24OQ': 'OO Support',  # select
        'hN%40_': 'OO Support (new)',  # select
        'verification_owner': 'Owner',  # people
        'N~V%60': 'Project team',  # people
        'NtuA': 'Region',  # select
        'Bw%7Cl': 'Related Commitments',  # relation
        '.M0z': 'Related to Implementation tracker (database) (Country)',  # relation
        'verification': 'Verification',  # verification
        'ej%5EU': 'Who can access',  # rollup
        'sccI': 'Year launched',  # rollup
    },
    'commitments': {
        'j%22%5DW': 'All sectors',  # checkbox
        'glm0': 'Attachment',  # files
        'o)_-': 'Central register',  # checkbox
        ')UWR': 'Commitment type',  # rich_text
        "X'sx": 'Country',  # relation
        'title': 'Country & Commitment Type',  # title
        '%3Ao%7C%23': 'Date',  # date
        '_gXH': 'Last changed (automatic)',  # last_edited_time
        'W%3FNu': 'Last edited',  # last_edited_time
        '-ifl': 'Link',  # url
        '%3C%7C%3Cz': 'Public register',  # checkbox
        'ZC(N': 'Summary Text',  # rich_text
        '4td%2B': 'Tags',  # multi_select
        'A%3Eu%60': 'Trips',  # rollup
    },
    'regimes': {
        '%3CB%3As': 'Access features',  # multi_select
        'J~fN': 'Access regime details',  # rich_text
        'GzVi': 'Agency type',  # select
        'PTKs': 'Country',  # relation
        '%3ARJ%3A': 'Coverage',  # multi_select
        "ApR'": 'Coverage details',  # rich_text
        'PpKg': 'Definition',  # rich_text
        'udCF': 'Details collected',  # rich_text
        '%5E%3C%5CH': 'Forms',  # files
        'ayiY': 'Imp. stage details',  # rich_text
        '86%605': 'Implementation stage',  # multi_select
        '%23--Y': 'Last edited',  # last_edited_time
        'm%3D%7BD': 'Last updated by',  # last_edited_by
        'x%5EQC': 'Launch date',  # select
        'iFf%3D': 'Licence and data use policy details',  # rich_text
        'uQB~': 'Policy aims details',  # rich_text
        'DRH%3D': 'Privacy and data protection details',  # rich_text
        'Pj%3DK': 'Protection regime',  # select
        'Eh~s': 'Region',  # formula
        'Qj%60N': 'Region lookup',  # rollup
        'X%26sR': 'Register URL',  # url
        '%5BBni': 'Register cost and business model',  # rich_text
        'title': 'Register name',  # title
        'Nkzy': 'Responsible agency',  # rich_text
        'Zm~c': 'Sanctions and enforcement details',  # rich_text
        'Z%3Dqf': 'Scope',  # multi_select
        'vfgV': 'Stated policy aims',  # multi_select
        'BEMg': 'Structured data details',  # relation
        '%24I.J': 'Threshold (%)',  # number
        'BHUK': 'Trips',  # rollup
        '%5EqJG': 'Up-to-date and historical data details',  # rich_text
        'pxZ%5E': 'User guidance',  # files
        'w%7DKB': 'Vendor/supplier',  # rich_text
        'iTV%5B': 'Verification details',  # rich_text
        'jxf!': 'Who can access',  # multi_select
    },
    'regimes_sub': {
        'BSPh': 'API URL',  # url
        'Rs%3D%7C': 'API available',  # select
        'aTIw': 'API documentation',  # url
        'Hvs%7C': 'Bulk data URL',  # url
        'mkyf': 'Bulk data available',  # select
        '%3D%60oM': 'Country',  # rollup
        'JK%3AL': 'Data analysed/mapped',  # select
        'tqwE': 'Data analysis/mapping',  # url
        'y%3D%7Bs': 'Data on OO Register',  # select
        'G%5D%3B%7D': 'Data published in BODS',  # select
        '_qpq': 'Disclosure regime',  # relation
        '%3D~mR': 'Exact ownership values',  # select
        'BgtO': 'Identifiers information',  # rich_text
        'usVN': 'Identifiers used',  # select
        'jgmn': 'Licence URL',  # url
        'p%7B%5Co': 'Notes and remarks',  # rich_text
        'Zf%3DI': 'Open licence',  # select
        'ybCM': 'Structured data',  # select
        '%3C%3E%3BY': 'Sufficient information for full ownership chains',  # select
        'title': 'Title',  # title
        '%3E%5BFO': 'User group',  # multi_select
    },
    'bot': {
        '%3Di%5BT': 'Added',  # created_time
        'tZGA': 'Added by',  # created_by
        's_dh': 'Archive',  # checkbox
        'otX%3B': 'Attach source/supporting documentation if possible',  # files
        'CAQ%3A': 'Data user',  # multi_select
        'OZh_': 'Disclosure regime(s)',  # relation
        'wgwg': 'International',  # checkbox
        'uMFg': 'Jurisdiction(s) (P)',  # relation
        'wMN~': 'Last updated',  # last_edited_time
        '%3EpYc': 'Last updated by',  # last_edited_by
        'dJ%3EA': 'Lessons',  # rich_text
        'LORe': 'OO outputs used in',  # rich_text
        'L%5EZN': "OO's influence",  # checkbox
        'title': 'One sentence description (P)',  # title
        '%5Di%60%5E': 'Policy area (P)',  # multi_select
        'R%5D%3FH': 'Presentations/slide decks used in',  # rich_text
        'J%60Y%3F': 'Publish?',  # checkbox
        'q%60L%7D': 'Region (P)',  # rollup
        '%5EE%3B%3C': 'Short summary (P)',  # rich_text
        'ka%3CB': 'Source URL (P)',  # url
        'QTHZ': 'Tangible impact',  # checkbox
        '%7BKyh': 'Trips',  # rollup
        'R%5Dk~': 'Type',  # multi_select
        'RsOD': 'Type of resource (P)',  # multi_select
        'OfYG': 'Usability theme(s)',  # multi_select
        'x%7B%5B%3C': 'Year (P)',  # number
        'J%3DgA': '[Archive]',  # multi_select
        'j%7Cit': '[TEMP] Old?',  # checkbox
    },
}
