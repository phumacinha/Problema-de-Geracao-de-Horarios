from openpyxl import load_workbook
from pprint import pprint

class Restricao(object):
    def __init__(self, nome):
        self.nome = nome
        self.restricoes = []

    def get_nome(self):
        return self.nome

    def add_restricao(self, horario):
        self.restricoes.append(horario)

    def esta_disponivel(self, horario):
        return horario in self.restricoes


class Professor(Restricao):
    def __init__(self, nome):
        super().__init__(nome)
        self.preferencias = []

    def add_preferencia(self, horario):
        self.preferencias.append(horario)

    def eh_preferencia(self, horario):
        return horario in self.preferencias


class Vertice(object):
    def __init__(self, materia, turma, professor):
        self.materia = materia
        self.turma = turma
        self.professor = professor
        self.horario = None
        self.restricoes = []
        self.preferencias = []

    def eh_restricao(self, horario):
        return horario in self.restricoes

    def add_restricao(self, horario):
        if not self.eh_restricao(horario):
            self.restricoes.append(horario)

    def atualiza_restricoes(self):
        for horario in self.professor.restricoes:
            self.add_restricao(horario)

        for horario in self.turma.restricoes:
            self.add_restricao(horario)

    def eh_preferencia(self, horario):
        return horario in self.preferencias

    def add_preferencia(self, horario):
        if not self.eh_preferencia(horario):
            self.preferencias.append(horario)

    def atualiza_preferencias(self):
        for horario in self.professor.preferencias:
            self.add_preferencia(horario)

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

    def dados(self):
        return 'Mat: {}, Tur: {}, Pro: {}'.format(self.materia, self.turma.nome, self.professor.nome)


class Horario(object):
    def __init__(self, dia, hora):
        self.dia = dia
        self.hora = hora
        self.vertices = []

    def add_vertice(self, vertice):
        self.vertices.append(vertice)


class HorarioDeAulas (object):
    def __init__(self, arquivo):
        self.planilha = load_workbook(arquivo)

        self.turmas = dict()
        self.professores = dict()
        self.horarios = dict()
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

            # Cria novo vertice e o insere
            vertice = Vertice(materia, turma, professor)
            self.insere_vertice(vertice, quantidade)

    ''' Lê planilha de configuracoes '''
    def inicializa_horarios(self):
        informacoes = self.planilha['Configuracoes']
        informacoes.delete_rows(1)  # Remove cabecalho
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        # Laço para inicializar horarios
        for dia in dias:
            self.horarios[dia] = dict()

            for hora in informacoes:
                horario = Horario(dia, str(hora[0].value))
                self.horarios[dia][str(hora[0].value)] = horario

    ''' Lê planilha de restricao de professores '''
    def define_restricoes_professores(self):
        informacoes = self.planilha['Restricao']
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

            for indice_v2 in range(indice_v1+1, len(self.vertices)):
                vertice_2 = self.vertices[indice_v2]

                if vertice_1.deve_ser_vizinho(vertice_2):
                    self.lista_adjacencia[vertice_1].append(vertice_2)

    def insere_vertice(self, vertice, qtd=1):
        for i in range(qtd):
            self.vertices.append(vertice)


    '''
    Aqui se inicia os algoritmos para coloração
    '''



def main():
    HorarioDeAulas('instancias/exemplinho.xlsx')


if __name__ == '__main__':
    main()
