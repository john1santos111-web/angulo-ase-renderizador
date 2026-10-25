import os, subprocess, tempfile, pathlib, hmac, ipaddress, socket
from urllib.parse import urlsplit
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
KEY = os.environ.get('ASE_API_KEY', '')
HOSTS = {'angulosolucoes.com.br', 'gestao.angulosolucoes.com'}
class Request(BaseModel):
    url: str
    format: str = 'a4-first-page'

@app.post('/render')
def render(req: Request, authorization: str = Header(default='')):
    if not KEY or not hmac.compare_digest(authorization, 'Bearer ' + KEY):
        raise HTTPException(401, 'Unauthorized')
    u = urlsplit(req.url)
    if u.scheme != 'https' or u.hostname not in HOSTS or u.port not in (None,443) or u.username or u.password or req.format != 'a4-first-page':
        raise HTTPException(400, 'Invalid document URL')
    # Block hostnames if they unexpectedly resolve to private/reserved addresses.
    try:
        ips = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(u.hostname,443,type=socket.SOCK_STREAM)]
        if not ips or any(not ip.is_global for ip in ips): raise ValueError('non-public address')
    except Exception: raise HTTPException(400, 'Unsafe document host')
    with tempfile.TemporaryDirectory() as d:
        pdf = pathlib.Path(d)/'document.pdf'
        png_prefix = pathlib.Path(d)/'page'
        # Chromium prints the actual A4 document; pdftoppm extracts only page 1.
        try:
            subprocess.run(['chromium','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',
                '--no-pdf-header-footer','--print-to-pdf='+str(pdf),req.url],timeout=35,check=True,capture_output=True)
            if not pdf.is_file() or pdf.stat().st_size < 1000: raise ValueError('Empty PDF')
            subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1200','-png',str(pdf),str(png_prefix)],timeout=12,check=True,capture_output=True)
            image=pathlib.Path(str(png_prefix)+'.png').read_bytes()
            if not image.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('Invalid PNG')
            return Response(image,media_type='image/png',headers={'Cache-Control':'no-store'})
        except Exception: raise HTTPException(502,'Render failed')
