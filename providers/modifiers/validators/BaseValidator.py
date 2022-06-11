from abc import ABC, abstractmethod
from functools import wraps
from quart import jsonify


class BaseValidator(ABC):
    # src: https://stackoverflow.com/a/11408458
    def _type(self):
        return self.__class__.__name__

    def __init__(self, call_func):
        self.call_func = call_func
        super().__init__()

    @abstractmethod
    def validate(self, param):
        raise NotImplementedError("Implemented in subclass")

    @abstractmethod
    def _validateParam(self, param) -> bool:
        """This function is called by the base class' `__handle` function and is passed the param value.

        Parameters:
        param (any): Parameter value

        Returns:
        bool: validation result
        """
        raise NotImplementedError("Implemented in subclass")

    def _handle(self, func, param):
        @wraps(func)
        def handle(*args, **kwargs):
            # Get the param from kwargs
            param_value = kwargs[param]

            isValid = self._validateParam(param_value)

            if isValid:
                # Return the decorator by calling the passed func
                return self.call_func(func, *args, **kwargs)
            else:
                res = jsonify({"error": "invalid '%s' parameter" % param, "code": 400})
                res.status_code = 400
                return res

        return handle
