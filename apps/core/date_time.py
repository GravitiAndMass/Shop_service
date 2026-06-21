from datetime import datetime


class DateTime:

    @classmethod
    def string(cls, obj: datetime):
        """
        Преобразует объект datetime в отформатированную строку.

        Этот метод принимает объект datetime obj и преобразует его в строку
        в формате 'ГГГГ-ММ-ДД ЧЧ:ММ:СС'. Если obj равен None или вычисляется как False,
        метод возвращает None.

        Параметры:
        cls (object): Экземпляр класса (хотя этот аргумент не используется).
        obj (datetime или None): Объект datetime, который нужно преобразовать в строку.

        Возвращает:
        str или None: Отформатированное строковое представление объекта datetime,
        или None, если входное значение равно None или вычисляется как False.
        """

        return obj.strftime('%Y-%m-%d %H:%M:%S') if obj else None

    @classmethod
    def now(cls):
        return datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
