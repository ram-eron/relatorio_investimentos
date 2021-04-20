import datetime
import json, time

from Investir import Log, Sheet, Historico
from Ploting import Plot
from Email import EnviaEmail

def j_data(json_file):
    with open(json_file, 'r') as read:
        return json.load(read)

def adiciona_horario():
    timestamp = int(datetime.datetime.timestamp(datetime.datetime.now())) + 60
    novo_horario = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')
    return novo_horario

JSON_FILE = 'investimentos.json'  # arquivo json que ficarao os dados recentes
JSON_FILE_HIST = 'investimentos_historico.json'  # arquivo json com os dados historicos para o grafico
SHEET_URL = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = ''  # id da sua planilha
RANGE_NAME = 'Investimentos!A2:E'  # planilha aba Investimentos coluna inciando da celula A2 até E
TOKEN = 'token.json'
CREDENCIAIS = 'credencials.json'

end_email_envio = ''  # endereço de email (gmail) que enviará
senha_envio = ''  # senha para logar na caixa de email do google
end_email_recebe = ''  # endereco do destino
COLOR = 3
hora_programada = ['08:00', '09:00', '10:00', '11:00', '11:50']
hora_envio = '12:00'

def atualiza():
    global hora_programada
    try:
        momento_execucao = datetime.datetime.now().strftime('%H:%M')
        if momento_execucao in hora_programada:
            Log.informacao('criando lista com dados da nuvem')
            sheet = Sheet(TOKEN, CREDENCIAIS, SHEET_ID, RANGE_NAME, SHEET_URL)
            l_sheet = sheet.get_sheet()
            Log.informacao('iniciando o tratamento dos dados')
            relatorio = Historico(l_sheet, JSON_FILE, JSON_FILE_HIST)
            relatorio.atualiza_dados()
            relatorio.atualiza_dados_historico(JSON_FILE_HIST, l_sheet)
            hora_programada = ['08:00', '09:00', '10:00', '11:00', '11:58']
    except Exception as erro:
        Log.informacao(f'houve erro na execuçaõ do metodo atualiza(), {erro}')
        hora_programada.append(adiciona_horario())

def relatorios():
    global hora_envio
    plt = Plot(j_data(JSON_FILE_HIST),j_data(JSON_FILE_HIST), COLOR)
    try:
        momento_execucao = datetime.datetime.now().strftime('%H:%M')
        if momento_execucao == hora_envio:
            Log.informacao('iniciando tratativa para envio do email')
            email = EnviaEmail(end_email_envio, end_email_recebe, senha_envio)
            email.insere_imagem(plt.plot_todos())
            email.insere_imagem(plt.plot())
            email.envia()
            hora_envio = '12:00'
        else:
            Log.informacao(f'aguardando momento do envio do relatorio: {hora_envio} horas')
    except Exception as erro:
        Log.informacao(f'houve erro na execuçaõ do metodo relatorios(), {erro}')
        hora_envio = adiciona_horario()

def main():
    atualiza()
    relatorios()

def teste():
    pass

if __name__ == '__main__':
    while True:
        main()
        # teste()
        time.sleep(60)