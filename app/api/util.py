# -- coding: utf-8 --
from sqlalchemy.orm import Session
from app import crud, models, schemas
import time
def make_return(code,memo):
    return {'code': code, 'result': memo}

cache_master_rate={}
cache_master_rate_time=0
cache_master_rate_refresh_interval=7200
def load_master_rate(db:Session):
    global cache_master_rate_time, cache_master_rate
    if int(time.time())-cache_master_rate<cache_master_rate_refresh_interval:
        return
    rates = {}
    counts ={}

    res = crud.order.get_all_rate_orders(db,-1)
    for one_data in res:
        rate = int(one_data.comment_rate)
        master_id = one_data.master_id
        if str(master_id) in rates:
            rates[str(master_id)]+=rate
            counts[str(master_id)]+=1
        else:
            rates[str(master_id)] = rate
            counts[str(master_id)] = 1
    cache_master_rate = {}
    for k,v in rates.items():
        cache_master_rate[k] = "%.1f"%(float(v)/counts[k])
    cache_master_rate_time = int(time.time())

