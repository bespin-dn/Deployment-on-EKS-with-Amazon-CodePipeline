FROM openjdk:22-jdk

# 디렉터리 변경
WORKDIR /app

# Build 아티팩트 복사
COPY ./build/libs/Deployment-on-EKS-with-Amazon-CodePipeline-0.0.1-SNAPSHOT.war /app

# Run Application
CMD ["java", "-jar", "Deployment-on-EKS-with-Amazon-CodePipeline-0.0.1-SNAPSHOT.war"]
