from providers.modifiers.validators.GamertagValidator import GamertagValidator
from providers.modifiers.validators.XuidValidator import XuidValidator


class Validators:
    def __init__(self, call_func):
        self.gamertag = GamertagValidator(call_func).validate
        self.xuid = XuidValidator(call_func).validate
