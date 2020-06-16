#!/bin/bash
cat<<EOF
===============================================================================
To deploy these images to Docker Hub, you need to create 2 repositories on your
  account: One for the Web Applicatoin and another one for the Envoy proxy. 
  They must be named as:
    prefix/mtls-demo-web
    prefix/mtls-demo-proxy
  Please inform the prefix you used to create these repos:
===============================================================================
EOF

while [[ $PREFIX == '' ]]; do
  read -er PREFIX
done

cat<<EOF
===============================================================================
will build and deploy the following images, are you sure ?
  $PREFIX/mtls-demo-web:latest
  $PREFIX/mtls-demo-proxy:latest
===============================================================================
EOF
select yn in Yes No; do
    case $yn in
        Yes) 
          break
        ;; 
        No)
          exit
        ;;
    esac
done


#build the java app
pushd web
./mvnw clean package
ret_code=$?
popd
if [ $ret_code != 0 ]; then
    exit $ret_code
fi


./generate-certs.sh
if [ $? != 0 ]; then
    exit $ret_code
fi

env PREFIX=$PREFIX docker-compose build
if [ $? != 0 ]; then
    exit $ret_code
fi

cat<<EOF
===============================================================================
If you're not logged in on docker hub, the docker utility will ask
for your credentials now. 
===============================================================================
EOF

#push images to docker.hub
docker login
if [ $? != 0 ]; then
    exit $ret_code
fi

docker push "${PREFIX}/mtls-demo-web:latest"
docker push "${PREFIX}/mtls-demo-proxy:latest"