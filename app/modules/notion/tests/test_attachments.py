# stdlib
from io import BytesIO

# 3rd party
import pytest
from django.apps import apps
from django.conf import settings
from PIL import Image as PILImage

# Module
from modules.notion import attachments
from modules.notion.models import ImpactAttachment, ImpactEntry
from modules.notion.schemas.rows import NotionFile

HOSTED = "https://prod-files-secure.s3.us-west-2.amazonaws.com/ws/id/"


####################################################################################################
# Helpers
####################################################################################################


def png_bytes(size=(4, 4)) -> bytes:
    buffer = BytesIO()
    PILImage.new("RGB", size, (255, 0, 0)).save(buffer, format="PNG")
    return buffer.getvalue()


def hosted(name, signature="sig=1"):
    return NotionFile(label=name, url=f"{HOSTED}{name}?{signature}", hosted=True)


def link(label, url):
    return NotionFile(label=label, url=url, hosted=False)


@pytest.fixture
def entry():
    return ImpactEntry.objects.create(
        notion_id="entry-1",
        description="Kenyan FIU used BO data in an investigation",
    )


@pytest.fixture
def downloads(monkeypatch):
    """Replace the network call, recording the urls asked for."""
    calls = []

    def fake_download(url):
        calls.append(url)
        if url.lower().split("?")[0].endswith(".png"):
            return png_bytes()
        return b"%PDF-1.4 pretend"

    monkeypatch.setattr(attachments, "_download", fake_download)
    return calls


####################################################################################################
# Links
####################################################################################################


def test_link_is_stored_without_being_fetched(entry, downloads):
    attachments.sync_attachments(entry, [link("Article 2", "https://media.am/story")])

    attachment = entry.attachments.get()
    assert attachment.kind == ImpactAttachment.KIND_LINK
    assert attachment.url == "https://media.am/story"
    assert attachment.label == "Article 2"
    assert attachment.document is None
    assert attachment.image is None
    assert downloads == []


def test_external_pdf_stays_a_link(entry, downloads):
    url = "https://gov.uk/media/State_of_Competition.pdf"
    attachments.sync_attachments(entry, [link(url, url)])

    assert entry.attachments.get().kind == ImpactAttachment.KIND_LINK
    assert downloads == []


####################################################################################################
# Fetching into Wagtail
####################################################################################################


def test_hosted_document_becomes_a_wagtail_document(entry, downloads):
    attachments.sync_attachments(entry, [hosted("gao-25-107403.pdf")])

    attachment = entry.attachments.get()
    assert attachment.kind == ImpactAttachment.KIND_DOCUMENT
    assert attachment.document is not None
    assert attachment.document.title == "gao-25-107403.pdf"
    assert attachment.fetch_error == ""
    assert len(downloads) == 1


@pytest.mark.usefixtures("downloads")
def test_hosted_image_becomes_a_wagtail_image(entry):
    attachments.sync_attachments(entry, [hosted("screenshot.png")])

    attachment = entry.attachments.get()
    assert attachment.kind == ImpactAttachment.KIND_IMAGE
    assert attachment.image is not None
    assert attachment.image.width == 4
    assert attachment.image.height == 4


@pytest.mark.usefixtures("downloads")
def test_fetched_files_land_in_their_own_collection(entry):
    attachments.sync_attachments(entry, [hosted("report.pdf"), hosted("shot.png")])

    collection = attachments.get_collection()
    assert collection.name == attachments.COLLECTION_NAME
    for attachment in entry.attachments.all():
        held = attachment.document or attachment.image
        assert held.collection == collection


@pytest.mark.usefixtures("downloads")
def test_url_is_not_stored_for_fetched_files(entry):
    """Notion's signed urls expire, so keeping one would only mislead."""
    attachments.sync_attachments(entry, [hosted("report.pdf")])

    assert entry.attachments.get().url == ""


@pytest.mark.usefixtures("downloads")
def test_title_falls_back_to_the_filename_when_the_label_is_a_url(entry):
    item = NotionFile(label=f"{HOSTED}report.pdf", url=f"{HOSTED}report.pdf?sig=1", hosted=True)
    attachments.sync_attachments(entry, [item])

    assert entry.attachments.get().document.title == "report.pdf"


####################################################################################################
# Re-running a sync
####################################################################################################


def test_a_resigned_url_does_not_download_the_file_again(entry, downloads):
    attachments.sync_attachments(entry, [hosted("gao.pdf", signature="sig=first")])
    first = entry.attachments.get().document_id

    attachments.sync_attachments(entry, [hosted("gao.pdf", signature="sig=second")])

    assert len(downloads) == 1
    assert entry.attachments.get().document_id == first


@pytest.mark.usefixtures("downloads")
def test_an_attachment_removed_in_notion_is_removed_here(entry):
    attachments.sync_attachments(entry, [hosted("one.pdf"), hosted("two.pdf")])
    assert entry.attachments.count() == 2

    attachments.sync_attachments(entry, [hosted("two.pdf")])

    assert [item.label for item in entry.attachments.all()] == ["two.pdf"]


@pytest.mark.usefixtures("downloads")
def test_every_attachment_removed_leaves_none(entry):
    attachments.sync_attachments(entry, [hosted("one.pdf")])
    attachments.sync_attachments(entry, [])

    assert entry.attachments.count() == 0


