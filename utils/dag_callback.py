def on_failure_callback():
    # 当playbook执行失败会调用此函数
    # 可在此处记录日志和告警提示
    ...
    
def on_retry_callback():
    # 当playbook重新执行会调用此函数
    # 可在此处记录日志
    ...

def on_success_callback():
    # 当playbook执行成功会调用此函数
    # 可在此处记录日志
    ...