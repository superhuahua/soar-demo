"""
    PlayBook Demo
"""
from pydantic import BaseModel, ValidationError, validator
import sys
import os

from models.playbook import PlayBook

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator

from utils.dag_callback import *
from utils.common import set_event

# DAG参数配置
dag_args = {
    'owner': '安全规则',
    'start_date': datetime(2021, 1, 10),
    'retries': 1,
    'on_failure_callback': on_failure_callback,
    'on_retry_callback': on_retry_callback,
    'on_success_callback': on_success_callback
}

# === playbook信息 ===
def get_playbook_info() -> PlayBook:
    # 填写DAG的id与文件名相同
    dag_id = os.path.split(__file__)[-1].split(".")[0]
    # 填写DAG的中文名
    dag_cn = '周期-生产恶意外联'
    # 事件类型, 此项与dag_args中的owner相同, 无需改动
    pb_type = dag_args.get('owner', '未知')
    # DAG的描述
    description = __doc__

    # 安全规则必须填写，如1d，2h，15m
    mttd = '15m'
    mttr = '1d'
    # 涉及ATT&CK，必须填写技术编号，以逗号拼接，如T1100
    attck_rule = 'T1100'
    # 所使用的数据源
    data_source = 'es_fw'

    info = {
        "dag_id": dag_id,
        "dag_cn": dag_cn,
        "pb_type": pb_type,
        "data_source": data_source,
        "mttd": mttd,
        "mttr": mttr,
        "attck_rule": attck_rule,
        "description": description
    }
    
    return PlayBook(**info)

# === END ===

# === 开始编写任务 ===

def task1(**context):
    # 调用elastic接口获取日志信息
    # ...
    
    # 样例数据
    respj = [
        {"src_ip": "192.168.1.2", "dest_ip": "220.181.38.148", "doc_count": 100},
        {"src_ip": "192.168.1.3", "dest_ip": "220.181.38.148", "doc_count": 100}
    ]
    if len(respj) > 0:
        # 存在外联风险
        context['ti'].xcom_push(key='threat_ip_list', value=respj)
        return "情报-内部威胁情报库"
    else:
        # 无外联行为
        return "结束-无外联行为"

def task7(**context):
    # 可通过xcom获取任意节点需要返回的数据
    threat_ip_list = context['ti'].xcom_pull(key='threat_ip_list', task_ids='elastic-获取外网防火墙日志')

    # 构造event数据结构
    Xcom = [
        {
            "taskname": "elastic-获取外网防火墙日志",
            "content": [
                {
                    "title": "外联源地址",
                    "value": ",".join([item["src_ip"] for item in threat_ip_list])
                }
            ]
        }
    ]
    event_info = {
        "event_id": get_playbook_info().dag_id,
        "dag_run_id": context['dag_run'].run_id,
        "the_same_list": [ item['src_ip'] for item in threat_ip_list ],
        "level": "高",
        "content": "生产业务系统恶意外联",
        "xcom": Xcom
    }
    set_event(event_info)
    ...
    
# === 结束编写任务 ===

# 创建DAG图
with DAG(get_playbook_info().dag_cn, default_args=dag_args, catchup=False, schedule_interval=None) as dag:
    # dag的描述
    dag.doc_md = get_playbook_info().description

    # === 将编写的任务加入DAG ===

    _task1 = BranchPythonOperator(
        task_id='elastic-获取外网防火墙日志',
        python_callable=task1,
        provide_context=True
    )

    _task2 = DummyOperator(
        task_id='情报-内部威胁情报库'
    ) 

    _task3 = DummyOperator(
        task_id='情报-微步在线'
    )

    _task4 = DummyOperator(
        task_id='防火墙-添加观察策略'
    )

    _task5 = DummyOperator(
        task_id='告警-邮件通知'
    )

    _task6 = DummyOperator(
        task_id='告警-企微通知'
    )
    
    _task7 = PythonOperator(
        task_id='创建安全事件',
        python_callable=task7,
        provide_context=True
    )
    
    _task1_end = DummyOperator(
        task_id='结束-无外联行为'
    )
    
    _task2_end = DummyOperator(
        task_id='结束-无恶意外联'
    )    
    # === 结束 ===

    # === 编排工作流 ===

    _task1 >> [_task2, _task1_end] 
    _task2 >> _task3 >>  [_task4, _task2_end] 
    _task4 >> [_task5, _task6, _task7] 

    # === 结束 ===
