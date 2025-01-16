import json
import psycopg2
import pathlib
import os

class ConnectUserDB(object):
    
    def __init__(self):
        
        with open ("/Users/chenyanjia/MyDjango/mydjango/finance/Django_old/Lab_Training/config/correlation_db.json", 'r')as f:
            self.db_info = json.load(f)


        # Connect to PostgreSQL server
        self.db_conn = psycopg2.connect(
                                    host = self.db_info['USER_DB_HOST'],
                                    database = self.db_info['USER_DB_NAME'],
                                    user = self.db_info['USER_DB_USER'],
                                    password = self.db_info['USER_DB_PASSWORD'],
                                    port = self.db_info['USER_DB_PORT'])
        print("Connect successful!!!!!!!")

        self.db_cursor = self.db_conn.cursor()

    def _get_user_id(self, username):

        
        try:
            sql = f"""SELECT id FROM auth_user WHERE username = %s"""
            username1 = 'test'
            sql_val = (username, )
            self.db_cursor.execute(sql, sql_val)
            result = self.db_cursor.fetchall()

            if not result:
                raise ValueError(f"No user found with username: {username}")
            
            user_id = result[0][0]
            return user_id
        except Exception as e:
            # 如果查詢出現錯誤，回滾事務
            self.db_conn.rollback()
            print(f"Error occurred while fetching user_id: {e}")
            raise  # 重新拋出錯誤，讓上層調用者能夠處理
            
        return user_id

