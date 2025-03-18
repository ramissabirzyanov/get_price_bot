# Задание: 
Появилась потребность дать обычному пользователю минимальными усилиями
добавлять еще сайты для парсинга.
Надо написать простого бота, который будет иметь одну кнопку: загрузить файл
1. При нажатии кнопки пользователь прикрепляет файл excel в формате таблицы с
полями:
- a. title - название
- b. url - ссылка на сайт источник
- c. xpath - путь к элементу с ценой
2. Бот получает файл, сохраняет
3. Открывает файл библиотекой pandas
4. Выводит содержимое в ответ пользователю
5. Сохраняет содержимое в локальную БД sqlite
6. Выводит среднюю цену товара из таблицы

Основные поставленные задачи выполнены.

## TODO
 - Тесты
 - Сам бот асинхронный, но пока в этом мало смысла. Потому что парсинг происходит синхронно.
 Поэтому нужно реализовать асинхронный и многопоточный (ThreadPoolExecutor для selenium) парсинг.


## BUILD

Для сборки приложения используется Docker.

**Выполните команды:**
- Скопируйте репозиторий
```bash
git clone https://github.com/ramissabirzyanov/get_price_bot
cd get_price_bot
```
- Создайте файл .env в корне проекта. И установите в нём переменные на основе примера (.env.example).
```bash
touch .env
```
1. Получите токен для бота. Для этого воспользуйтесь телеграм ботом BotFather.
2. Установите ваш токен для переменной TELEGRAM_TOKEN.
3. Значение для переменой SELENIUM_URL скопируйте из .env.example.
- Установить в файле docker-compose тот image для selenium, который вам необходим в зависимости от вашей системы.
Если контейнер запускается на ARM (например, Apple M1/M2), используйте образ seleniarm.
Если контейнер запускается на x86_64 (Intel/AMD), используйте selenium.
- Запустите приложение
```bash
docker-compose up --build
```
