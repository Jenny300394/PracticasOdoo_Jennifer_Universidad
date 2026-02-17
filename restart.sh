#!/bin/bash
echo "Reiniciando contenedores Odoo"
docker compose down
docker compose up -d
echo "Contenedores reiniciados"
