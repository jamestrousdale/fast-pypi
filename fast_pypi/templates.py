from textwrap import dedent

from pydantic import BaseModel


class HTMLLink(BaseModel):

    link_text: str
    link_href: str

def generate_html_links(links: list[HTMLLink]) -> str:
    return '\n'.join([
        f'<a href="{link.link_href}">{link.link_text}</a><br>'
        for link in links
    ])

def simple_template(title: str, links: list[HTMLLink]) -> str:
    html_links = generate_html_links(links=links)
    return dedent(f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{title}</title>
            </head>
            <body>
                <h1>{title}</h1>
                {html_links}
            </body>
        </html>
    """)
