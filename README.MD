# Установка SPEEDTEST® Клиента и Python Скрипта

## Установка SPEEDTEST Клиента
Этот README-файл содержит инструкции по установке SPEEDTEST® клиента на различных языках программирования.

## Install Options
Если у вас :
1. **Ubuntu/Debian**
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
2. **Fedora/Centos/Redhat**
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
3. **FreeBSD**
    ```bash
    sudo pkg update && sudo pkg install -g libidn2 ca_root_nss
    # Example how to remove conflicting or old versions using pkg
    # sudo pkg remove speedtest
    # FreeBSD 12 install
    sudo pkg add "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-freebsd12-x86_64.pkg"
    # FreeBSD 13 install
    sudo pkg add "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-freebsd13-x86_64.pkg"
    ```

### Установка зависимостей Python Скрипта
Для Python-скрипта убедитесь, что установлена библиотека httpx:
```bash
pip install httpx
```

> **Примечание:** Убедитесь также, что у вас установлены стандартные библиотеки Python, такие как `json`, `asyncio`, `random`, `datetime`, `pytz`, `logging`.

> **Примечание:** Установку делать в `\opt\isl_client`

# Конфигурация

### GraphQL

Для использования SPEEDTEST® клиента вам необходимо настроить параметры GraphQL:

```json
{
    "graphql": {
        "protocol": "http",
        "url": "91.185.5.210",
        "port": 3000,
        "endpoint": "/graphql"
    }
}
```

### Speedtest
Для настройки SPEEDTEST® клиента у вас есть следующие параметры:

```json
{
    "speedtest": {
        "commandString": "speedtest --server-id=48175 -f json --accept-license --accept-gdpr",
        "commandStringWin": "speedtest.exe --server-id=48175 -f json --accept-license --accept-gdpr",
        "intervalSec": 1200,
        "client": {
            "station": "Kumsistau",
            "branch": "OSK",
            "vlan": 2919
        }
    }
}
```
- **commandString:** Команда для выполнения SPEEDTEST® на UNIX-подобных системах.
- **commandStringWin:** Команда для выполнения SPEEDTEST® на системах Windows.
- **intervalSec:** Интервал между запусками SPEEDTEST® в секундах.
- **client:** Параметры клиента SPEEDTEST® с указанием станции, филиала и VLAN.

**Обязательно нужно изменить значения в блоке `client` в вашем JSON-коде, замените текущие значения новыми в соответствии с вашими требованиями:**
```json
{
    "client": {
        "station": "Новое_название_станции",
        "branch": "Новое_название_филиала",
        "vlan": 1234 \\PPPoE vlanID
    }
}
```

### Описания параметров команды speedtest.exe:

- `--server-id=48175`: Указывает идентификатор сервера, на который будет отправлен запрос Speedtest. В данном случае, идентификатор сервера равен 48175. Вы можете заменить это значение на идентификатор сервера, который вы хотите использовать.

- `-f json`: Устанавливает формат вывода результатов Speedtest в JSON. Это позволяет получить результаты в формате JSON для дальнейшей обработки в программном коде или скрипте.

- `--accept-license`: Подтверждает лицензионное соглашение Speedtest. Этот параметр предназначен для автоматического принятия условий лицензии при запуске Speedtest из командной строки.

- `--accept-gdpr`: Подтверждает согласие на обработку данных в соответствии с Общим регламентом по защите данных (GDPR). Этот параметр также используется для автоматического принятия согласия на обработку данных при запуске Speedtest из командной строки.

**Эта команда `speedtest.exe` предназначена для выполнения Speedtest на системах Windows. Она отправляет запрос на указанный сервер, форматирует результаты в формате JSON и автоматически принимает лицензию и согласие на обработку данных.**

## Запуск скрипта при каждом перезапуске системы

Если вы хотите запустить Python-скрипт `runner.py` при каждом перезапуске системы, добавьте следующую строку в ваш файл crontab:

```bash
#crontab -e
@reboot /usr/bin/python3 /opt/isl_client/runner.py >> /opt/isl_client/logs/worker.log 2>&1
```