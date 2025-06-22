# Тестовое задание на Python разработчика в DimaTech

## Запуск локально

1. Клонируйте репозиторий
    ```bash
   git clone https://github.com/dreamLogicc/dimatech-test.git
   ```
2. Создайте виртуальное окружение и активирейте его 
    ```bash
   python -m venv .venv
   ```
   ```bash
    source .venv/bin/activate  
   ```
3. Установите зависимости
    ```bash
   pip install -r requirements.txt
   ```
4. Запустите приложение
    ```
   python src/main.py
   ```
   
**Note 1**: Я намеренно не добавлял `.env` в `.gitignore`, чтобы не высылать его отдельно.

**Note 2**: Возможно вам придется изменить параметры для БД в файле `.env`.

Swagger будет доступен по адресу http://0.0.0.0:8080/docs

## Запуск в Docker

1. Клонируйте репозиторий
   ```bash
   git clone https://github.com/dreamLogicc/dimatech-test.git
   ```
2. Запустите приложение в Docker
   ```bash
   docker-compose up --build
   ```

Swagger будет доступен по адресу http://0.0.0.0:8080/docs
## Тестова БД

В БД были созданы следующие отношения:

1. user - таблица пользователей. В ней были созданы 2 пользователя:
   ```
    {
      "users": [
        {
          "id": 1,
          "email": "admin@example.com",
          "full_name": "Admin User",
          "hashed_password": "$2b$12$J3/D8U0JzoSskEYYTZVYNu9EFPP51H1XdJ.lIXiJhGISlygv18f8G",
          "role_id": 1
        },
        {
          "id": 2,
          "email": "user@example.com",
          "full_name": "Regular User",
          "hashed_password": "$2b$12$WAM.5gN1NQ36sZzm/JCBsO4zQgGnsjJJpnx4S7vV1mTQ7IO8NclRK",
          "role_id": 2
        }
      ]
    }
   ```
   Логин для обычного пользователя: user@example.com.

   Пароль для обычного пользователя: user123.

   Логин для администратора: admin@example.com

   Пароль для администратора: admin123

2. role - таблица ролей. В ней созданы две роли: Admin и User.
3. transaction - таблица с транзакциями.
4. account - таблица со счетами пользователей. В ней созданы три счета пользователей:
   ```
    {
      "accounts": [
        {
          "id": 2,
          "user_id": 1,
          "amount": 0
        },
        {
          "id": 3,
          "user_id": 2,
          "amount": 0
        },
        {
          "id": 1,
          "user_id": 1,
          "amount": 0
        }
      ]
    }
    ```

