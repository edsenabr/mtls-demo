FROM openjdk:8-jre-alpine
EXPOSE 8080
COPY target/mtls-demo-web-*.jar /mtls-demo.jar
CMD ["/usr/bin/java", "-jar", "-Dspring.profiles.active=test", "/mtls-demo.jar"]