import uvicorn


def main():
    """Start the uvicorn webserver."""
    uvicorn.run(
        app='fast_pypi.app:app',
        host='0.0.0.0',  # noqa: S104
        port=8080,
        proxy_headers=True,
        forwarded_allow_ips='*',
    )
