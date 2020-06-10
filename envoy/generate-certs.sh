#!/bin/bash
if [[ ! -d certs ]]; then
  mkdir certs
fi

if [[ ! -e ca.pem ]]; then
  #create the CA
  openssl req -nodes -newkey rsa:2048 -x509 -keyout certs/ca.key -out certs/ca.pem -subj "/C=BR/ST=SP/L=SP/O=EdSena/OU=mTLS Demo/CN=CA"
fi

if [[ ! -e server.pem ]]; then
  # create the server csr
  openssl req -nodes -newkey rsa:2048 -keyout certs/server.key -out certs/server.csr -subj "/C=BR/ST=SP/L=SP/O=EdSena/OU=mTLS Demo/CN=*"
  #sign the server csr
  openssl x509 -req -in certs/server.csr -CA certs/ca.pem -CAkey certs/ca.key -CAcreateserial -out certs/server.pem -days 365 -sha256
fi

if [[ ! -e client.pem ]]; then
  # create the client csr
  openssl req -nodes -newkey rsa:2048 -keyout certs/client.key -out certs/client.csr -subj "/C=BR/ST=SP/L=SP/O=EdSena/OU=mTLS Demo/CN=client"
  #sign the client csr
  openssl x509 -req -in certs/client.csr -CA certs/ca.pem -CAkey certs/ca.key -CAcreateserial -out certs/client.pem -days 825 -sha256
fi

#remove intermediate files
rm certs/*.csr