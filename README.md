# BHappyBot
Телеграм-бот, созданный для поздравления с днём рождения участников чата
## Установка (Linux)
У вас должны быть установлены следующие зависимости
- Python версии 3.10 или выше
- PIP 23.3.2 или выше

1. Клонирование репозитория и переход в директорию
```sh
git clone https://github.com/kowyki/BHappyBot.git
cd BHappyBot
```
2. Создание виртуального окружения
```sh
python3 -m venv .venv
```
3. Активация виртуального окружения
```sh
source .venv/bin/activate
```
4. Установка зависимостей
```sh
pip install -r requirements.txt
```
5. Так как для хранения конфиденциальных данных используются переменные окружения, необходимо в папку `bot` добавить файл `.env` с указанием [переменных окружения](https://github.com/kowyki/BHappyBot#переменные-окружения)
## Добавление в автозапуск (Linux)
1. Создание и открытие файла юнита
```sh
sudo nano /etc/systemd/system/BHappyBot.service
``` 
2. Добавление служебной информации в файл юнита, вместо `USERNAME` укажите ваше имя пользователя
```sh
[Unit]
Description=Launch BHappyBot
After=multi-user.target

[Service]
Type=simple
ExecStart=/bin/bash -c '/home/USERNAME/BHappyBot/.venv/bin/python -B /home/USERNAME/BHappyBot/run.py'
Restart=always

[Install]
WantedBy=multi-user.target
```
3. Добавление юнита в автозагрузку
```sh 
sudo systemctl enable BHappyBot.service
``` 
4. Перезапуск сервиса
```sh
sudo systemctl restart BHappyBot.service
```
## Использование
Чтобы начать пользоваться ботом, добавьте его в нужный чат
##### Комманды администрирования
- `/start` — вывести список комманд 
- `/list` — посмотреть список всех пользователей
- `/add` — добавить пользователя
- `/remove` — удалить пользователя
- `/clear` — очистить данные
- `/timer` — запустить ежедневную проверку
- `/table_upload` — загрузить таблицу
- `/table_init` —  занести в базу данных пользователей из таблицы
- `/id` — вывести id чата и топика
## Переменные окружения
- `API_KEY` — токен бота
- `ADMIN_IDS` — уникальные идентификаторы администраторов (перечислять через пробел)
- `CHAT_ID` — идентификатор чата, в который будут отправляться поздравления
- `THREAD_ID` — идентификатор топика (треда) внутри чата