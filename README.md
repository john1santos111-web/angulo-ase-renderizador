# Ângulo ASE Renderizador — RunPod Serverless

Este repositório executa um handler de fila RunPod, não um servidor HTTP Uvicorn.

## Arquivos com nomes exatos
- `handler.py` (não `manipulador.py`)
- `requirements.txt` (não `requisitos.txt`)
- `Dockerfile`
- `.dockerignore`
- `.github/workflows/docker-publish.yml`

## Publicação
Substitua os arquivos do repositório pelos do ZIP, preservando os nomes e o caminho `.github/workflows/`. Remova arquivos traduzidos `manipulador.py` e `requisitos.txt` para não causar confusão. Faça commit na branch main. O workflow publica `latest` e a tag SHA completa. Configure o RunPod para usar a imagem publicada.

## Segurança e teste
Configure `ASE_API_KEY` como variável de ambiente secreta no RunPod. O payload de teste deve conter `input.api_key` com o mesmo valor, além de `input.html`. Não compartilhe a chave em capturas. Sem chave, o handler retorna `ok:false`.

Exemplo (substitua somente no painel privado):
```json
{"input":{"api_key":"SUA_CHAVE_PRIVADA","html":"<html><body><h1>TESTE ANGULO ASE</h1></body></html>"}}
```

Resultado esperado: `output.ok=true`, `content_type=image/png` e `image_base64`. `Finished` nos logs não comprova que `ok=true`.

A saída é PNG da primeira página de um PDF gerado pelo Chromium. Não há garantia de fidelidade pixel a pixel para documentos que usam estilos de impressão distintos.
