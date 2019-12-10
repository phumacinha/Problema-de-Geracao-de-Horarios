# Problema de Programação de Horários de Aula

O problema de programação de horários de aula consiste em organizar encontros de alunos e professores respeitando-se várias restrições. Essa tarefa possui grande dificuldade de ser executada manualmente, já que deve-se respeitar as restrições e procurar atender certas preferências.

O projeto aqui apresentado é resultado do projeto final da disciplina de Algoritmos em Grafos do curso de Ciência da Computação, ministrada pelo Professor Mayron Moreira, do Departamento de Ciência da Computação, UFLA.

Você também poderá obter os arquivos do projeto e executá-los em sua máquina.

    git clone https://github.com/phumacinha/Problema-de-Programacaoo-de-Horarios-de-Aula
    
## Tecnologias Utilizadas
Foi utilizada a linguagem Python 3.7.3. Foram necessárias as bibliotecas:
- openpyxl para a leitura e escrita de arquivos;
- collections para comparação de dicionários;
- path para verificação de arquivo;
- argparse para tratar argumentos passados pelo terminal.

## Problema proposto
O problema proposto consiste em implementar um algoritmo baseado em coloração de vértices para automatizar a tarefa de designar horários a turmas já pré-estabelecidas, levando em conta as seguintes restrições obrigatórias:
- **[R1]** não é permitida a alocação de duas aulas para um mesmo professor no mesmo horário;
- **[R2]** não pode haver duas aulas para uma mesma turma no mesmo horário;
- **[R3]** todas as aulas devem ser alocadas ao longo dos dias de funcionamento da escola e turnos de aula pré-determinados;
- **[R4]** professores não devem ser alocados em horários nos quais eles não podem estar presentes.

Além disso, outras restrições são de caráter desejável, isto é, podem não ser respeitadas de acordo com a necessidade. São elas:
- **[R5]** uma mesma turma não deverá ter três ou mais aulas geminadas da mesma disciplina, em horários sequenciais;
- **[R6]** não deverá haver horários de aula separados por grandes janelas entre aulas, para uma mesma turma. Exemplo: suponha que durante um dia, os alunos tivessem 5 horários de aulas. Então, considere que no 1° e 2° horários houvesse aula, depois no 3° horário houvesse uma janela, e nos 4° e 5° horários os alunos voltassem a ter aulas. Logo, a solução sofreria uma penalidade. O ideal seria ter 4 aulas sequenciais, e o 5° horário livre.
- **[R7]** deve-se buscar atender às preferências de cada professor em relação a dias ou horários em que possa lecionar.

## Algoritmo implementado
Para modelar o problema em um grafo, foram implementadas cinco classes dos tipos Restricao, Professor, Vertice, Horario, HorarioDeAula.
### Classes implementadas
#### Restricao
Classe para instanciar objetos que contenham algum tipo de restrição, como professores e turmas.
Possui como atributos o nome do objeto que possui a restrição e a lista de horários restritos àquele objeto.
#### Professor
Classe para instanciar objetos do tipo Professor. Essa classe herda de Restricao. Além de restrições, um objeto do tipo professor também possui preferências.
Possui como atributos a lista de horários preferidos pelo professor além da quantidade de preferências atendidas.
#### Vertice
Classe para instanciar vértices do grafo. São as aulas da instituição. O vértice é a representação de uma aula, onde há uma matéria definida, uma turma e um professor.
#### Horario
Classe que define horários que as aulas podem ser ministradas. Possuem como atributos o dia, a hora e a lista de aulas (vértices) que serão alocadas nesse horário.
#### HorarioDeAula
É a classe principal do programa. Nela, o grafo é montado analisando as informações de uma planilha que contenha os dados da instituição de ensino, como a designação das aulas (tuplas com matéria, professor e turma), horários de início das aulas, restrições de turmas e professores, além das preferências dos professores. Além disso, essa classe é responsável por implementar o método chamado dsatur_com_heurirtica() que será analisado na sequência desse documento.

