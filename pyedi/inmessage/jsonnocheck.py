from .json import Json


class JsonNoCheck(Json):
    def checkmessage(self, node_instance, defmessage, subtranslation=False):
        pass

    def _getrootid(self):
        return self.ta_info[
            "defaultBOTSIDroot"
        ]  # as there is no structure in grammar, use value form syntax.

