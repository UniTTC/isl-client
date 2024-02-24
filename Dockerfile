# Используем официальный образ Ubuntu
FROM ubuntu:latest

# Устанавливаем зависимости для SPEEDTEST® клиента и Python
RUN apt-get update && \
    apt-get install -y apt-utils && \
    apt-get install -y curl && \
    curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
    apt-get install -y speedtest && \
    apt-get install -y python3 python3-pip && \
    pip3 install pytz PyYAML requests schedule GitPython && \
    apt-get install -y supervisor && \
    apt-get install -y ntp

# Устанавливаем переменные среды
ENV TZ=Asia/Almaty \
    SPEEDTEST_INTERVAL=1200 \
    CLIENT_STATION=Station \
    CLIENT_BRANCH=Branch \
    CLIENT_LATITUDE=0.0 \
    CLIENT_LONGITUDE=0.0 \
    CONNECTION_TYPE=FTTB \
    CONNECTION_LOGIN=test@test \
    CONNECTION_VLAN=1 \
    CONNECTION_IP=000.000.000.000 \
    CONNECTION_TP=70

# Копируем код проекта в контейнер
RUN git clone https://github.com/UniTTC/isl-client.git /opt/isl_client

# Копируем конфигурацию Supervisor из папки dist
COPY /opt/isl_client/dist/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Создаем volume для logs и config
VOLUME ["/opt/isl_client/logs", "/opt/isl_client/config"]

# Устанавливаем рабочую директорию
WORKDIR /opt/isl_client

# Заменяем значения в файле config.yaml
RUN sed -i "s/tp: 1200/intervalSec: ${SPEEDTEST_INTERVAL}/" /opt/isl_client/config.yaml && \
    sed -i "s/station: Kumsistau/station: ${CLIENT_STATION}/" /opt/isl_client/config.yaml && \
    sed -i "s/branch: OSK/branch: ${CLIENT_BRANCH}/" /opt/isl_client/config.yaml && \
    sed -i "s/latitude: 49.680414/latitude: ${CLIENT_LATITUDE}/" /opt/isl_client/config.yaml && \
    sed -i "s/longitude: 83.314745/longitude: ${CLIENT_LONGITUDE}/" /opt/isl_client/config.yaml && \
    sed -i "s/type: FTTB/type: ${CONNECTION_TYPE}/" /opt/isl_client/config.yaml && \
    sed -i "s/login: test@test/login: ${CONNECTION_LOGIN}/" /opt/isl_client/config.yaml && \
    sed -i "s/vlan: 2919/vlan: ${CONNECTION_VLAN}/" /opt/isl_client/config.yaml && \
    sed -i "s/ip: Nan/ip: ${CONNECTION_IP}/" /opt/isl_client/config.yaml && \
    sed -i "s/tp: 70/tp: ${CONNECTION_TP}/" /opt/isl_client/config.yaml 

# Устанавливаем точку входа
ENTRYPOINT ["/usr/bin/supervisord"]
