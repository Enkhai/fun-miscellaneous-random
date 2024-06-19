import os
from abc import ABC
from contextlib import contextmanager
from typing import Optional, Union

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session


class MySqlCRUD(ABC):
    _session: Session = None

    @classmethod
    @logger.catch(message="Failed to connect to database", reraise=True)
    def _create_session(cls) -> None:
        logger.info("Connecting to database...")
        engine = create_engine(f"mysql+mysqlconnector://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASS']}@"
                               f"{os.environ['MYSQL_HOST']}/{os.environ['MYSQL_DB_NAME']}")

        cls._session = sessionmaker(bind=engine)()
        logger.info("Connected to database.")

    def __del__(self):
        if self._session is not None:
            self._session.close()

    _transaction_active = False

    @classmethod
    def get_last_inserted(cls, table: str, pk_index: int) -> dict:
        pk = cls._session.execute(
            text(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
        ).fetchone()
        col_index = pk._fields.index('Column_name')
        return cls.select(table, **{pk[col_index]: pk_index})[0]

    @classmethod
    @contextmanager
    def transaction(cls) -> None:
        cls._transaction_active = True
        try:
            yield
            cls._session.commit()
        except Exception as e:
            cls._session.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
        finally:
            cls._transaction_active = False

    @classmethod
    def _execute(cls,
                 query: str,
                 params: Optional[tuple[dict]] = None,
                 return_last_insert: Optional[bool] = False) -> Optional[Union[list[dict], int]]:
        result = cls._session.execute(text(query), params or ())
        cls._session.flush()
        if not cls._transaction_active:
            cls._session.commit()
        if return_last_insert:
            return result.lastrowid
        try:
            return [dict(zip(result.keys(), v)) for v in result.fetchall()]
        except Exception:
            return None

    @classmethod
    def select(cls,
               table: str,
               columns: Optional[list[str]] = None,
               order_by: Optional[str] = None,
               desc: Optional[bool] = True,
               limit: Optional[int] = None,
               **where) -> list[dict]:
        logger.info(f"Getting data from {table}...")

        columns_fill = ', '.join(columns) if columns else '*'
        where_fill = ' AND '.join([f'{key}=:{key}' for key in where])

        order_fill = f" ORDER BY {order_by}{' DESC' if desc else ' ASC'} " if order_by else ''
        limit_fill = f" LIMIT {limit}" if limit else ''

        query = (f"SELECT {columns_fill} FROM {table}{f' WHERE {where_fill}' if where_fill else ''}"
                 f"{order_fill}{limit_fill}")

        return cls._execute(query, (where,))

    @classmethod
    def insert(cls, table: str, **values) -> dict:
        logger.info(f"Inserting data into {table}...")

        columns_fill = ', '.join(values.keys())
        values_fill = ', '.join(f':{key}' for key in values.keys())

        query = f"INSERT INTO {table} ({columns_fill}) VALUES ({values_fill})"

        pk_index = cls._execute(query, (values,), True)
        return cls.get_last_inserted(table, pk_index)

    @classmethod
    def update(cls, table: str, where: dict, **values) -> list[dict]:
        logger.info(f"Updating data in {table}...")

        columns_fill = ', '.join([f'{key}=:v_{key}' for key in values.copy()])
        where_fill = ' AND '.join([f'{key}=:w_{key}' for key in where.copy()])

        values_cp = {'v_' + key: value for key, value in values.items()}
        where_cp = {'w_' + key: value for key, value in where.items()}

        query = f"UPDATE {table} SET {columns_fill} WHERE {where_fill}"

        cls._execute(query, ({**values_cp, **where_cp},))

        return cls.select(table, **where)

    @classmethod
    def delete(cls, table: str, **where) -> list[dict]:
        logger.info(f"Deleting data from {table}...")

        result = cls.select(table, **where)

        where_fill = ' AND '.join([f'{key}=:{key}' for key in where])

        query = f"DELETE FROM {table} WHERE {where_fill}"

        cls._execute(query, (where,))
        return result


MySqlCRUD._create_session()
