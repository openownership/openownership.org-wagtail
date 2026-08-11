"""
notion.attachments

Brings the files hanging off an impact tracker row into Wagtail. Anything Notion
hosts is fetched once and stored as a Wagtail image or document in its own
collection; external links are recorded as links and never fetched, since they
are other people's material and we only need to point at them.

Notion re-signs the urls of files it hosts on every fetch, so a url can never
say whether we already hold a file. `NotionFile.fingerprint` strips the
signature and is what makes a re-run cheap.
"""

# stdlib
import re
from io import BytesIO
from pathlib import PurePosixPath

# 3rd party
import requests
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from loguru import logger
from wagtail.models import Collection

# Module
from modules.notion.models import ImpactAttachment
from modules.notion.schemas.rows import NotionFile

COLLECTION_NAME = "BOT impact tracker"
DOWNLOAD_TIMEOUT = 30
MAX_BYTES = 25 * 1024 * 1024

# Wagtail truncates longer titles anyway, and the field stops at 255.
MAX_TITLE = 255
MAX_ERROR = 500

# Wagtail stores documents under `documents/` and images under
# `original_images/` in file fields that stop at 100 characters, and Django adds
# a random suffix of its own when a name collides. 60 leaves room for all of it.
MAX_FILENAME = 60
MAX_EXTENSION = 10

UNSAFE_CHARACTERS = re.compile(r"[^A-Za-z0-9_-]+")


####################################################################################################
# Entry point
####################################################################################################


def sync_attachments(entry, items: list[NotionFile]) -> None:
    """Make an entry's attachments match what Notion now holds.

    Items are upserted in the order Notion returns them, files it hosts are
    fetched the first time they are seen, and anything no longer listed is
    dropped. A download that fails is recorded on the attachment and retried on
    the next run rather than failing the entry.

    Args:
        entry: The `ImpactEntry` the attachments belong to.
        items: The row's files, in Notion's order.
    """
    seen = []
    for index, item in enumerate(items):
        attachment = _upsert(entry, item, index)
        seen.append(attachment.fingerprint)

    entry.attachments.exclude(fingerprint__in=seen).delete()


####################################################################################################
# Wagtail collection
####################################################################################################


def get_collection(name: str = COLLECTION_NAME) -> Collection:
    """Return the collection fetched files go into, creating it on first use."""
    root = Collection.get_first_root_node()
    existing = root.get_children().filter(name=name).first()
    if existing is not None:
        return existing
    return root.add_child(name=name)


####################################################################################################
# Per-attachment work
####################################################################################################


def _upsert(entry, item: NotionFile, index: int) -> ImpactAttachment:
    """Record one attachment, fetching it if we do not already hold it."""
    attachment, _ = ImpactAttachment.objects.update_or_create(
        entry=entry,
        fingerprint=item.fingerprint,
        defaults={
            "sort_order": index,
            "kind": item.kind,
            "label": item.label,
            # A signed url would be dead within the hour, so only real links
            # are worth keeping.
            "url": item.url if item.kind == ImpactAttachment.KIND_LINK else "",
        },
    )

    if attachment.kind == ImpactAttachment.KIND_LINK:
        return attachment
    if attachment.document_id or attachment.image_id:
        return attachment

    _fetch(attachment, item)
    return attachment


def _fetch(attachment: ImpactAttachment, item: NotionFile) -> None:
    """Download an item and attach it, recording any failure on the row."""
    try:
        content = _download(item.url)
    except Exception as err:  # noqa: BLE001
        logger.warning(f"impact attachment {item.fingerprint} failed: {err}")
        attachment.fetch_error = str(err)[:MAX_ERROR]
        attachment.save(update_fields=["fetch_error"])
        return

    collection = get_collection()
    title = _title_for(item)
    if attachment.kind == ImpactAttachment.KIND_IMAGE:
        attachment.image = _make_image(title, item.filename, content, collection)
    else:
        attachment.document = _make_document(title, item.filename, content, collection)

    attachment.fetch_error = ""
    attachment.save(update_fields=["image", "document", "fetch_error"])


def _download(url: str) -> bytes:
    """Fetch a url into memory, refusing anything past `MAX_BYTES`."""
    with requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True) as response:
        response.raise_for_status()
        buffer = BytesIO()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            buffer.write(chunk)
            if buffer.tell() > MAX_BYTES:
                msg = f"file is larger than the {MAX_BYTES} byte limit"
                raise ValueError(msg)
        return buffer.getvalue()


def _title_for(item: NotionFile) -> str:
    """A title fit to show a reader.

    Notion's label is a filename as often as it is a real name, and sometimes
    the url itself, so a url falls back to the filename from its path.
    """
    label = item.label.strip()
    if label and not label.startswith(("http://", "https://")):
        return label[:MAX_TITLE]
    return (item.filename or label)[:MAX_TITLE]


def _safe_filename(name: str) -> str:
    """Reduce a Notion filename to something the Wagtail file fields can hold.

    Some of the files have extraordinarily long names, sometimes with multiple dots
    """
    suffix = PurePosixPath(name).suffix
    extension = suffix.lower()[:MAX_EXTENSION]
    stem = name.removesuffix(suffix) if suffix else name
    stem = UNSAFE_CHARACTERS.sub("_", stem).strip("_")
    stem = stem[: MAX_FILENAME - len(extension)] or "attachment"
    return f"{stem}{extension}"


def _make_image(title: str, filename: str, content: bytes, collection: Collection):
    model = apps.get_model(settings.WAGTAILIMAGES_IMAGE_MODEL)
    image_file = ImageFile(BytesIO(content), name=_safe_filename(filename))
    image = model(
        title=title,
        collection=collection,
        file=image_file,
        width=image_file.width,
        height=image_file.height,
    )
    image.save()
    return image


def _make_document(title: str, filename: str, content: bytes, collection: Collection):
    model = apps.get_model(settings.WAGTAILDOCS_DOCUMENT_MODEL)
    document = model(title=title, collection=collection)
    document.file.save(_safe_filename(filename), ContentFile(content), save=True)
    return document
