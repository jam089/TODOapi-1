#!/usr/bin/env bash

set -e

echo "Creating ./certs dir."
mkdir ./certs
echo "Start generation public/private key pair.."
openssl genpkey -algorithm RSA -out ./certs/jwt-private.pem -pkeyopt rsa_keygen_bits:2048
echo "Private key created."
openssl rsa -pubout -in ./certs/jwt-private.pem -out ./certs/jwt-public.pem
echo "Public key created."
echo "Start apply migrations.."
alembic upgrade head
echo "Migrations applied!"

exec "$@".
