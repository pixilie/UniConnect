# 1. Image Python officielle légère
FROM python:3.12-slim

# 2. Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Dossier de travail dans le conteneur
WORKDIR /server

# 4. Copier les fichiers de dépendances en premier
COPY pyproject.toml uv.lock ./

# 5. Installer les dépendances (utilisation de pip standard pour la compatibilité)
# Pip sait lire le pyproject.toml automatiquement
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# 6. Copier tout le code de l'application
COPY ./app ./app

# 7. Exposer le port
EXPOSE 8000

# 8. Lancer le serveur (basé sur ton app/main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
