import re
from typing import Union, List, Dict
from pydantic import BaseModel, ValidationError, validator

class PlayBook(BaseModel):
    dag_id: str
    dag_cn: str
    pb_type: str # playbook类型
    description: str = None # playbook描述
    mttd: str = None
    mttr: str = None
    attck_rule: Union[str, List[str]] = None # 技术编号
    data_source: Union[str, List[str]] = None # 数据源
    ... # 后续更多扩展

    @validator('pb_type')
    def check_pb_type(cls, val):
        if val not in ["运维规则", "安全规则", "审计规则", "临时规则"]:
            raise ValueError('不存在这种规则类型')
        return val

    @validator('mttd')
    def check_mttd(cls, val, values):
        if values["pb_type"] == "安全规则":
            match = re.match(r"^\d+[mhd]{1}$", val)
            if not match:
                raise ValueError('MTTD格式不合法')
            return val

    @validator('mttr')
    def check_mttr(cls, val, values):
        if values["pb_type"] == "安全规则":
            match = re.match(r"^\d+[mhd]{1}$", val)
            if not match:
                raise ValueError('MTTR格式不合法')
            return val

    @validator('attck_rule')
    def check_attck_rule(cls, val, values):
        if values["pb_type"] == "安全规则":
            if isinstance(val, str):
                val = val.split(",")
            for item in val:
                match = re.match(r"^[a-zA-Z]{1}\d{4,6}$", item)
                if not match:
                    raise ValueError('技术点编号格式不合法')
            return ",".join(val)