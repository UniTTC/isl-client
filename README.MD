# Установка скрипта-измерителя скорости

## Установка SPEEDTEST Клиента
Этот README-файл содержит инструкции по установке SPEEDTEST® клиента на различных языках программирования.

1. ### Установка SPEEDTEST Клиента
   1.1. **Ubuntu/Debian**
    ```bash
    ## If migrating from prior bintray install instructions please first...
    # sudo rm /etc/apt/sources.list.d/speedtest.list
    # sudo apt-get update
    # sudo apt-get remove speedtest
    ## Other non-official binaries will conflict with Speedtest CLI
    # Example how to remove using apt-get
    # sudo apt-get remove speedtest-cli
    sudo apt-get install curl
    curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
    sudo apt-get install speedtest
    ```
   1.2. **Fedora/Centos/Redhat**
    ```bash
    ## If migrating from prior bintray install instructions please first...
    # sudo rm /etc/yum.repos.d/bintray-ookla-rhel.repo
    # sudo yum remove speedtest
    ## Other non-official binaries will conflict with Speedtest CLI
    # Example how to remove using yum
    # rpm -qa | grep speedtest | xargs -I {} sudo yum -y remove {}

    curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.rpm.sh | sudo bash
    sudo yum install speedtest
    ```
   1.3. **FreeBSD**
    ```bash
    sudo pkg update && sudo pkg install -g libidn2 ca_root_nss
    # Example how to remove conflicting or old versions using pkg
    # sudo pkg remove speedtest
    # FreeBSD 12 install
    sudo pkg add "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-freebsd12-x86_64.pkg"
    # FreeBSD 13 install
    sudo pkg add "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-freebsd13-x86_64.pkg"
    ```

2. ### Установка зависимостей Python для работы скрипта
    2.1.  Для Python-скрипта убедитесь, что установлены следующие библиотеки:`pytz` `PyYAML` `requests` `schedule` `subprocess` `json` 
    ```bash
    pip install pytz PyYAML requests schedule subprocess json GitPython
    ```

 > **Примечание:** 
 >
 > Убедитесь также, что у вас установлены стандартные библиотеки Python, такие как: `os` `sys` `platform` `time` `logging` `datetime` `pathlib` `argparse` `signal`

3. Клонирование репозитория
   ```bash 
   git clone https://github.com/UniTTC/isl-client.git /opt/isl_client
    ```
> **Примечание:** 
> 
> Установку делать в `\opt\isl_client`

# Конфигурация

### GraphQL

***Пример config.yaml***
```yaml
graphql:
  protocol: http       # Протокол (не изменять)
  url: 91.185.5.210    # URL (не изменять)
  port: 3000           # Порт (не изменять)
  endpoint: /graphql   # Конечная точка (не изменять)

speedtest:
  commandString: speedtest --server-id=48175 -f json --accept-license --accept-gdpr -p   # Команда для выполнения speedtest с указанным сервером (ID 48175) и форматом json (не изменять, 48175 - ID сервера TTC speedtest001.ttc.kz)
  commandStringWin: speedtest.exe --server-id=48175 -f json --accept-license --accept-gdpr -p  # Команда для выполнения speedtest на Windows с указанным сервером (ID 48175) и форматом json (не изменять, 48175 - ID сервера TTC speedtest001.ttc.kz)
  intervalSec: 1200     # Интервал выполнения speedtest в секундах (1200 секунд = 20 минут)

global:
  client:
    station: Station        # Название станции клиента-измерителя (Изменить)
    branch: Branch          # Филиал клиента-измерителя (Изменить)
    location:
      latitude: 49.680414         # Широта местоположения клиента-измерителя (Изменить)
      longitude: 83.314745        # Долгота местоположения клиента-измерителя (Изменить)
  connection:
    type: FTTB              # Тип подключения (FTTB, ADSL, p2pVpn, GPon, WLL) (Изменить)
    login: test@test        # Логин для подключения (если p2pVpn, p2p-host@p2p) (Изменить p2p-host на IP VPn или P2P)
    vlan: 777               # VLAN (если не используется установить как 1)
    ip: 000.000.000.000     # IP-адрес (если применимо, замените на конкретное значение xxx.xxx.xxx.xxx; если PPPoe и нет статики оставить ноли иначе указать статику)
    tp: 70               # Скорость подключения по тарифу/договору
```

### Speedtest
Для настройки клиента у вас есть следующие параметры:

