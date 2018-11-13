from .var import Var


class Edifact(Var):
    def _getescapechars(self):
        terug = (
                self.ta_info["record_sep"]
                + self.ta_info["field_sep"]
                + self.ta_info["sfield_sep"]
                + self.ta_info["escape"]
        )
        if self.ta_info["version"] >= "4":
            terug += self.ta_info["reserve"]
        return terug
