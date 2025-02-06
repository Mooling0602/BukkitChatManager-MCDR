from typing import Callable, Any


def execute_if(condition: bool | Callable[[], bool]):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # 动态评估条件
            actual_condition = condition() if callable(condition) else condition
            if actual_condition:
                return func(*args, **kwargs)
            return None  # 可自定义跳过执行时的返回值
        return wrapper
    return decorator