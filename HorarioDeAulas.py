from openpyxl import load_workbook
from collections import Counter

from operator import itemgetter
import pprint


class Restricao(object):
    def __init__(self, nome):
        self.nome = nome
        self.restricoes = []

    def get_nome(self):
        return self.nome

    def add_restricao(self, horario):
        self.restricoes.append(horario)


class Professor(Restricao):
    def __init__(self, nome):
        super().__init__(nome)
        self.preferencias = []

    def add_preferencia(self, horario):
        self.preferencias.append(horario)

    def tem_preferencia(self, horario):
        return horario in self.preferencias


class Vertice(object):
    def __init__(self, materia, turma, professor):
        self.materia = materia
        self.turma = turma
        self.professor = professor
        self.grau_saturacao = 0
        self.restricoes = []
        self.restricoes_leves = []  # 3 aulas seguidas da mesma matéria
        self.preferencias = []
        self.horarios_sequencia = []

    def tem_restricao(self, horario, leves=False):
        if leves:
            return horario in (self.restricoes + self.restricoes_leves)
        return horario in self.restricoes

    def qtd_restricao(self, leves=False):
        if not leves:
            return len(self.restricoes)
        return len(self.restricoes)+len(self.restricoes_leves)

    def add_restricao(self, horario):
        if horario is not None and horario in self.preferencias:
            self.preferencias.remove(horario)

        if horario is not None and horario in self.horarios_sequencia:
            self.horarios_sequencia.remove(horario)

        if not self.tem_restricao(horario):
            self.restricoes.append(horario)

    def atualiza_restricoes(self):
        for horario in self.professor.restricoes:
            self.add_restricao(horario)

        for horario in self.turma.restricoes:
            self.add_restricao(horario)

    def tem_restricao_leve(self, horario):
        return horario in self.restricoes_leves

    def add_restricao_leve(self, horario):
        if horario is not None and horario in self.preferencias:
            self.preferencias.remove(horario)

        if horario is not None and horario in self.horarios_sequencia:
            self.horarios_sequencia.remove(horario)

        if not self.tem_restricao_leve(horario):
            self.restricoes_leves.append(horario)

    def qtd_preferencia(self):
        return len(self.preferencias)

    def add_preferencia(self, horario):
        if (horario is not None
                and not self.tem_restricao(horario, True)):
            self.preferencias.append(horario)

    def atualiza_preferencias(self):
        for horario in self.professor.preferencias:
            self.add_preferencia(horario)

    def add_horario_sequencia(self, horario):
        if horario not in self.horarios_sequencia:
            self.horarios_sequencia.append(horario)

    def tem_horario_sequencia(self):
        return len(self.horarios_sequencia)

    def eh_horario_sequencia(self, horario):
        return horario in self.horarios_sequencia

    def eh_igual(self, outro_vertice):
        return (outro_vertice.materia == self.materia
                and outro_vertice.turma == self.turma
                and outro_vertice.professor == self.professor)

    def deve_ser_vizinho(self, outro_vertice):
        if (self.eh_igual(outro_vertice)
            or self.turma == outro_vertice.turma
                or self.professor == outro_vertice.professor):
            return True
        return False

    def incrementa_grau_saturacao(self):
        self.grau_saturacao += 1

    def horarios_preferidos(self):
        return [horario[0] for horario in Counter(self.preferencias+self.horarios_sequencia).most_common()]

    def dados(self):
        return 'Mat: {}, Tur: {}, Pro: {}'.format(self.materia, self.turma.nome, self.professor.nome)


class Horario(object):
    def __init__(self, dia, hora):
        self.dia = dia
        self.hora = hora
        self.vertices = []

    def add_vertice(self, vertice):
        igual = False
        for colorido in self.vertices:
            igual = vertice.eh_igual(colorido)

        if igual:
            print('vish')
        self.vertices.append(vertice)

    def turma_tem_aula(self, turma):
        for vertice in self.vertices:
            if vertice.turma.nome == turma:
                return [vertice.materia, vertice.professor.nome]
        return False

    def dados(self):
        return '{} {}'.format(self.dia, self.hora)


