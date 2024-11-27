import os
import json
import pathlib
import requests

class FuncClient(object):
    _instance = None
    # env = os.environ.get('PROJECT_ENV', 'dev')
    # if env == "prod":
    #     ROOT = os.environ['FUNC_API_ROOT']
    # elif env == "dev":
    #     ROOT = 'http://127.0.0.1:1986/usFunc/'
    # else:
    #     raise EnvironmentError("Unknown environment! Please set the 'ENV' variable to 'production' or 'development'.")
    ROOT='http://127.0.0.1:1986/usFunc/'    
    DISTANCEMETHOD_URL= ROOT + "distance_method/" 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass

    def _send_request(self, url: str, request_body: str):
            request_header = {
                "Content-Type"  : "application/json"
            }
            response = requests.post(url, data=json.dumps(request_body), headers=request_header)
            
            return response  
        
    def pairtrading_backtesting(self,
                params: dict,
                method:str
                ):
        
            request_body = {
                "params" : params,
                "method":method
            }                       

            response = self._send_request(self.DISTANCEMETHOD_URL, request_body)
                
            if response.status_code == 200:
                return response.json()['detail']
            
            elif response.status_code == 404:
                print("It has no trading pair found!")
                print(response.json()['msg'])
            else:
                print("Something wrong at get spreads, status code:", response.status_code)
                print(response.json()['msg'])
                
            return None   
##此檔案處理多個股票數據分析的功能，包括繪製交易信號的價格圖和盈虧圖表。
# 它包含載入數據、執行交易策略、計算交易盈虧的方法。run 方法整合了這些操作以生成交易信號、繪製結果並儲存輸出。        
        
        
        
        