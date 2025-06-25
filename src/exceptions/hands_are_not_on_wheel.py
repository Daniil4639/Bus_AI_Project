# Исключение, выбрасываемое при отсутствии обеих рук на руле
class HandsAreNotOnWheelException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None