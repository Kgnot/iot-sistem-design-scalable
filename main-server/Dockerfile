# ---- Etapa de build ----
FROM eclipse-temurin:21-jdk-alpine AS build

WORKDIR /app

# Copiamos primero el wrapper y los archivos de config de Gradle para cachear dependencias
COPY gradlew .
COPY gradle gradle
COPY build.gradle* settings.gradle* .
RUN chmod +x gradlew
RUN ./gradlew dependencies --no-daemon || true

# Ahora sí copiamos el código fuente y compilamos
COPY src src
RUN ./gradlew clean bootJar --no-daemon -x test

# ---- Etapa de runtime (imagen final, mucho más liviana) ----
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]