FROM node:20-bullseye

# instalar dependencias
RUN apt-get update && \
    apt-get install -y poppler-utils

# instalar n8n
RUN npm install -g n8n

# usar usuario ya existente
USER node

WORKDIR /home/node

EXPOSE 5678

CMD ["n8n"]