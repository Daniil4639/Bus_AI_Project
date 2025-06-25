# Исключение, выбрасываемое при некорректном определении ключевого объекта на изображении
class NotDetectedException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None