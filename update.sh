#!/bin/bash
echo "Actualizando imágenes Docker"
docker compose pull
docker compose up -d
echo "Contenedores actualizados"
