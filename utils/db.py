import sys
import psycopg2

from time import sleep

class PostgresDatabase:
    __instance = None
    __connection = None
    
    __host = None
    __port = None
    __database = None
    
    __user = None
    __password = None

    def __new__(cls, host, port, database, user, password):
        cls.__host = host
        cls.__port = port
        cls.__database = database
        cls.__user = user
        cls.__password = password
        if cls.__instance == None:
            cls.__instance = super(PostgresDatabase, cls).__new__(cls)
            cls.__connection = cls.create_connection()
        return cls.__instance
    
    # Refresh connection
    @classmethod
    def reload_connection(cls):
        cls.__connection = cls.create_connection()
        
    # Connecting database
    @classmethod
    def create_connection(cls):
        connection = None
        try:
            connection = psycopg2.connect(user=cls.__user,
                                          password=cls.__password,
                                          host=cls.__host,
                                          port=cls.__port,
                                          database=cls.__database)
            print('Connection to Postgres database')
        except psycopg2.Error as e:
            print(f'Cannot connect to Database!\n' + str(e))
            raise SystemExit('Cannot connect to Database!')
        return connection
    
    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        if (not cls.test_query()):
            sleep(2)
            cls.reload_connection()
        try:
            cursor = cls.__connection.cursor()
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            pass
        except psycopg2.Error as e:
            print(f'Exception in execute_query occured, {e}')
            raise(e)
    
    # Test query
    @classmethod
    def test_query(cls):
        try:
            cursor = cls.__connection.cursor()
            cursor.execute('select * from users limit 1')
            cls.__connection.commit()
            return True
        except Exception as e:
            print(f'Exception in test_query occured {e}')
            return False
    
    @classmethod
    def add_user(cls, user_id: int):
        """Add new user to database

        Args:
            user_id (int): telegram user id
        """
        PostgresDatabase.execute_query(f'insert into users (id) values ({user_id})')
        return cls.get_user(user_id)

    @classmethod
    def get_user(cls, user_id: int):
        """Get user from database

        Args:
            user_id (int): telegram user id
        Return:
            tuple(id: int, first_access: datetime, is_teacher: bool)
        """ 
        user = PostgresDatabase.execute_query(f'select * from users where id={user_id}')
        if (len(user) == 0):
            return None
        else:
            return user[0]