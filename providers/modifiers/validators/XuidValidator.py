from providers.modifiers.validators.BaseValidator import BaseValidator


class XuidValidator(BaseValidator):
    def _validateParam(self, param):
        # 1. Check type
        if type(param) == int:
            # Cast param to int
            param: int = param

            # XUIDs are 16 chracters long
            return len(param) == 16
        else:
            # Wrong type
            return False

    def validate(self, param="id"):
        def dec(func):
            return self._handle(func, param)

        return dec
