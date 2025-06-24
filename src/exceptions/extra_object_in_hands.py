# Исключение, выбрасываемое при обнаружении постороннего предмета в руках
class ExtraObjectInHandsException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.groups = args[1]
        else:
            self.message = None