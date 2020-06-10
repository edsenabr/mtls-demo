FROM openjdk:8-jre-alpine
ARG JAR_FILE
EXPOSE 8080
COPY $JAR_FILE /mtls-demo.jar
CMD ["/usr/bin/java", "-jar", "-Dspring.profiles.active=test", "/mtls-demo.jar"]