@pytest.mark.usefixtures("downloads")
def test_order_is_kept(entry):
    items = [hosted("one.pdf"), link("two", "https://example.com/two"), hosted("three.png")]
    attachments.sync_attachments(entry, items)

    assert [item.label for item in entry.attachments.all()] == ["one.pdf", "two", "three.png"]


@pytest.mark.usefixtures("downloads")
def test_reordering_in_notion_is_followed(entry):
    attachments.sync_attachments(entry, [hosted("one.pdf"), hosted("two.pdf")])
    attachments.sync_attachments(entry, [hosted("two.pdf"), hosted("one.pdf")])

    assert [item.label for item in entry.attachments.all()] == ["two.pdf", "one.pdf"]


####################################################################################################
# Failure
####################################################################################################


def test_a_failed_download_is_recorded_and_does_not_raise(entry, monkeypatch):
    def boom(url):  # noqa: ARG001
        msg = "404 Not Found"
        raise ValueError(msg)

    monkeypatch.setattr(attachments, "_download", boom)
    attachments.sync_attachments(entry, [hosted("gone.pdf")])

    attachment = entry.attachments.get()
    assert attachment.document is None
    assert "404 Not Found" in attachment.fetch_error


def test_a_failed_download_is_retried_on_the_next_run(entry, monkeypatch):
    def boom(url):  # noqa: ARG001
        msg = "timed out"
        raise ValueError(msg)

    monkeypatch.setattr(attachments, "_download", boom)
    attachments.sync_attachments(entry, [hosted("gao.pdf")])

    monkeypatch.setattr(attachments, "_download", lambda url: b"%PDF-1.4 pretend")  # noqa: ARG005
    attachments.sync_attachments(entry, [hosted("gao.pdf")])

    attachment = entry.attachments.get()
    assert attachment.document is not None
    assert attachment.fetch_error == ""


def test_an_oversized_file_is_not_stored(entry, monkeypatch):
    monkeypatch.setattr(attachments, "MAX_BYTES", 8)

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size):  # noqa: ARG002
            yield b"x" * 32

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(attachments.requests, "get", lambda *a, **kw: FakeResponse())  # noqa: ARG005
    attachments.sync_attachments(entry, [hosted("huge.pdf")])

    attachment = entry.attachments.get()
    assert attachment.document is None
    assert "larger than" in attachment.fetch_error


####################################################################################################
# Collection
####################################################################################################


@pytest.mark.usefixtures("entry", "downloads")
def test_the_collection_is_only_created_once():
    first = attachments.get_collection()
    second = attachments.get_collection()

    assert first.pk == second.pk


@pytest.mark.usefixtures("downloads")
def test_documents_and_images_use_the_configured_wagtail_models(entry):
    attachments.sync_attachments(entry, [hosted("report.pdf"), hosted("shot.png")])

    document_model = apps.get_model(settings.WAGTAILDOCS_DOCUMENT_MODEL)
    image_model = apps.get_model(settings.WAGTAILIMAGES_IMAGE_MODEL)
    assert document_model.objects.count() == 1
    assert image_model.objects.count() == 1


####################################################################################################
# Filenames
####################################################################################################


# Real filename from the tracker. The interior dots are what defeat Django's
# own shortening, since it reads everything after the first one as the extension.
LONG_NAME = (
    "Marsh_A.__Rao_S._-_Policy_Summary_Report_-_"
    "The_Value_of_Corporate_Transparency_in_Tackling_Crime.pdf"
)


@pytest.mark.usefixtures("downloads")
def test_a_long_filename_with_interior_dots_is_stored(entry):
    attachments.sync_attachments(entry, [hosted(LONG_NAME)])

    document = entry.attachments.get().document
    assert document is not None
    assert len(document.file.name) <= 100


@pytest.mark.usefixtures("downloads")
def test_a_long_filename_keeps_its_full_title(entry):
    attachments.sync_attachments(entry, [hosted(LONG_NAME)])

    assert entry.attachments.get().document.title == LONG_NAME


@pytest.mark.usefixtures("downloads")
def test_a_long_image_filename_is_stored(entry):
    attachments.sync_attachments(entry, [hosted(f"{'x' * 150}.png")])

    image = entry.attachments.get().image
    assert image is not None
    assert len(image.file.name) <= 100


def test_safe_filename_keeps_the_extension():
    assert attachments._safe_filename("report.PDF").endswith(".pdf")


def test_safe_filename_flattens_interior_dots():
    assert attachments._safe_filename("a.b.c.pdf") == "a_b_c.pdf"


def test_safe_filename_replaces_spaces():
    assert attachments._safe_filename("IMG 5547.JPG") == "IMG_5547.jpg"


def test_safe_filename_is_capped():
    assert len(attachments._safe_filename(f"{'x' * 300}.pdf")) <= attachments.MAX_FILENAME


def test_safe_filename_survives_a_name_with_nothing_usable():
    assert attachments._safe_filename("...pdf") == "attachment.pdf"


def test_safe_filename_handles_a_name_with_no_extension():
    assert attachments._safe_filename("justaname") == "justaname"