class UserTrackingHandler(ConnectUserDB):

    def __init__(self):
        super().__init__()
        
    # add track-step2
    def add(self, **kwargs):
        
        user_id = self._get_user_id(kwargs['username'])
        
        # 確定要插入的欄位和相應的值
        fields = ['user_id']
        values = [user_id]
        placeholders = ['%s']
        
  
        optional_fields = [
            'stock1', 'start_date', 'end_date', 
            'fastk_period', 'slowk_period', 'slowd_period',    # 新增 KD 指標相關欄位
            'fastperiod', 'slowperiod', 'signalperiod',        # 新增 MACD 指標相關欄位
            'bb_timeperiod', 'nbdevup', 'nbdevdn', 'matype',   # 新增 布林帶相關欄位
            'rsi_timeperiod',                                 # 新增 RSI 指標相關欄位
            'dmi_timeperiod'
        ]

        
        for field in optional_fields:
            if field in kwargs and kwargs[field] is not None:
                fields.append(field)
                values.append(kwargs[field])
                placeholders.append('%s')
        
        # 動態生成 INSERT 語句
        sql = f"""
            INSERT INTO user_tracker1 ({', '.join(fields)}) 
            VALUES({', '.join(placeholders)}) 
            ON CONFLICT DO NOTHING;
        """
        
        # 執行 SQL 語句
        self.db_cursor.execute(sql, values)
        self.db_conn.commit()
        
    # 刪除json檔
    def delete_json_files(self, username, stock, start_date, end_date, window_size, n_times):
        """
        根据指定条件删除 JSON 文件
        Args:
            username: 用户名
            stock: 股票名
            start_date: 开始日期
            end_date: 结束日期
            window_size: 窗口大小
            n_times: 次数
        """
        print('in here no delete')
        print(username, stock, start_date, end_date, window_size, n_times)
        # 文件根目录
        json_dir = '/Users/chenyanjia/MyDjango/mydjango/finance/distance_method/monitor1/common1/tracker_results'
        user_dir = os.path.join(json_dir, username)
        
        print(user_dir)

        # 检查目录是否存在
        if not os.path.exists(user_dir):
            print(f"Directory not found: {user_dir}")
            return

        # 遍历用户目录中的所有文件
        for file_name in os.listdir(user_dir):
            print('in for')
            # 验证文件名是否符合条件
            if stock and stock not in file_name:
                continue
            if start_date and start_date not in file_name:
                continue
            if end_date and end_date not in file_name:
                continue
            if window_size and f"_{window_size}_" not in file_name:
                continue
            if n_times and f"_{n_times}." not in file_name:  # 注意最后的 "." 是文件扩展名前的分隔符
                continue

            # 构建文件路径并删除文件
            file_path = os.path.join(user_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        return

    # remove track-step4
    def remove(self, **kwargs):
        
        user_id = self._get_user_id(kwargs['username'])
        
        # uth.remove(
        #     username=user,
        #     method = method,
        #     start_date=start_date,       
        #     end_date = end_date,  
        #     stock1=stock1,                  
        #     # stock2=stock2,                  
        #     window_size=window_size,                
        #     n_times=std,              
        # )
        
        print('see here')
        print(kwargs['stock1'])
        print(kwargs['start_date'])
        print('see here')
        
        # 起始 WHERE 條件，最少要有 user_id 作為條件
        conditions = ['user_id = %s']
        values = [user_id]
        
        # 可選的條件
        # optional_conditions = [
        #     'method', 'stock1', 'stock2', 'start_date', 'end_date', 'window_size', 'n_times'
        # ]
        optional_conditions = [
            'stock1', 'start_date', 'end_date', 
            # 'window_size', 'n_times',
            'fastk_period', 'slowk_period', 'slowd_period',  # KD 指標條件
            'fastperiod', 'slowperiod', 'signalperiod',     # MACD 指標條件
            'bb_timeperiod', 'nbdevup', 'nbdevdn', 'matype', 
            'rsi_timeperiod',  # 布林帶及 RSI 指標條件
            'dmi_timeperiod'
        ]
        
        # 動態添加條件
        for field in optional_conditions:
            if field in kwargs and kwargs[field] is not None:
                conditions.append(f"{field} = %s")
                values.append(kwargs[field])
        
        # 動態生成 DELETE 語句
        sql = f"""
            DELETE FROM user_tracker1 
            WHERE {' AND '.join(conditions)}
        """
        
        # 執行 SQL 語句
        self.db_cursor.execute(sql, values)
        self.db_conn.commit()
        
        # self.delete_json_files(kwargs['username'], kwargs['stock1'], kwargs['start_date'], kwargs['end_date'], kwargs['window_size'], kwargs['n_times'])
        
        return

    # get user email from name
    def get_user_email(self, user):

        sql = f"""
            SELECT email FROM auth_user 
            where username = %s
        """
        sql_val = (user, )
        self.db_cursor.execute(sql, sql_val)
        res = self.db_cursor.fetchall()[0][0]
        return res
    
    # get tracker's user name & email
    def get_all_user_info(self):
        sql = f"""
            SELECT DISTINCT (auth_user.username), auth_user.email FROM user_tracker1
            INNER JOIN auth_user ON user_tracker1.user_id = auth_user.id;
        """
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()
        return res

    # select track spreads
    def get_all_track_params_combination_from_user(self, user):
        sql = f"""
            SELECT user_tracker1.created_at::date,  start_date::date, end_date::date, stock1,
            fastk_period, slowk_period, slowd_period,
            fastperiod, slowperiod, signalperiod,
            bb_timeperiod, nbdevup, nbdevdn, matype, rsi_timeperiod, dmi_timeperiod
            FROM user_tracker1
            INNER JOIN auth_user ON auth_user.id = user_tracker1.user_id
            WHERE auth_user.username = %s"""
        sql_val = (user, )
        self.db_cursor.execute(sql, sql_val)
        res = self.db_cursor.fetchall()
        return res
    
    # get all track spreads
    def get_all_track_params_combination(self):
        # sql = f"""
        #     SELECT username, user_tracker1.created_at::date,  start_date::date, end_date::date, method,
        #     stock1, stock2, window_size, n_times
        #     FROM user_tracker1
        #     INNER JOIN auth_user ON auth_user.id = user_tracker1.user_id
        #     """  
        sql = f"""
            SELECT username, user_tracker1.created_at::date,  start_date::date, end_date::date,
            stock1, window_size, n_times
            FROM user_tracker1
            INNER JOIN auth_user ON auth_user.id = user_tracker1.user_id
            """
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()
        return res


if __name__ == "__main__":
    uth = UserTrackingHandler()

