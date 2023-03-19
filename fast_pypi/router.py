import mimetypes
import os
import re
from inspect import cleandoc

from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
    Response,
)
from pypiserver import pkg_helpers

from fast_pypi import env, templates

fast_pypi_settings = env.FastPypiSettings()
pypiserver_cfg = fast_pypi_settings.pypiserver_config
file_backend = fast_pypi_settings.file_backend

_valid_upload_filename_regex = re.compile(r"^[a-z0-9_.!+-]+$", re.I)

pypi_router = APIRouter(tags=['pypi'])

@pypi_router.get(
    path='/simple/',
    status_code=status.HTTP_200_OK,
)
def fast_pypi_simple_index() -> HTMLResponse:
    projects = file_backend.get_projects()

    return HTMLResponse(
        content=templates.simple_template(
            title='Package Index',
            links=[
                templates.HTMLLink(
                    link_text=package,
                    link_href=f'{package}/',
                )
                for package in projects
            ],
        ),
        status_code=status.HTTP_200_OK,
    )

@pypi_router.get(
    path='/simple/{project}/',
    status_code=status.HTTP_200_OK,
)
def fast_pypi_simple_project_index(project: str, request: Request) -> Response:
    normalized = pkg_helpers.normalize_pkgname_for_url(project)
    if project != normalized:
        return RedirectResponse(
            url=request.url_for(
                'fast_pypi_simple_project_index',
                project=normalized,
            ),
            status_code=status.HTTP_301_MOVED_PERMANENTLY,
        )

    packages = sorted(
        file_backend.find_project_packages(project),
        key=lambda x: (x.parsed_version, x.relfn),
    )
    if not packages:
        if not config.disable_fallback:
            fallback_url_noslash = config.fallback_url.rstrip('/')
            return RedirectResponse(
                url=f'{fallback_url_noslash}/{project}/',
                status_code=status.HTTP_303_SEE_OTHER,
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Not Found ({normalized} does not exist)'
        )

    print([pkg.fname_and_hash for pkg in packages])

    return HTMLResponse(
        content=templates.simple_template(
            title='Package Index',
            links=[
                templates.HTMLLink(
                    link_text=os.path.basename(pkg.relfn),
                    link_href=str(
                        request.url_for(
                            'package_download',
                            filename=pkg.fname_and_hash,
                        ),
                    ),
                )
                for pkg in packages
            ],
        ),
        status_code=status.HTTP_200_OK,
    )


@pypi_router.get(
    path='/packages/{filename}',
    status_code=status.HTTP_200_OK,
)
def package_download(filename: str) -> FileResponse:
    all_packages = file_backend.get_all_packages()

    for pkg in all_packages:
        if pkg.relfn_unix == filename and pkg.fn:
            file_response = FileResponse(
                filename=filename,
                path=pkg.fn,
                media_type=mimetypes.guess_type(filename)[0],
            )
            if config.cache_control:
                file_response.headers.update({
                    'Cache-Control': f'public, max-age={config.cache_control}',
                })
            return file_response

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Not Found ({filename} does not exist)',
    )

async def file_upload(request: Request) -> None:
    async with request.form() as form:
        content_get = form.get('content')
        content = (
            content_get
            if content_get and isinstance(content_get, UploadFile)
            else None
        )

        gpg_sig_get = form.get('gpg_signature')
        gpg_sig = (
            gpg_sig_get
            if gpg_sig_get and isinstance(gpg_sig_get, UploadFile)
            else None
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Missing "content" file field',
        )

    valid_gpg_sig = (
        content.filename
        and gpg_sig
        and gpg_sig.filename == f'{content.filename}.asc'
    )
    if gpg_sig and not valid_gpg_sig:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cleandoc(f"""
                Unrelated signature {gpg_sig.filename} for package
                {content.filename}
            """),
        )

    upload_files = [file for file in (content, gpg_sig) if file is not None]

    for uf in upload_files:
        invalid_filename = (
            _valid_upload_filename_regex.match(uf.filename) is None
            or pkg_helpers.guess_pkgname_and_version(uf.filename) is None
        )
        if invalid_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid filename: {uf.filename}',
            )

        allow_write = (
            pypiserver_cfg.overwrite
            or not file_backend.exists(uf.filename)
        )
        if not allow_write:


@pypi_router.post(
    path='/packages/update',
    status=status.HTTP_204_NO_CONTENT,
)
def package_update(request: Request) -> None:
    return
