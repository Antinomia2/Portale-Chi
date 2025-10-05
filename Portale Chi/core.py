import json
import requests
import config

def connected():
    try:
        requests.head("https://gestioneorari.didattica.unimib.it", timeout=3)
        return True
    except requests.RequestException:
        return False

def load_facolta():
    text = requests.get(config.URL_FACOLTA).text
    raw = text.split("var esami_cdl = ")[1].split(";\nvar elenco_scuole = ")[0]
    data = json.loads(raw)
    return {f'{corso["label"]} - {item}': item for item, corso in data.items()}

def build_payload(fac_key: str, today, ayear_later, facolta_dict: dict) -> dict:
    return {
        "et_er": "1",
        "esami_cdl": {facolta_dict[fac_key]},
        "anno2[]": ["1", "2", "3", "4", "5"],
        "datefrom": today.strftime("%d-%m-%Y"),
        "dateto": ayear_later.strftime("%d-%m-%Y"),
        "_lang": "it",
    }

def get_corsi(data_local: dict) -> dict:
    corsi = {}
    insegnamenti = data_local.get("Insegnamenti")
    if insegnamenti:
        for corso in insegnamenti.values():
            dat_ins = corso["DatiInsegnamento"]
            nome = dat_ins["Nome"]
            cod_gen = dat_ins["CodiceGenerale"]
            codice = dat_ins["Codice"]
            key = f"{nome} - {cod_gen}"
            corsi[key] = codice
    return corsi