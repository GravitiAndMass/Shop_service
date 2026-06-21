from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from config.database import FastModel


class User(FastModel):
    """
        id (int): Уникальный идентификатор пользователя.
        email (str): Адрес электронной почты пользователя, используемый для аутентификации и связи.
        password (str): Хешированный пароль для аутентификации пользователя.
        first_name (str, optional): Имя пользователя. По умолчанию None.
        last_name (str, optional): Фамилия пользователя. По умолчанию None.
        is_verified_email (bool): Флаг, указывающий, подтверждён ли адрес электронной почты пользователя.
        is_active (bool): Флаг, указывающий, активна ли учётная запись пользователя.
        is_superuser (bool): Флаг, указывающий, имеет ли пользователь права суперпользователя.
        role (str): Роль пользователя в системе, представленная в виде короткой строки.
        date_joined (datetime): Временная метка, указывающая, когда была создана учётная запись пользователя.
        updated_at (datetime, optional): Временная метка, указывающая, когда учётная запись пользователя была последний раз обновлена. По умолчанию None.
        last_login (datetime, optional): Временная метка, указывающая время последнего входа пользователя. По умолчанию None.
        change (relationship): Атрибут связи, связывающий этого пользователя с запросами на изменения, инициированными пользователем.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String, nullable=False)

    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    is_verified_email = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # TODO add unittest and check the default role is 'user', also move role to permissions table
    role = Column(String(5), default="user")

    date_joined = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    change = relationship("UserVerification", back_populates="user", cascade="all, delete-orphan")


class UserVerification(FastModel):
    """
        UserVerification представляет запросы на изменение, инициированные пользователями, такие как изменение адреса электронной почты или номера телефона, которые требуют проверки через OTP (одноразовый пароль).

        Атрибуты:
        id (int): Уникальный идентификатор запроса на верификацию.
        user_id (int): ID пользователя, инициировавшего запрос на верификацию.
        request_type (str): Указывает тип запроса на верификацию (register / reset-password / change-email / change-phone).
        new_email (str): Новый адрес электронной почты, запрошенный пользователем.
        new_phone (str): Новый номер телефона, запрошенный пользователем.
        active_access_token (str, optional): Последний действительный токен доступа, используемый для JWT-аутентификации. По умолчанию None.
        created_at (datetime): Временная метка, указывающая, когда был создан запрос на верификацию.
        updated_at (datetime): Временная метка, указывающая, когда запрос на верификацию был последний раз обновлён.
    """

    __tablename__ = "users_verifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    request_type = Column(String, nullable=True)
    new_email = Column(String(256), nullable=True)
    new_phone = Column(String(256), nullable=True)
    active_access_token = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="change")