### Funcionamento
Ao instanciar um objeto do tipo HorarioDeAula, deve ser passado como parâmetro o caminho do arquivo com extensão .xlsx que contenha os dados da escola. A partir dos dados lidos, são instanciados os vertices, os horários de aula, são definidas as restrições de cada professor e turma e, por fim, são definidas as preferências dos professores. Logo após, as restrições e preferências de cada vértice (aula) são atualizadas de acordo com seu respectivo professor e turma. Após, deve-se encontrar os pares de vértices que serão vizinhos. Para serem definidos como vizinhos, os vértices devem possuir, no mínimo, igualdade em relação à turma ou ao professor, respeitando, assim, as restrições **R1** e **R2**.

Com o grafo montado, pode ser aplicado o método dsatur_com_heuristica().

#### Método dsatur_com_heuristica()
O método de coloração implementado foi baseado no algoritmo de DSATUR, onde os vértices de maior grau de saturação possuem prioridade na coloração. Porém, com as restrições e preferências apresentadas, algumas adaptações foram necessárias para se obter um resultado mais próximo do ideal.
Nessa heurística são priorizados em ordem:

- Vértices com maior número de restrições;
- Vértices com maior grau de saturação;
- Vértices com maior grau no grafo original;
- Vértices com possibilidade de horário em sequência;
- Vértices com mais preferências.

Além disso, ao encontrar o vértice a ser colorido, o algoritmo tenta colori-lo de acordo com sua lista de horários preferidos. Caso não consiga, a busca da menor cor possível para coloração se inicia do menor horário já utilizado até o momento. Isso evita que em turmas com poucas aulas, caso as primeiras aulas sejam alocadas no meio da semana, as demais não sejam alocadas no início da semana. Procura-se sempre preencher por completo cada dia que possua aula.

#### Instanciação do objeto de tipo HorarioDeAula
Ao instanciar um objeto do tipo HorarioDeAula, pode-se definir o parâmetro prioridade_aula_sequencial como True ou False. Esse parâmetro definido como True permite que o algoritmo insira nos vértices, em uma lista chamada horarios_sequencia, o horário anterior e sucessor aos horários em que a mesma aula é ministrada. Essa lista é verificada sempre que se procura uma cor para o vértice que a possui. Esses horários são tidos como prioridade para que a mesma matéria seja ministrada em sequência. Com essa lista, também é possível verificar se já há 2 aulas em sequência, limitando uma terceira aula seguida. Porém, através de testes, verificou-se que esse parâmetro aumenta a ineficiência do algoritmo, fazendo com que mais vértices fiquem sem cor. Recomenda-se a utilização desse parâmetro como False.

## Modo de usar
O arquivo é chamado na linha de comando e possui quatro parâmetros possíveis:
- [--file]: argumento obrigatório onde deve-se passar o caminho para o arquivo .xlsx com os dados da instituição;
- [--aulas-sequenciais]: argumento opicional que aceita [S/N]. 'S' para priorizar aulas sequencias e 'N' para o oposto.
- [--gerar-horarios-turmas]: argumento opicional para gerar um arquivo .xlsx com os horários das turmas. Deve se passar como valor o nome que o arquivo gerado terá. É recomendado a opção 'N', já que oferece melhores resultados.
- [--gerar-horarios-professores]: argumento opicional para gerar um arquivo .xlsx com os horários das professores. Deve se passar como valor o nome que o arquivo gerado terá.

Exemplo de chamada:

    python HorarioDeAula.py --file instancias/Escola_A.xlsx --gerar-horarios-turmas resultados/Horarios_Por_Turma_Escola_A.xlsx

Nesse exemplo será lido o arquivo 'instancias/Escola_A.xlsx' e uma planilha com os horarios da turma será salva em 'resultados/Horarios_Por_Turma_Escola_A.xlsx'.

Além disso, sempre será impresso na tela o nome da escola, a quantidade de cores utilizadas, a quantidade de vértices não coloridos, a proporção de preferências atendidas em relação ao total de preferências apresentas e o tempo de execução do algoritmo.