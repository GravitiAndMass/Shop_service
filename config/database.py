import importlib
import os
from operator import and_
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import create_engine, URL, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, Session, Query

from . import settings

testing = False


class DatabaseManager:
    """
        Вспомогательный класс для управления операциями с базой данных с использованием SQLAlchemy.

        DatabaseManager упрощает процесс инициализации и управления подключениями к базе данных, создания таблиц базы данных на основе моделей SQLAlchemy и предоставляет сессию для выполнения операций с базой данных.

        Атрибуты:
        engine (Engine): Движок SQLAlchemy для настроенной базы данных.
        session (Session): Сессия SQLAlchemy для взаимодействия с базой данных.

        Методы:
        init():
        Инициализирует DatabaseManager, создавая движок SQLAlchemy и сессию на основе
        указанной конфигурации базы данных из модуля 'settings'.

        create_database_tables():
        Обнаруживает файлы 'models.py' в поддиректориях папки 'apps' и создаёт соответствующие
        таблицы базы данных на основе моделей SQLAlchemy.

        Пример использования:
        db_manager = DatabaseManager()
    """
    engine: create_engine = None
    session: Session = None

    @classmethod
    def __init__(cls):
        """
            Инициализирует DatabaseManager.

            Этот метод создаёт движок SQLAlchemy и сессию на основе указанной конфигурации базы данных из модуля 'settings'.
        """
        global testing
        db_config = settings.DATABASES.copy()
        if testing:
            db_config["database"] = "test_" + db_config["database"]

        if db_config["drivername"] == "sqlite":
            project_root = Path(__file__).parent.parent
            db_config["database"] = os.path.join(project_root, db_config["database"])

            url = URL.create(**db_config)
            cls.engine = create_engine(url, connect_args={"check_same_thread": False})
        else:
            cls.engine = create_engine(URL.create(**db_config))

        session = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        cls.session = session()

    @classmethod
    def create_test_database(cls):
        """
        Создаёт и настраивает тестовую базу данных для использования в тестах.
        """

        # Set the testing flag to True
        global testing
        testing = True

        # Reinitialize the DatabaseManager for testing
        cls.__init__()
        DatabaseManager.create_database_tables()

    @classmethod
    def drop_all_tables(cls):
        """
            Удаляет все таблицы в текущей базе данных.
        """
        # TODO drop tables for postgres too
        if cls.engine:
            metadata = MetaData()
            metadata.reflect(bind=cls.engine)
            for table_name, table in metadata.tables.items():
                table.drop(cls.engine)

    @classmethod
    def create_database_tables(cls):
        """
        Создаёт таблицы базы данных на основе моделей SQLAlchemy.

        Этот метод обнаруживает файлы models.py в поддиректориях папки apps
        и создаёт соответствующие таблицы базы данных на основе моделей SQLAlchemy,
        определённых в этих файлах.

        Возвращает:
        None
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        project_root = Path(script_directory).parent
        apps_directory = project_root / "apps"

        for app_dir in apps_directory.iterdir():
            if app_dir.is_dir():
                models_file = app_dir / "models.py"
                if models_file.exists():
                    module_name = f"apps.{app_dir.name}.models"
                    try:
                        module = importlib.import_module(module_name)
                        if hasattr(module, "FastModel") and hasattr(module.FastModel, "metadata"):
                            module.FastModel.metadata.create_all(bind=cls.engine)
                    except ImportError:
                        pass

    @classmethod
    def get_testing_mode(cls):
        return testing


class FastModel(DeclarativeBase):
    """
    A base class for creating SQLAlchemy ORM models with built-in CRUD operations.

    This class provides a foundation for defining SQLAlchemy models with common
    database operations like creating, updating, and querying records. It simplifies
    database interactions while ensuring proper session management.

    DeclarativeBase: The SQLAlchemy declarative base class from which this model inherits.

    Class Methods:
        __eq__(column, value):
            Override the equality operator to create filter conditions for querying.

        create(**kwargs):
            Create a new instance of the model, add it to the database, and commit the transaction.

        filter(condition):
            Retrieve records from the database based on a given filter condition.

    Example Usage:
        class Product(FastModel):
            ...

        # Create a new product
        new_product = Product.create(product_name="Example Product", ...)

        # Filter products based on a condition
        active_products = Product.filter(Product.status == "active")
    """

    # TODO update FastModel methods

    @classmethod
    def __eq__(cls, **kwargs):
        filter_conditions = [getattr(cls, key) == value for key, value in kwargs.items()]
        return and_(*filter_conditions) if filter_conditions else True

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new instance of the model, add it to the database, and commit the transaction.

        Args:
            **kwargs: Keyword arguments representing model attributes.

        Returns:
            The newly created model instance.
        """

        instance = cls(**kwargs)
        session = DatabaseManager.session
        try:
            session.add(instance)
            session.commit()
            session.refresh(instance)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return instance

    @classmethod
    def filter(cls, condition):
        """
        Retrieve records from the database based on a given filter condition.

        Args:
            condition: SQLAlchemy filter condition.

        Returns:
            List of model instances matching the filter condition.
        """

        with DatabaseManager.session as session:
            query: Query = session.query(cls).filter(condition)
        return query

    @classmethod
    def get(cls, pk):
        """
        Retrieve a record by its primary key.

        Args:
            pk: The primary key value of the record to retrieve.

        Returns:
            The model instance with the specified primary key, or None if not found
        """
        with DatabaseManager.session as session:
            instance = session.get(cls, pk)
        return instance

    @classmethod
    def get_or_404(cls, pk):
        """
        Retrieve a record by its primary key or raise a 404 HTTPException if not found.

        Args:
            pk: The primary key value of the record to retrieve.

        Returns:
            The model instance with the specified primary key.

        Raises:
            HTTPException(404): If the record is not found.
        """
        with DatabaseManager.session as session:
            instance = session.get(cls, pk)
            if not instance:
                raise HTTPException(status_code=404, detail=f"{cls.__name__} not found")
        return instance

    @classmethod
    def update(cls, pk, **kwargs):
        """
        Update a record by its primary key.

        Args:
            pk: The primary key value of the record to update.
            **kwargs: Keyword arguments representing model attributes to update.

        Returns:
            The updated model instance.

        Raises:
            HTTPException(404): If the record is not found.
        """
        with DatabaseManager.session as session:

            # Retrieve the object by its primary key or raise a 404 exception
            # instance = session.query(cls).get(pk)
            instance = session.get(cls, pk)
            if not instance:
                raise HTTPException(status_code=404, detail=f"{cls.__name__} not found")

            # Update the instance attributes based on the provided kwargs
            for key, value in kwargs.items():
                setattr(instance, key, value)

            try:
                # Commit the transaction and refresh the instance
                session.commit()
                session.refresh(instance)
            except Exception:
                session.rollback()
                raise
        return instance

    @staticmethod
    def delete(instance):

        with DatabaseManager.session as session:

            # destroy
            session.delete(instance)

            try:
                # Commit the transaction and refresh the instance
                session.commit()
            except Exception:
                session.rollback()
                raise
