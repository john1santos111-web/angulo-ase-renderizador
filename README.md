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

## Pacote completo corrigido
A pasta `.github/workflows/docker-publish.yml` é obrigatória e fica oculta em alguns gerenciadores de arquivos. Envie **o conteúdo** desta pasta do pacote à raiz do repositório GitHub, preservando a estrutura, não a pasta externa `angulo-ase-renderizador-corrigido-completo`.

O workflow dispara a cada commit em `main` e publica as tags `latest` e SHA no GHCR. A imagem não muda automaticamente no RunPod quando o workflow termina: é necessário atualizar a imagem no endpoint e aguardar o worker novo ficar pronto.

A variável `ASE_API_KEY` deve ser configurada no RunPod como segredo ou valor de ambiente; o handler não imprime o valor. Se a referência `{{ RUNPOD_SECRET_... }}` não for resolvida, o worker informa configuração ausente.

A compilação Docker e a execução no RunPod devem ser validadas no GitHub Actions e RunPod, respectivamente.
