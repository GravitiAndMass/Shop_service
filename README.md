
НАЗВАНИЕ ПРОЕКТА: Shop_service


ЧТО ЭТО ЗА ПРОЕКТ?
-------------------
Shop_service — это готовый шаблон (стартовый проект) для создания интернет-магазина 
на Python с использованием FastAPI, SQLAlchemy и Pydantic.

Проект уже содержит:
- RESTful API для управления товарами, заказами и пользователями
- Подключение к базе данных (PostgreSQL, MySQL, SQLite)
- Аутентификацию и авторизацию пользователей (JWT)
- Управление товарами (добавление, обновление, удаление)
- Управление заказами
- Регистрацию и вход пользователей

Этот проект подходит для:
- Создания собственного интернет-магазина
- Изучения FastAPI и работы с базами данных
- Использования как основы для коммерческих проектов


КАК СКОПИРОВАТЬ ПРОЕКТ С GITHUB

1. Клонируйте репозиторий:

   git clone https://github.com/GravitiAndMass/Shop_service.git

2. Перейдите в папку проекта:

   cd Shop_service

===========================================
КАК УСТАНОВИТЬ И ЗАПУСТИТЬ
===========================================

1. Создайте виртуальное окружение:

   python -m venv venv

2. Активируйте его:
   - Windows: venv\Scripts\activate
   - Mac/Linux: source venv/bin/activate

3. Установите зависимости:

   pip install -r requirements.txt

4. Создайте файл .env (скопируйте из .env.template):

   cp .env.template .env

5. Запустите сервер:

   uvicorn apps.main:app --reload

6. Откройте документацию API в браузере:

   http://localhost:8000/docs


КАК ДОБАВИТЬ ТЕСТОВЫЕ ДАННЫЕ


1. Удалите существующие таблицы (если нужно):

   python -c "from apps.database.manager import DatabaseManager; DatabaseManager().drop_all_tables()"

2. Создайте тестовые данные:

   python demo.py

После этого в базе появятся:
- Тестовые товары с изображениями
- Тестовый администратор
- Тестовый пользователь


ОСНОВНЫЕ ТЕХНОЛОГИИ


- Python 3.8+
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL / SQLite / MySQL


