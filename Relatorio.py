import datetime
import json, time

from Investir import Log, Sheet, Historico
import matplotlib.pyplot
import matplotlib.colors as colors
from Email import EnviaEmail

def j_data(json_file):
    with open(json_file, 'r') as read:
        return json.load(read)

def adiciona_horario():
    timestamp = int(datetime.datetime.timestamp(datetime.datetime.now())) + 60
    novo_horario = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')
    return novo_horario

def plot_todos(lista_investimentos):
    lista_imagens = []
    dicionario = {}
    lista_x = []
    matplotlib.pyplot.figure(figsize=(14, 7))
    for x in lista_investimentos:
        apoio = []
        for k, v in x['dados_atuais'].items():
            apoio.append(v)
            if k not in lista_x:
                lista_x.append(k)
        dicionario[x['nome']] = apoio

    for k, v in dicionario.items():
        nome = k
        plt_y = v
        matplotlib.pyplot.plot(lista_x, plt_y, label=nome)

    matplotlib.pyplot.title('Investimentos', fontsize=15, weight='bold')
    matplotlib.pyplot.xlabel('Periodo', horizontalalignment='right')
    matplotlib.pyplot.ylabel('Valor em R$')
    matplotlib.pyplot.xticks(rotation=75)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.savefig('investimentos.png')
    matplotlib.pyplot.close()
    lista_imagens.append('investimentos.png')
    return lista_imagens

def plot(lista_invetimentos, color):
    colors_list = list(colors._colors_full_map.values())
    lista_imagens = []
    for x in lista_invetimentos:
        data = []
        valor = []
        nome = x['nome']
        for k, v in x['dados_atuais'].items():
            data.append(k)
            valor.append(v)
        Log.informacao(f'Investimento: {nome}, data: {data}, valor: {valor}')
        matplotlib.pyplot.rcParams['axes.spines.top'] = False
        matplotlib.pyplot.rcParams['axes.spines.right'] = False
        matplotlib.pyplot.title(nome, fontsize=15, weight='bold')
        matplotlib.pyplot.xlabel('Periodo', horizontalalignment='right')
        matplotlib.pyplot.ylabel('Valor em R$')
        for i in range(len(valor)):
            matplotlib.pyplot.annotate(str(valor[i]), xytext=(5, 0), fontsize=7,
                                       textcoords="offset points", ha='center', va='bottom', xy=(data[i], valor[i]))
            matplotlib.pyplot.xticks(rotation=75)
            matplotlib.pyplot.subplots_adjust(bottom=0.25)
            color = color + 1
        matplotlib.pyplot.bar(data, valor, color=colors_list[color])
        matplotlib.pyplot.savefig(nome + '.png')
        matplotlib.pyplot.close()
        imagem = nome + '.png'
        lista_imagens.append(imagem)
    return lista_imagens

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
            hora_programada = ['08:00', '09:00', '10:00', '11:00', '11:50']
    except Exception as erro:
        Log.informacao(f'houve erro na execuçaõ do metodo atualiza(), {erro}')
        hora_programada.append(adiciona_horario())

def relatorios():
    global hora_envio
    try:
        momento_execucao = datetime.datetime.now().strftime('%H:%M')
        if momento_execucao == hora_envio:
            Log.informacao('iniciando tratativa para envio do email')
            email = EnviaEmail(end_email_envio, end_email_recebe, senha_envio)
            email.insere_imagem(plot_todos(j_data(JSON_FILE_HIST)))
            email.insere_imagem(plot(j_data(JSON_FILE_HIST), COLOR))
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
