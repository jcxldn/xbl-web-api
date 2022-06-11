from providers.modifiers.validators.BaseValidator import BaseValidator


class GamertagValidator(BaseValidator):
    def _validateParam(self, param):
        # 1. Check type
        if type(param) == str:
            # Cast param to string
            param: str = param

            # Check string and return boolean
            # Gamertags used to be 15 chars long
            # Now are max. 12 to allow gamertags with suffixes to be supported on legacy platforms
            return len(param) <= 15
        else:
            # Wrong type, return false
            return False

    def validate(self, param="gamertag"):
        def dec(func):
            return self._handle(func, param)

        return dec
