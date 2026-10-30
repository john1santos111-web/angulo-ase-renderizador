"""Ângulo ASE - RunPod Serverless queue handler (no Uvicorn)."""
import base64
import hmac
import ipaddress
import os
from pathlib import Path
import socket
import subprocess
import tempfile
from urllib.parse import urlsplit
import runpod

ALLOWED_HOSTS = {"angulosolucoes.com.br", "gestao.angulosolucoes.com"}
def get_api_key():
    """Lê a configuração do ambiente sem revelar seu conteúdo."""
    return os.environ.get("ASE_API_KEY", "")

def validate_url(url):
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("URL inválida")
    u = urlsplit(url)
    if u.scheme != "https" or u.hostname not in ALLOWED_HOSTS or u.port not in (None, 443) or u.username or u.password:
        raise ValueError("Domínio ou protocolo não autorizado")
    addresses = [ipaddress.ip_address(r[4][0]) for r in socket.getaddrinfo(u.hostname, 443, type=socket.SOCK_STREAM)]
    if not addresses or any(not ip.is_global for ip in addresses):
        raise ValueError("Destino não público")
    return url

def render(url=None, html=None):
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        profile = work / "chromium-profile"
        profile.mkdir(mode=0o700)
        cache = work / "cache"
        cache.mkdir(mode=0o700)
        pdf = work / "documento.pdf"
        prefix = work / "pagina"
        if html is not None:
            if not isinstance(html, str) or len(html.encode("utf-8")) > 100_000:
                raise ValueError("HTML de teste inválido ou muito grande")
            source = work / "teste.html"
            source.write_text(html, encoding="utf-8")
            target = source.as_uri()
        else:
            target = validate_url(url)
        command = [
            "chromium", "--headless", "--no-sandbox", "--disable-gpu",
            f"--user-data-dir={profile}",
            "--disable-dev-shm-usage", "--no-first-run", "--disable-extensions",
            "--disable-background-networking", "--no-pdf-header-footer",
            "--virtual-time-budget=2500", f"--print-to-pdf={pdf}", target
        ]
        try:
            env = os.environ.copy()
            env.update({"HOME": str(work), "XDG_CONFIG_HOME": str(work),
                        "XDG_CACHE_HOME": str(cache), "TMPDIR": str(work)})
            subprocess.run(command, check=True, timeout=50, capture_output=True, env=env)
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or b"").decode("utf-8", "replace")[-500:]
            raise RuntimeError("Chromium falhou: " + details) from exc
        if not pdf.exists() or pdf.stat().st_size < 1000:
            raise RuntimeError("PDF não foi gerado")
        subprocess.run([
            "pdftoppm", "-f", "1", "-singlefile", "-scale-to", "1200",
            "-png", str(pdf), str(prefix)
        ], check=True, timeout=20, capture_output=True)
        png = (work / "pagina.png").read_bytes()
        if not png.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("Imagem PNG inválida")
        return png

def handler(job):
    payload = job.get("input", {})
    if not isinstance(payload, dict):
        return {"ok": False, "error": "input deve ser um objeto"}
    # RunPod queue endpoints validate the Bearer token before dispatching a job.
    # Do not demand a second shared secret in the job input.
    if payload.get("format", "a4-first-page") != "a4-first-page":
        return {"ok": False, "error": "Formato não suportado"}
    if ("url" in payload) == ("html" in payload):
        return {"ok": False, "error": "Informe apenas url (produção) ou html (teste)"}
    try:
        print("ASE_RENDER_START", flush=True)
        png = render(url=payload.get("url"), html=payload.get("html"))
        print("ASE_RENDER_OK", len(png), flush=True)
        return {"ok": True, "content_type": "image/png",
                "image_base64": base64.b64encode(png).decode("ascii"), "bytes": len(png)}
    except (ValueError, RuntimeError, subprocess.SubprocessError, OSError) as exc:
        print("ASE_RENDER_ERROR", type(exc).__name__, str(exc)[:250], flush=True)
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:250]}

if __name__ == "__main__":
    print("ANGULO_ASE_SERVERLESS_HANDLER_V2 iniciado", flush=True)
    runpod.serverless.start({"handler": handler})