```yaml
speedtest:
  commandString: speedtest --server-id=48175 -f json --accept-license --accept-gdpr -p 
  commandStringWin: speedtest.exe --server-id=48175 -f json --accept-license --accept-gdpr -p 
  intervalSec: 1200 
```

- **commandString:** Команда для выполнения SPEEDTEST® на UNIX-подобных системах.
- **commandStringWin:** Команда для выполнения SPEEDTEST® на системах Windows.
- **intervalSec:** Интервал между запусками SPEEDTEST® в секундах.
  
**Описания параметров команды speedtest.exe:**
- `--server-id=48175`: Указывает идентификатор сервера, на который будет отправлен запрос Speedtest. В данном случае, идентификатор сервера равен 48175. Вы можете заменить это значение на идентификатор сервера, который вы хотите использовать.**
- `-f json`: Устанавливает формат вывода результатов Speedtest в JSON. Это позволяет получить результаты в формате JSON для дальнейшей обработки в программном коде или скрипте.
- `--accept-license`: Подтверждает лицензионное соглашение Speedtest. Этот параметр предназначен для автоматического принятия условий лицензии при запуске Speedtest из командной строки.
-  `--accept-gdpr`: Подтверждает согласие на обработку данных в соответствии с Общим регламентом по защите данных (GDPR). Этот параметр также используется для автоматического принятия согласия на обработку данных при запуске Speedtest из командной строки. 

> **Примечание:** 
> 
> Эта команда `speedtest.exe` предназначена для выполнения Speedtest на системах Windows. Она отправляет запрос на указанный сервер, форматирует результаты в формате JSON и автоматически принимает лицензию и согласие на обработку данных.


### Global
Глобалные настройки клиента
```yaml
client:
    station: Kumsistau   # Название станции клиента-измерителя
    branch: OSK          # Филиал клиента-измерителя
    location:
      latitude: 49.680414         # Широта местоположения клиента-измерителя 49.680414, 83.314745
      longitude: 83.314745        # Долгота местоположения клиента-измерителя
```
#### Секция client
- `station`: Название станции клиента-измерителя.
- `branch`: Филиал клиента-измерителя.
#### Дочерняя секция location:
- `latitude`: Широта местоположения клиента-измерителя (Пример: 49.680414).
- `longitude`: Долгота местоположения клиента-измерителя (Пример: 83.314745).
#### Дочерняя секция connection
- `type`: Тип подключения (FTTB, ADSL, p2pVpn, GPon, WLL).
- `login`: Логин для подключения (если p2pVpn, ставить ip@p2p).
- `vlan`: VLAN (если применимо).
- `ip`: IP-адрес (если применимо, замените на конкретное значение xxx.xxx.xxx.xxx; если PPPoe, оставить пустым).
- `tp`: Скорость подключения по тарифу (Пример: 70).

> **Примечание:**  
> 
> Обязательно нужно изменить значения в блоке `client`, замените текущие значения новыми в соответствии с вашими данными:**


## Запуск скрипта при каждом перезапуске системы
> **Внимание:**  
> 
> Обязательно нужно сделать файл `runner.py`  исполняемым 
> ```bash 
> chmod u+x /opt/isl_client/runner.py ```**


Если вы хотите запустить Python-скрипт `runner.py` при каждом перезапуске системы, добавьте следующую строку в ваш файл crontab:

```bash
#crontab -e 
@reboot /usr/bin/python3 /opt/isl_client/runner.py --daemon >> /opt/isl_client/logs/worker.log 2>&1
```
или

**Для CentOS,Debian,Ubuntu (systemd)**
1. Скопируйте файл службы `isl-client.service`  из `/opt/isl_client/services` в `/etc/systemd/system/`:
```bash
cp /opt/isl_client/services/isl-client.service /etc/systemd/system/isl-client.service
```
1. Перезагрузите конфигурацию systemd и запустите службу:

```bash
sudo systemctl daemon-reload
sudo systemctl start isl
sudo systemctl enable isl  # Добавляет службу в автозагрузку
```

**Для FreeBSD (rc.d)**
1. Скопируйте файл службы `isl-client` из `/opt/isl_client/services/` в `/usr/local/etc/rc.d/`:
```bash
cp /opt/isl_client/services/isl-client /usr/local/etc/rc.d/isl-client
```
2. Сделайте файл `isl-client` исполняемым:

```bash
chmod +x /usr/local/etc/rc.d/isl
```
3. Запустите службу:
```bash
service isl start
```
4. Добавьте службу в автозагрузку:
```bash
sysrc isl_enable=YES
```

