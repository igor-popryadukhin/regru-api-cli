# REG.RU API CLI

Инструмент командной строки для работы с API REG.RU. Поддерживает быстрый просмотр услуг и серверов аккаунта, а также управление базовыми настройками подключения.

## Требования
- Python 3.11+
- Наличие API‑токена REG.RU

## Установка
```bash
pip install .
```

После установки консольная команда доступна как `regru-cli`.

## Настройка
1. Сохраните токен (также можно передавать через переменную окружения `REGRU_API_TOKEN`):
   ```bash
   regru-cli config set-token <ваш_токен>
   ```
2. При необходимости задайте базовый URL или имя пользователя:
   ```bash
   regru-cli config set-endpoint https://api.reg.ru/api/regru2
   regru-cli config set-username my_login
   ```
3. Проверьте соединение:
   ```bash
   regru-cli ping
   ```

## Использование
Команда состоит из подкоманд. Наиболее полезные примеры:

### Услуги
```bash
regru-cli services list
```
Выводит список услуг, доступных вашему аккаунту.

### Серверы
```bash
regru-cli servers list
```
Показывает серверы и оборудование, привязанные к аккаунту.

### Общие параметры
- `--token` – временно переопределить токен.
- `--base-url` – указать альтернативный адрес API на время выполнения.
- `--username` – задать логин по умолчанию для операций, требующих параметр `username`.

## Хранение настроек
Конфигурация сохраняется в файле `~/.config/regru-api-cli/config.json` (или в каталоге `XDG_CONFIG_HOME`). Переменные окружения `REGRU_API_TOKEN`, `REGRU_API_USERNAME` и `REGRU_API_URL` всегда имеют приоритет над сохранёнными значениями.

## Разработка
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```
Линтеры и форматирование:
```bash
ruff check src
ruff format src
black src
```
