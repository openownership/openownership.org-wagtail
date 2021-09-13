@hooks.register('before_serve_document')
def track_document_download(document, request):
    from urllib.parse import urlparse

    try:
        referrer = urlparse(request.META['HTTP_REFERER']).path
    except KeyError:
        referrer = None

    download = DocumentDownload(
        document=document,
        referrer_path=referrer
    )

    if request.user.is_authenticated:
        download.user = request.user

    download.save()
