__all__ = ['Singleton']


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]

    # 单元测试的时候,使用了单例的会在各个test之间共享,
    # 这是不期望看到的,所以需要重新刷新
    @staticmethod
    def clear():
        Singleton._instances.clear()
