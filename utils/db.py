import sys
import json
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
                                          database=cls.__database,
                                          )
        except psycopg2.Error as e:
            print(f'Cannot connect to Database!\n' + str(e))
            raise SystemExit('Cannot connect to Database!')
        return connection
    
    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        cls.reload_connection()
        try:
            cursor = cls.__connection.cursor()
            cursor.execute(query)
            cls.__connection.commit()
        except psycopg2.ProgrammingError as e:
            print(f'ProgrammingError in execute_query occured, {e}')
            pass
        except psycopg2.Error as e:
            print(f'Exception in execute_query occured, {e}')
            raise(e)
        
        try:
            return cursor.fetchall()
        except Exception as e:
            pass
    
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
    def get__user(cls, user_id: int):
        """Get user from database
        
        Args:
            user_id (int): telegram user id
        Return:
            user dict
        """ 
        data = PostgresDatabase.execute_query(f'select get_user({user_id})')
        if(data[0][0] == None):
            data = PostgresDatabase.execute_query(f'select add_user({user_id})')
        return data[0][0]
    
    @classmethod
    def add_user(cls, user_id: int):
        """Add new user to database

        Args:
            user_id (int): telegram user id
        """
        PostgresDatabase.execute_query(f'insert into users ("id") values ({user_id})')
        return cls.get_user(user_id)

    @classmethod
    def get_user(cls, user_id: int):
        """Get user from database

        Args:
            user_id (int): telegram user id
        Return:
            tuple(id: int, first_access: datetime, is_teacher: bool)
        """ 
        data = PostgresDatabase.execute_query(f'select * from users where "id"={user_id}')
        if(len(data) == 0):
            return None
        else:
            return data[0]
        
    @classmethod
    def add_verification_request(cls, user_id: int, code: int):
        """Add verifiaction request
        
        Args:
            user_id (int): telegram user id
            code (int): verification code
        """
        PostgresDatabase.execute_query(f'insert into verification ("user", "code") values ({user_id}, {code})')
        
    @classmethod
    def get_verification_request_by_code(cls, code: int):
        """Get verification request by code

        Args:
            code (int): verification code
        """
        data = PostgresDatabase.execute_query(f'select * from verification where "code"={code}')
        if(len(data) == 0):
            return None
        else:
            return data[0]
        
    @classmethod
    def get_verification_request_by_id(cls, user_id: int):
        """Get verification request by code

        Args:
            code (int): telegram user id
        """
        data = PostgresDatabase.execute_query(f'select * from verification where "user"={user_id}')
        if(len(data) == 0):
            return None
        else:
            return data[0]
        
    @classmethod
    def set_teacher(cls, user_id: int):
        """Set user's teacher field to True

        Args:
            user_id (int): telegram user id
        """
        PostgresDatabase.execute_query(f'update users set is_teacher=true where id = {user_id}')
        return cls.get_user(user_id)
    
    @classmethod
    def delete_verification_request(cls, user_id: int):
        """Delete user verification request

        Args:
            user_id (int): telegram user id
        """
        PostgresDatabase.execute_query(f'delete from verification where "user" = {user_id}')