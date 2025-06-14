# ---- Estágio 1: Build ----
# Usamos a imagem oficial do Python 3.10, conforme especificado no seu pyproject.toml.
FROM python:3.10-slim as builder

# Define o diretório de trabalho.
WORKDIR /app

# Instala o Poetry.
# Desativamos a criação de ambientes virtuais pelo Poetry, pois gerenciaremos isso manualmente.
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Copia os arquivos de definição de dependências.
# Copiamos estes primeiro para aproveitar o cache do Docker.
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto, incluindo as de desenvolvimento como o gunicorn.
# A flag --no-root impede que o próprio projeto (first-api) seja instalado neste momento.
RUN poetry install --no-dev --no-root

# Copia o restante do código da aplicação.
COPY . .

# ---- Estágio 2: Final ----
# Começamos de uma nova imagem Python limpa para manter a imagem final leve.
FROM python:3.10-slim

# Define o diretório de trabalho.
WORKDIR /app

# Copia o ambiente virtual com as dependências já instaladas do estágio de build.
COPY --from=builder /app/.venv /app/.venv

# Copia o código da aplicação do estágio de build.
COPY --from=builder /app/first_api /app/first_api
COPY --from=builder /app/main.py /app/main.py

# Ativa o ambiente virtual para os comandos subsequentes.
ENV PATH="/app/.venv/bin:$PATH"

# Comando para executar a aplicação com gunicorn.
# O Cloud Run envia requisições para a porta 8080.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]