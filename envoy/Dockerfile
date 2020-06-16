FROM envoyproxy/envoy-dev:latest
COPY --chown=envoy:envoy envoy/envoy.yaml /etc/envoy/envoy.yaml
COPY --chown=envoy:envoy certs/server.pem /etc/envoy/server.pem
COPY --chown=envoy:envoy certs/server.key /etc/envoy/server.key
COPY --chown=envoy:envoy certs/ca.pem /etc/envoy/ca.pem
EXPOSE 9901 8081 8082 8083