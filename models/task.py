import re
from typing import Union, List, Dict
from pydantic import BaseModel, ValidationError, validator

class Task(BaseModel):
    """
        编排任务所需要展示的内容
    """
    taskname: str
    content: List[Dict[str, str]]
    
    @validator('content')
    def check_pb_type(cls, val):
        if all(key in ["title", "value"] for key in val):
            return val
        else:
           raise ValueError('必须包含title和value字段') 

class Xcom(BaseModel):
    task_list: List[Task]
    ... # 后续更多扩展

class Event(BaseModel):
    event_id: str
    dag_run_id: str
    the_same_list: List[str]
    level: str = None
    content: Union[str, List[str]]
    xcom: Xcom
    ... # 后续更多扩展
    
    


