import urllib.request
import json
import time
from datetime import datetime

INMET_TOKEN = "ZDZzZXgxSGZ2M2tDbG1qZHVXNkpwQkwzS1h6T2p4Vko=d6sex1Hfv3kClmjduW6JpBL3KXzOjxVJ"

capitais = {
    "ARACAJU - SE": ("83096", "A402"), "BELEM - PA": ("82193", "A201"),
    "BELO HORIZONTE - MG": ("83587", "A502"), "BOA VISTA - RR": ("82024", "A103"),
    "BRASILIA - DF": ("83377", "A001"), "CAMPO GRANDE - MS": ("83552", "A727"),
    "CUIABA - MT": ("83361", "A901"), "CURITIBA - PR": ("83842", "A807"),
    "FLORIANOPOLIS - SC": ("83980", "A806"), "FORTALEZA - CE": ("82397", "A305"),
    "GOIANIA - GO": ("83423", "A002"), "JOAO PESSOA - PB": ("82791", "A321"),
    "MACAPA - AP": ("82106", "A204"), "MACEIO - AL": ("82994", "A302"),
    "MANAUS - AM": ("82331", "A101"), "NATAL - RN": ("82784", "A304"),
    "PALMAS - TO": ("82596", "A008"), "PORTO ALEGRE - RS": ("83967", "A801"),
    "PORTO VELHO - RO": ("82825", "A106"), "RECIFE - PE": ("82900", "A301"),
    "RIO BRANCO - AC": ("82915", "A108"), "RIO DE JANEIRO - RJ": ("83743", "A602"),
    "SALVADOR - BA": ("83229", "A401"), "SAO LUIS - MA": ("82244", "A308"),
    "SAO PAULO - SP": ("83781", "A701"), "TERESINA - PI": ("82571", "A307"),
    "VITORIA - ES": ("83648", "A612")
}

meses = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
mapa_global = {c: {f"{d:02d}/{m:02d}": set() for m, d_max in enumerate(meses, 1) for d in range(1, d_max + 1)} for c in capitais}

def baixar_dados(url, max_tentativas=3):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for _ in range(max_tentativas):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.loads(response.read().decode('utf-8'))
        except:
            time.sleep(5)
    return []

def processar_reg(dados, cidade, ano):
    for reg in dados:
        dt = reg.get('DT_MEDICAO') or reg.get('dt_medicao')
        if not dt: continue
        dia = dt.split('-')[2].split('T')[0]
        mes = dt.split('-')[1]
        chuva = float(reg.get('CHUVA') or reg.get('chuva') or reg.get('CHUVA_MAX_DIARIA') or reg.get('PRECIPITACAO_TOTAL') or 0)
        if chuva > 0:
            mapa_global[cidade][f"{dia}/{mes}"].add(ano)

ano_atual = datetime.now().year

for cidade, (conv, auto) in capitais.items():
    print(f"--- Iniciando {cidade} ---")
    for ano in range(1961, ano_atual):
        # Convencional
        url_c = f"https://apitempo.inmet.gov.br/token/estacao/diaria/{ano}-01-01/{ano}-12-31/{conv}/{INMET_TOKEN}"
        processar_reg(baixar_dados(url_c), cidade, ano)
        # Automática
        if ano >= 2000:
            url_a = f"https://apitempo.inmet.gov.br/token/estacao/diaria/{ano}-01-01/{ano}-12-31/{auto}/{INMET_TOKEN}"
            processar_reg(baixar_dados(url_a), cidade, ano)
        print(f"[{ano}] OK", end=" | ", flush=True)
    print("\n")

print("Gerando arquivo dados.js...")
with open("dados.js", "w", encoding="utf-8") as f:
    f.write("const historicoChuva = " + json.dumps({c: {d: sorted(list(anos)) for d, anos in dias.items() if anos} for c, dias in mapa_global.items()}, indent=4) + ";")
print("Processo Finalizado com Sucesso.")
