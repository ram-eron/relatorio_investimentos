import json
import locale
import logging,coloredlogs, os.path
from datetime import date, datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class Log:
    logging.basicConfig(filename='investimentos.log')

    @staticmethod
    def informacao(msg):
        dt = datetime.now().strftime('%d/%m/%Y %H:%M')
        logging.disable(20)
        logging.addLevelName(21,'MY_INFO')
        coloredlogs.install()
        logging.log(21,f'{dt} - {msg}')

    @staticmethod
    def excecao(msg):
        dt = datetime.now().strftime('%d/%m/%Y %H:%M')
        coloredlogs.install()
        logging.exception(f'{dt} - {msg}')

class DadosExternos():
    @staticmethod
    def cria_lista_Investimentos(lista_de_listas):
        Log.informacao('chamando metodo DadosExternos().cria_lista_Investimentos')
        lista_investimentos = []
        for x in lista_de_listas:
            nome = str(x[0]).strip()
            tipo = str(x[1]).strip()
            valor_inicio = x[4]
            data_inicio = str(x[3]).strip()
            lista_investimentos.append(Investimento(nome, tipo, valor_inicio, data_inicio))
        return lista_investimentos

class Investimento():
    def __init__(self, nome, tipo, valor, data_inicio):
        self._nome = nome
        self._tipo = tipo
        self._valor = self.ajusta_valor(valor)
        self._data_inicio_investimento = data_inicio
        self._dicionario_dados = {data_inicio:self.valor}

    @property
    def valor(self):
        return self._valor

    def ajusta_valor(self,valor):
        return int(str(valor).replace('.',''))

    @property
    def tipo(self):
        return self._tipo

    @property
    def nome(self):
        return self._nome

    @property
    def data_inicio_investimento(self):
        return self._data_inicio_investimento

    @property
    def dicionario_dados(self):
        return self._dicionario_dados

    def adiciona_dicicionario(self,data,valor):
        self._dicionario_dados[data]=valor


