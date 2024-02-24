# Use a specific Ubuntu version
FROM python:latest

# Set environment variables
ENV TZ=Asia/Almaty \
    DEBIAN_FRONTEND=noninteractive \
    SPEEDTEST_INTERVAL=1200 \
    CLIENT_STATION=Kumsistau \
    CLIENT_BRANCH=OSK \
    CLIENT_LATITUDE=49.680414 \
    CLIENT_LONGITUDE=83.314745 \
    CONNECTION_TYPE=FTTB \
    CONNECTION_LOGIN=test@test \
    CONNECTION_VLAN=2919 \
    CONNECTION_IP=Nan \
    CONNECTION_TP=70

# Install dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    git \
    curl \
    ntp && \
    git clone https://github.com/UniTTC/isl-client.git /opt/isl_client && \
    python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytz PyYAML requests schedule GitPython && \
    curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash  &&\
    apt-get install -y speedtest

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH" 

# Create a symbolic link for the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Replace values in config.yaml
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

# Set the working directory
WORKDIR /opt/isl_client

# Run the script when the container starts
CMD ["python3", "runner.py", "--daemon"]
