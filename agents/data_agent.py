import pandas as pd
import json
import toml


class DataAgent:

    @staticmethod
    def load_file(uploaded_file):

        filename = uploaded_file.name.lower()

        if filename.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        elif filename.endswith(".json"):

            data = json.load(uploaded_file)
            df = pd.DataFrame(data)

        elif filename.endswith(".toml"):

            content = uploaded_file.read().decode("utf-8")
            data = toml.loads(content)

            if "records" in data:
                df = pd.DataFrame(data["records"])
            else:
                raise ValueError(
                    "В TOML ожидается секция [records]"
                )

        else:
            raise ValueError(
                "Поддерживаются только CSV, JSON и TOML"
            )

        return df