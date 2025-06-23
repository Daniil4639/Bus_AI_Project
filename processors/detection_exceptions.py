# Исключение, выбрасываемое при некорректном определении ключевого объекта на изображении
class NotDetectedException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


# Исключение, выбрасываемое при отсутствии обеих рук на руле
class HandsAreNotOnWheelException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


# Исключение, выбрасываемое при обнаружении постороннего предмета в руках
class ExtraObjectInHandsException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.groups = args[1]
        else:
            self.message = None
