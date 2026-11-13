from genericparser.plugins.domain.generic_class import GenericStaticABC


class ParserSonarQube(GenericStaticABC):
    def _to_number(self, value):
        """
        Converte o valor da métrica, que o SonarQube entrega como string, para
        float.

        Métrica ausente ou com valor não numérico vira None, que o
        `transform_df_to_python_dict` descarta: assim apenas a medida que
        depende dela deixa de ser calculada, em vez de a extração inteira
        quebrar.
        """
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def extract(self, **kwargs):
        input_file = kwargs.get("input_file")
        metrics = []
        keys = []
        values = []
        for entry in input_file:
            key = entry.get("key", {})
            measures = entry.get("measures", [])
            if entry.get("qualifier") in ["FIL", "UTS", "TRK"]:
                for measure in measures:
                    metric = measure.get("metric", None)
                    value = self._to_number(measure.get("value", None))
                    metrics.append(metric)
                    keys.append(key)
                    values.append(value)
        return {"file_paths": keys, "metrics": metrics, "values": values}


def main():
    return ParserSonarQube()
