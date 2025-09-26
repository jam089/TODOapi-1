#!/usr/bin/env bash

set -e

echo "Creating ./certs dir."
mkdir ../TODOapp/certs
echo "Start generation public/private key pair.."
openssl genpkey -algorithm RSA -out ../TODOapp/certs/jwt-private.pem -pkeyopt rsa_keygen_bits:2048
echo "Private key created."
openssl rsa -pubout -in ./certs/jwt-private.pem -out ../TODOapp/certs/jwt-public.pem
echo "Public key created."

exec "$@"