class Historico():
    def __init__(self,lista_externa, json_file,json_file_historico):
        self.__lista_investimentos = DadosExternos.cria_lista_Investimentos(lista_externa)
        self.json_file = json_file
        self.json_file_historico = json_file_historico

    @property
    def lista_investimentos(self):
        return self.__lista_investimentos

    def __json_escrever(self,json_file,objetos):
        Log.informacao(f'escrevendo no arquivo: {json_file}')
        with open(json_file, 'w') as j:
            json.dump(objetos, j)

    def __json_ler(self,json_file):
        Log.informacao(f'lendo dados do arquivo: {json_file}')
        try:
            with open(json_file, 'r') as read:
                return json.load(read)
        except:
            Log.informacao(f'arquivo {json_file} nao encontrado')
            return None

    def atualiza_dados(self):
        Log.informacao('chamando metodo Historico().atualiza_dados')
        objetos = []
        for y in self.lista_investimentos:
            Log.informacao(f'Investimento incluido - nome: {y.nome}, tipo: {y.tipo}, data_inicial: {y.data_inicio_investimento}'
                   f'valor: {y.valor}, dados_atuais: {y.dicionario_dados}')
            obj = {'nome': y.nome,
                   'tipo': y.tipo,
                   'data_inicial': y.data_inicio_investimento,
                   'valor_inicial': y.valor,
                   'dados_atuais': y.dicionario_dados}
            objetos.append(obj)
        self.__json_escrever(self.json_file,objetos)

    def __inicializa_json_hist(self):
        Log.informacao('chamando metodo Historico().atualiza_dados')
        objetos = []
        for y in self.lista_investimentos:
            # Log.informacao(f'Investimento incluido - nome: {y.nome}, tipo: {y.tipo}, data_inicial: {y.data_inicio_investimento}'
            #       f'valor: {y.valor}, dados_atuais: {y.dicionario_dados}')
            obj = {'nome': y.nome,
                   'tipo': y.tipo,
                   'data_inicial': y.data_inicio_investimento,
                   'valor_inicial': y.valor,
                   'dados_atuais': y.dicionario_dados}
            objetos.append(obj)
        self.__json_escrever(self.json_file_historico,objetos)

    def novo_investimento(self,json_historico, lista_externa):
        Log.informacao('chamando metodo Historico().novo_investimento')
        novos_investimentos = []
        lista_apoio_e = []
        lista_apoio_i = []
        lista_novos_investimentos = []
        hist = self.__json_ler(json_historico)

        for l_ext in lista_externa:
            lista_apoio_e.append(l_ext[0])
        for inv in hist:
            lista_apoio_i.append(inv['nome'])

        for x in lista_apoio_e:
            if x not in lista_apoio_i:
                for y in lista_externa:
                    if y[0] == x:
                        lista_novos_investimentos.append(y)
                        lista_nova = DadosExternos.cria_lista_Investimentos(lista_novos_investimentos)
                        for inv in lista_nova:
                            obj = {'nome': inv.nome, 'tipo': inv.tipo,
                                   'data_inicial': inv.data_inicio_investimento,
                                   'valor_inicial': inv.valor,
                                   'dados_atuais': inv.dicionario_dados}
                            novos_investimentos.append(obj)
                            Log.informacao(f'Historico().novo_investimento {obj}')
        return novos_investimentos

    def atualiza_dados_historico(self, json_historico, lista_externa):
        Log.informacao('chamando metodo Historico().atualiza_dados_historico')
        objetos = []
        hist = self.__json_ler(json_historico)
        if hist is not None:
            #atualiza lista de investimentos
            hoje = date.today().strftime("%d/%m/%Y")

            # pesquisa por novos investimentos
            for novo_inv in self.novo_investimento(json_historico, lista_externa):
                objetos.append(novo_inv)

            #atualiza os ja existentes
            for dict_h in hist:
                dict_dados_atuais = dict_h['dados_atuais']
                for y in lista_externa:
                # mantendo dicionario sempre com o dado ja existente no arquivo
                    if y[0] == dict_h['nome']:
                        # para cada nome de investimento, aidiciona nos dados atuais os valores do dia corrente
                        dict_dados_atuais[hoje] = int(str(y[2]).replace('.', ''))
                        obj = {'nome': dict_h['nome'],
                               'tipo': dict_h['tipo'],
                               'data_inicial': dict_h['data_inicial'],
                               'valor_inicial': dict_h['valor_inicial'],
                               'dados_atuais': dict_dados_atuais}
                        objetos.append(obj)
                Log.informacao(f'historico montado com valores: {objetos}')
                self.__json_escrever(self.json_file_historico, objetos)
        else:
            Log.informacao(f'nao ha arquivo {json_historico}')
            self.__inicializa_json_hist()

    def rendimentos_str(self,json_historico):
        Log.informacao('chamando metodo Historico().rendimentos_str()')
        locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
        total = 0
        rendimento_dia = 0
        dict_rend = {}
        destaques = {}
        positivos = ""
        negativos = ""
        Log.informacao('iniciando o tratamento dos dados')
        rend = self.__json_ler(json_historico)
        for r in rend:
            dict_rend[r['nome']] = list(r['dados_atuais'].values())
        for k, v in dict_rend.items():
            total += v[-1]
            apoio_rend = v[-1] - v[-2]
            rendimento_dia += apoio_rend
            destaques[k] = apoio_rend

        for k, v in destaques.items():
            if v > 0:
                positivos += f'\n\t{k}: {locale.currency(v)} '
            elif v < 0:
                negativos += f'\n\t{k}: {locale.currency(v)}'

        return f'Total investido: {locale.currency(total)}\n' \
               f'Seu rendimento hoje foi de: {locale.currency(rendimento_dia)}' \
               f'\n\nDestaques positivos: {positivos}\nDestaques negativos: {negativos}'

class Sheet():
    def __init__(self,token_json,credentials_json,sheet_id,range_name,sheet_url):
        self.token_json = token_json
        self.credentials_json = credentials_json
        self.sheet_id = sheet_id
        self.range_name = range_name
        self.sheet_url = sheet_url

    def autentica(self):
        try:
            Log.informacao('chamando metodo Sheet().utentica')
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first time.
            if os.path.exists(self.token_json):
                creds = Credentials.from_authorized_user_file(self.token_json, self.sheet_url)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_json, self.sheet_url)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(self.token_json, 'w') as token:
                    token.write(creds.to_json())
            return creds
        except:
            Log.excecao('Sem acesso externo')

    def get_sheet(self):
        try:
            Log.informacao('chamando metodo Sheet().get_sheet')
            service = build('sheets', 'v4', credentials=self.autentica())
            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId= self.sheet_id,
                                        range=self.range_name).execute()
            values = result.get('values', [])
            return values
        except:
            Log.excecao('Erro ao gerar dados da planilha')