class HorarioDeAulas (object):
    def __init__(self, arquivo):
        self.planilha = load_workbook(arquivo)

        self.turmas = dict()
        self.professores = dict()
        self.horarios = dict()
        self.aulas_por_dia = 0
        self.vertices = list()
        self.lista_adjacencia = dict()

        self.inicializa_vertices()
        self.inicializa_horarios()
        self.define_restricoes_professores()
        self.define_restricoes_turmas()
        self.define_preferencias_professores()
        self.atualiza_restricoes_preferencias_vertices()
        self.define_arestas()

    ''' Lê planilha de dados '''
    def inicializa_vertices(self):
        informacoes = self.planilha['Dados']

        if informacoes.max_row == 1:
            return

        informacoes.delete_rows(1)  # Remove cabecalho

        # Laço para criar vertices com a tupla (Matéria, Turma, Professor, Quantidade de Aulas)
        for linha in informacoes:
            materia = linha[0].value
            turma = linha[1].value
            professor = linha[2].value
            quantidade = linha[3].value

            # Verifica se a turma já está no dicionario de turmas
            # Se nao estiver, cria uma nova turma do tipo Restricao e adiciona ao dicionario
            if turma in self.turmas:
                turma = self.turmas[turma]
            else:
                turma = Restricao(turma)
                self.turmas[turma.get_nome()] = turma

            # Verifica se o professor já está no dicionario de professores
            # Se nao estiver, cria um novo professor do tipo Professor e adiciona ao dicionario
            if professor in self.professores:
                professor = self.professores[professor]
            else:
                professor = Professor(professor)
                self.professores[professor.get_nome()] = professor

            # Insere os vertices
            self.insere_vertice((materia, turma, professor), quantidade)

    ''' Lê planilha de configuracoes '''
    def inicializa_horarios(self):
        informacoes = self.planilha['Configuracoes']

        if informacoes.max_row == 1:
            return

        informacoes.delete_rows(1)  # Remove cabecalho

        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        # Laço para inicializar horarios
        for dia in dias:
            self.horarios[dia] = dict()

            for hora in informacoes:
                horario = Horario(dia, str(hora[0].value))
                self.horarios[dia][str(hora[0].value)] = horario

            self.aulas_por_dia = len(self.horarios[dia])

    ''' Lê planilha de restricao de professores '''
    def define_restricoes_professores(self):
        informacoes = self.planilha['Restricao']

        if informacoes.max_row == 1:
            return

        informacoes.delete_rows(1)  # Remove cabecalho

        for restricao in informacoes:
            professor = restricao[0].value
            hora = str(restricao[1].value)
            dia = restricao[2].value

            if (professor in self.professores
                    and dia in self.horarios
                    and hora in list(self.horarios.values())[0]):
                horario = self.horarios[dia][hora]
                self.professores[professor].add_restricao(horario)

    ''' Lê planilha de restricao de turma '''
    def define_restricoes_turmas(self):
        informacoes = self.planilha['Restricoes Turma']

        if informacoes.max_row == 1:
            return

        informacoes.delete_rows(1)  # Remove cabecalho

        for restricao in informacoes:
            turma = restricao[0].value
            hora = str(restricao[1].value)
            dia = restricao[2].value

            if (turma in self.turmas
                and dia in self.horarios
                    and hora in list(self.horarios.values())[0]):
                horario = self.horarios[dia][hora]
                self.turmas[turma].add_restricao(horario)

    ''' Lê planilha de preferencias de professores '''
    def define_preferencias_professores(self):
        informacoes = self.planilha['Preferencias']

        if informacoes.max_row == 1:
            return

        informacoes.delete_rows(1)  # Remove cabecalho

        for preferencia in informacoes:
            professor = preferencia[0].value
            hora = str(preferencia[1].value)
            dia = preferencia[2].value

            if (professor in self.professores
                and dia in self.horarios
                    and hora in list(self.horarios.values())[0]):
                horario = self.horarios[dia][hora]
                self.professores[professor].add_preferencia(horario)

    ''' Atualiza restricoes do vértice com base '''
    def atualiza_restricoes_preferencias_vertices(self):
        for vertice in self.vertices:
            vertice.atualiza_restricoes()
            vertice.atualiza_preferencias()

    def define_arestas(self):
        for indice_v1 in range(len(self.vertices)):
            vertice_1 = self.vertices[indice_v1]
            self.lista_adjacencia[vertice_1] = []

            for indice_v2 in range(len(self.vertices)):
                vertice_2 = self.vertices[indice_v2]

                if vertice_1.deve_ser_vizinho(vertice_2):
                    self.lista_adjacencia[vertice_1].append(vertice_2)

    def insere_vertice(self, dados, qtd=1):
        materia = dados[0]
        turma = dados[1]
        professor = dados[2]
        for i in range(qtd):
            self.vertices.append(Vertice(materia, turma, professor))

    '''
    Aqui se inicia os algoritmos para coloração
    '''
    def dsatur_com_heristica(self):
        debug = 1

        lista_de_horarios = []

        for dia in self.horarios:
            for horario in self.horarios[dia]:
                lista_de_horarios.append(self.horarios[dia][horario])

        vertices_nao_coloridos = self.vertices.copy()

        # inicia aqui a escolha do vertice a ser colorido
        # e também se inicia a coloração
        vertice_escolhido = self.escolher_vertice(vertices_nao_coloridos)

        vertices_nao_coloridos.remove(vertice_escolhido)

        horarios_preferidos = vertice_escolhido.horarios_preferidos()
        horario = lista_de_horarios[0] if len(horarios_preferidos) == 0 else horarios_preferidos[0]

        horarios_com_restricao_leve = []
        iter = 1
        while vertice_escolhido.tem_restricao(horario, True) and iter < len(lista_de_horarios):
            horario = lista_de_horarios[iter]

            if not vertice_escolhido.tem_restricao_leve(horario):
                horarios_com_restricao_leve.append(horario)

            iter += 1

        print(horario.dia, horario.hora)
        flag = True

        if iter == len(lista_de_horarios) and len(horarios_com_restricao_leve) == 0:
            flag = False
        else:
            horario = horarios_com_restricao_leve[0] if iter == len(lista_de_horarios) else horario
            self.define_horario(vertice_escolhido, horario, lista_de_horarios, vertices_nao_coloridos)

        vertice_anterior = vertice_escolhido

        #loop
        while len(vertices_nao_coloridos) > 0 and flag:
            debug += 1
            vertice_escolhido = self.escolher_vertice(
                self.vizinhos_nao_coloridos(vertice_anterior, vertices_nao_coloridos))
            # Se não houver vizinhos sem cor
            vertice_escolhido = self.escolher_vertice(vertices_nao_coloridos) if not vertice_escolhido else vertice_escolhido

            vertices_nao_coloridos.remove(vertice_escolhido)

            horarios_preferidos = vertice_escolhido.horarios_preferidos()

            for horario in horarios_preferidos:
                if vertice_escolhido.tem_restricao(horario):
                    horarios_preferidos.remove(horario)

            if len(horarios_preferidos) > 0:
                horario = horarios_preferidos[0]
            else:
                horarios_com_restricao_leve = []
                iter = 0
                encontrado = False
                while iter < len(lista_de_horarios) and not encontrado:
                    horario = lista_de_horarios[iter]
                    if vertice_escolhido.tem_restricao_leve(horario) and not vertice_escolhido.tem_restricao(horario):
                        horarios_com_restricao_leve.append(horario)

                    if not vertice_escolhido.tem_restricao(horario, True):
                        encontrado = True

                    iter += 1

                if not encontrado and len(horarios_com_restricao_leve) > 0:
                    horario = horarios_com_restricao_leve[0]
                elif not encontrado:
                    print("Nem todos os vértices foram coloridos.")
                    return False

            if vertice_escolhido.turma.nome == 1:
                print('turma {}, dia: {}, horario: {}'.format(vertice_escolhido.turma.nome, horario.dia, horario.hora))

            self.define_horario(vertice_escolhido, horario, lista_de_horarios, vertices_nao_coloridos)

        if not flag:
            print('deu ruim')
        else:
            print('deu bom')

    def vertices_de_maior_grau(self, lista_de_vertices):
        vertices = []
        maior_grau = 0

        for vertice in lista_de_vertices:
            grau = len(self.lista_adjacencia[vertice])
            if grau > maior_grau:
                maior_grau = grau
                vertices = [vertice]
            elif grau == maior_grau:
                vertices.append(vertice)

        return vertices

    def vertices_maior_grau_saturacao(self, lista_de_vertices):
        vertices = []
        maior_grau = 0

        for vertice in lista_de_vertices:
            grau = vertice.grau_saturacao
            if grau > maior_grau:
                maior_grau = grau
                vertices = [vertice]
            elif grau == maior_grau:
                vertices.append(vertice)

        return self.vertices_de_maior_grau(vertices)

    def vertices_com_mais_restricoes(self, lista_de_vertices):
        vertices = []
        maior_quantidade = 0

        for vertice in lista_de_vertices:
            quantidade = vertice.qtd_restricao()
            if quantidade > maior_quantidade:
                maior_quantidade = quantidade
                vertices = [vertice]
            elif quantidade == maior_quantidade:
                vertices.append(vertice)

        return vertices

    def vertices_com_horario_sequencia(self, lista_de_vertices):
        lista_aux = [vertice for vertice in lista_de_vertices if vertice.tem_horario_sequencia()]

        return lista_aux if len(lista_aux) > 0 else lista_de_vertices

    def vertices_com_mais_preferencias(self, lista_de_vertices):
        vertices = []
        maior_quantidade = 0

        for vertice in lista_de_vertices:
            quantidade = vertice.qtd_preferencia()
            if quantidade > maior_quantidade:
                maior_quantidade = quantidade
                vertices = [vertice]
            elif quantidade == maior_quantidade:
                vertices.append(vertice)

        return vertices

    def escolher_vertice(self, lista_de_vertices):
        lista_de_vertices = self.vertices_maior_grau_saturacao(lista_de_vertices)
        lista_de_vertices = self.vertices_com_mais_restricoes(lista_de_vertices)
        lista_de_vertices = self.vertices_com_mais_restricoes(lista_de_vertices)
        lista_de_vertices = self.vertices_com_horario_sequencia(lista_de_vertices)
        lista_de_vertices = self.vertices_com_mais_preferencias(lista_de_vertices)

        return False if len(lista_de_vertices) == 0 else lista_de_vertices[0]

    def define_horario(self, vertice, horario, lista_de_horarios, vertices_nao_coloridos):
        horario.add_vertice(vertice)

        horario_seguinte = lista_de_horarios.index(horario) + 1
        horario_anterior = lista_de_horarios.index(horario) - 1

        # Não faz sentido dar preferencia em aula em sequencia,
        # caso ela seja a primeira do dia seguinte por isso a condicao apos o and
        horario_seguinte = (horario_seguinte if (horario_seguinte < len(lista_de_horarios)
                            and horario_seguinte % self.aulas_por_dia != 0)
                            else None)

        # Não faz sentido dar preferencia em aula em sequencia,
        # caso ela seja a ultima do dia anterior por isso a condicao apos o and
        horario_anterior = (horario_anterior if (horario_anterior >= 0
                            and horario_anterior % self.aulas_por_dia != self.aulas_por_dia - 1)
                            else None)

        # Se o vertice que esta sendo definido o horario
        # ja for uma aula em sequencia, adiciona restricao leve
        # aos vertices vizinhos que são a mesma materia e turma.
        # Se nao for aula em sequencia, adiciona preferencia aos vizinhos
        for vizinho in self.vizinhos_nao_coloridos(vertice, vertices_nao_coloridos):
            vizinho.incrementa_grau_saturacao()
            if vizinho.eh_igual(vertice):
                if vertice.eh_horario_sequencia(horario):
                    if horario_seguinte is not None:
                        vizinho.add_restricao_leve(lista_de_horarios[horario_seguinte])

                    if horario_anterior is not None:
                        vizinho.add_restricao_leve(lista_de_horarios[horario_anterior])
                else:
                    if horario_seguinte is not None:
                        vizinho.add_horario_sequencia(lista_de_horarios[horario_seguinte])

                    if horario_anterior is not None:
                        vizinho.add_horario_sequencia(lista_de_horarios[horario_anterior])
            vizinho.add_restricao(horario)

    def vizinhos_nao_coloridos(self, vertice, vertices_nao_coloridos):
        return [vizinho for vizinho in self.lista_adjacencia[vertice] if vizinho in vertices_nao_coloridos]

    def gerar_horarios_por_turma(self):
        self.dsatur_com_heristica()
        cont = 0
        print('='*10 + str(1) + '='*10)
        for dia in self.horarios:
            print(dia)
            for hora in self.horarios[dia]:
                print(hora, end=': ')
                tem_aula = self.horarios[dia][hora].turma_tem_aula(1);
                if tem_aula:
                    print(tem_aula)
                    cont += 1
            print('')
            print('-'*15)

        print('\ntotal de aulas', cont)


def main():
    a = HorarioDeAulas('instancias/exemplinho.xlsx')
    a.gerar_horarios_por_turma()


if __name__ == '__main__':
    main()
