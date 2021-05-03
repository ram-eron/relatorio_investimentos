import matplotlib.pyplot
from matplotlib import colors

from Investir import Log

class Plot():
    def __init__(self, lista_investimentos_total,lista_investimentos, id_cor):
        self.lista_investimentos = lista_investimentos
        self.lista_investimentos_todos = lista_investimentos_total
        self.cor = id_cor

    def plot_todos(self):
        lista_todos_investimentos = []
        lista_imagens = []
        dicionario = {}
        dic_tam = {}
        dados_atuais = {}
        lista_x = []
        ctrl_tam = 0
        max = 0
        matplotlib.pyplot.figure(figsize=(14, 7))

        # novo dicionario com tamanho do dicionario dados atuais para cada invetimento
        for tam in self.lista_investimentos_todos:
            dic_tam[tam['nome']] = len(tam['dados_atuais'])

        # varrendo dicionario tamanho para encontrar o maior
        for k, v in dic_tam.items():
            if v > ctrl_tam:
                ctrl_tam = v

        # encontrando a relação datas para plotagem
        lista_datas = []
        for inv in self.lista_investimentos_todos:
            if len(inv['dados_atuais']) == ctrl_tam:
                for k, v in inv['dados_atuais'].items():
                    lista_datas.append(k)
                break

        # datas da plotagem + dicionario com dados dos invetimentos mais recentes
        for inv in self.lista_investimentos_todos:
            if len(inv['dados_atuais']) < ctrl_tam:
                datas = list(inv['dados_atuais'].keys())
                for dt in lista_datas:
                    dados_atuais[dt] = 0
                for x_ind in range(1, len(list(inv['dados_atuais'].keys()))):
                    dados_atuais[datas[x_ind]] = inv['dados_atuais'][datas[x_ind]]
                dic = inv
                dic['dados_atuais'] = dados_atuais
                lista_todos_investimentos.append(dic)
            else:
                lista_todos_investimentos.append(inv)

        # dados para grafico
        for x in lista_todos_investimentos:
            apoio = []
            for k, v in x['dados_atuais'].items():
                apoio.append(v)
                max = (v + 1000) if max < v else max
                if k not in lista_x:
                    lista_x.append(k)
            dicionario[x['nome']] = apoio

        for k, v in dicionario.items():
            nome = k
            plt_y = v
            matplotlib.pyplot.plot(lista_x, plt_y, label=nome)

        # plot
        with matplotlib.pyplot.style.context('classic'):
            matplotlib.pyplot.title('Investimentos', fontsize=15, weight='bold')
            matplotlib.pyplot.xlabel('Periodo', horizontalalignment='right')
            matplotlib.pyplot.ylabel('Valor em R$')
            matplotlib.pyplot.xticks(rotation=75)
            matplotlib.pyplot.ylim(0,max)
            matplotlib.pyplot.legend()
            matplotlib.pyplot.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
            matplotlib.pyplot.tight_layout()
            matplotlib.pyplot.grid(True)
            matplotlib.pyplot.savefig('investimentos.png')
            #matplotlib.pyplot.show()
            matplotlib.pyplot.close()
            lista_imagens.append('investimentos.png')
        return lista_imagens


    def plot(self):
        colors_list = list(colors._colors_full_map.values())
        lista_imagens = []
        for x in self.lista_investimentos:
            matplotlib.pyplot.figure(figsize=(14, 7))
            data = []
            valor = []
            nome = x['nome']
            for k, v in x['dados_atuais'].items():
                data.append(k)
                valor.append(v)
            Log.informacao(f'Investimento: {nome}, data: {data}, valor: {valor}')
            with matplotlib.pyplot.style.context('Solarize_Light2'):
                matplotlib.pyplot.rcParams['axes.spines.top'] = False
                matplotlib.pyplot.rcParams['axes.spines.right'] = False
                matplotlib.pyplot.text(0.5, 1.08, nome,
                                       horizontalalignment='center',
                                       weight='bold',
                                       fontsize=15,
                                       transform=matplotlib.pyplot.subplot(1, 1, 1).transAxes)
                matplotlib.pyplot.xlabel('Periodo', horizontalalignment='right')
                matplotlib.pyplot.ylabel('Valor em R$')
                for i in range(len(valor)):
                    matplotlib.pyplot.annotate(str(valor[i]), xytext=(1, 12), fontsize=6, rotation=60, color='#121212',
                                               textcoords="offset points", ha='center', va='center',
                                               xy=(data[i], valor[i]))
                    matplotlib.pyplot.xticks(rotation=75, fontsize=7, color='#121212')
                    matplotlib.pyplot.subplots_adjust(bottom=0.25)
                    self.cor = self.cor + 1
                matplotlib.pyplot.bar(data, valor, color=colors_list[self.cor])
                matplotlib.pyplot.savefig(nome + '.png')
                # matplotlib.pyplot.show()
                matplotlib.pyplot.close()
            imagem = nome + '.png'
            lista_imagens.append(imagem)
        return lista_imagens
