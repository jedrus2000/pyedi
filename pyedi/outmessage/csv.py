
from .var import Var


class Csv(Var):
    def _getescapechars(self):
        return self.ta_info["escape"]
