import json
import datetime
import pymysql

from DBUtils.PooledDB import PooledDB

from utils.singleton import singleton
from utils.misc import get_settings


def singleton_raw(cls):
    instance = singleton(cls)
    instance.settings = get_settings()
    return instance


@singleton_raw
class Pool(object):
    __pool = None

    def __init__(self):
        if not self.__pool:
            assert self.settings.get('MYSQL', None), 'mysql args not be found, please check config file'
            self.__class__.__pool = PooledDB(
                                pymysql,
                                mincached=10,
                                maxcached=20,
                                maxshared=10,
                                maxconnections=200,
                                blocking=True,
                                maxusage=100,
                                cursorclass=pymysql.cursors.DictCursor,
                                **self.settings['MYSQL']
                            )
        self._conn = None
        self._cursor = None
        self.__get_conn()

    def __get_conn(self):
        self._conn = self.__pool.connection()
        self._cursor = self._conn.cursor()

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            print(e)

    def __execute(self, sql, param=()):
        count = self._cursor.execute(sql, param)
        print(count)
        return count

    @staticmethod
    def __dict_datetime_obj_to_str(result_dict):
        """
        把字典里面的 datatime 对象转成字符串，使json转换不出错
        :param result_dict:
        :return result_dict:
        """
        if result_dict:
            result_replace = {k: v.__str__() for k, v in result_dict.items() if isinstance(v, datetime.datetime)}
            result_dict.update(result_replace)
        return result_dict

    def select_one(self, sql, param=()):
        """查询单个结果"""
        count = self.__execute(sql, param)
        result = self._cursor.fetchone()
        """:type result:dict"""
        result = self.__dict_datetime_obj_to_str(result)
        return count, result

    def select_many(self, sql, param=()):
        """
        查询多个结果
        :param sql: qsl语句
        :param param: sql参数
        :return: 结果数量和查询结果集
        """
        count = self.__execute(sql, param)
        result = self._cursor.fetchall()
        """:type result:list"""
        [self.__dict_datetime_obj_to_str(row_dict) for row_dict in result]
        return count, result

    def execute(self, sql, param=()):
        count = self.__execute(sql, param)
        return count

    def begin(self):
        """开启事务"""
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """结束事务"""
        if option == 'commit':
            self._conn.autocommit()
        else:
            self._conn.rollback()


if __name__ == "__main__":
    pass
