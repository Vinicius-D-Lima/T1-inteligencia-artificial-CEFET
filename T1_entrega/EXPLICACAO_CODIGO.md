# Explicação detalhada do código — Trabalho 1 (GCC1734)

Este documento explica, praticamente linha por linha, tudo o que foi
implementado nos três arquivos entregues (`search.py`, `searchAgents.py`,
`deliveryrobot.py`). A ideia é te dar material suficiente para ler o
código na tela e explicar cada trecho no vídeo, sem precisar decorar
nada. Os números de linha citados são os dos arquivos **desta pasta**
(`T1_entrega/`).

Sumário:
- [1. Estrutura de nó de busca usada em todo o trabalho](#1-estrutura-de-nó-de-busca-usada-em-todo-o-trabalho)
- [2. search.py — Q1 (DFS), Q2 (BFS), Q3 (A*)](#2-searchpy)
- [3. searchAgents.py — Q4 (CornersProblem)](#3-q4-cornersproblem)
- [4. searchAgents.py — Q5 (cornersHeuristic)](#4-q5-cornersheuristic)
- [5. searchAgents.py — Q6 (foodHeuristic)](#5-q6-foodheuristic)
- [6. searchAgents.py — Q7 (AnyFoodSearchProblem + findPathToClosestDot)](#6-q7-anyfoodsearchproblem--findpathtoclosestdot)
- [7. deliveryrobot.py — Q8 (problema de busca do robô)](#7-deliveryrobotpy--q8)
- [8. Como cada questão se relaciona com o pseudocódigo GRAPH_SEARCH do PDF](#8-relação-com-o-graph_search-do-pdf)

---

## 1. Estrutura de nó de busca usada em todo o trabalho

Antes de implementar os algoritmos, foram criadas três funções auxiliares
no topo de `search.py` (linhas 23–44). Elas existem porque DFS, BFS e A*
compartilham a mesma "forma" de nó de busca — o próprio PDF sugere isso
na dica da Q1 ("os algoritmos... compartilham grande parte de sua
estrutura"). Em vez de reescrever a lógica de nó três vezes, ela foi
escrita uma vez só e reaproveitada.

Um **nó de busca** aqui é representado como um dicionário Python com
quatro chaves possíveis:
- `'STATE'`: o estado do problema (pode ser uma posição `(x,y)`, uma
  tupla mais complexa, etc. — o código dos algoritmos nunca olha para
  dentro do estado, só compara com `==`/`in set`).
- `'PATH-COST'`: o custo acumulado do caminho desde o início até este nó.
- `'ACTION'`: a ação que levou do nó pai até este nó (não existe no nó
  raiz).
- `'PARENT'`: referência ao nó pai (não existe no nó raiz).

### `getStartNode(problem)` — linhas 23–25
```python
def getStartNode(problem):
    """Create the initial search node for a problem."""
    return {'STATE': problem.getStartState(), 'PATH-COST': 0}
```
Cria o nó raiz da árvore de busca: o estado inicial do problema
(`problem.getStartState()`), com custo de caminho zero. Note que esse
nó **não tem** `'ACTION'` nem `'PARENT'` — isso é usado depois como
"sentinela" para saber quando parar de reconstruir o caminho.

### `getChildNode(successor, parent_node)` — linhas 28–35
```python
def getChildNode(successor, parent_node):
    """Create a child node from a successor triple and its parent node."""
    return {
        'STATE': successor[0],
        'ACTION': successor[1],
        'PARENT': parent_node,
        'PATH-COST': parent_node['PATH-COST'] + successor[2],
    }
```
Todo `problem.expand(state)` (definido em `search.py`, contrato da
classe `SearchProblem`) devolve uma lista de **triplas**
`(child_state, action, stepCost)` — é exatamente isso que `successor`
representa aqui: `successor[0]` é o estado filho, `successor[1]` é a
ação, `successor[2]` é o custo daquele passo. Essa função pega uma
dessas triplas e o nó pai, e monta o nó filho: guarda o estado, a ação
que foi tomada, o ponteiro para o pai (para reconstruir o caminho depois)
e o custo acumulado (custo do pai + custo do passo).

### `getActionSequence(node)` — linhas 38–44
```python
def getActionSequence(node):
    """Return the action sequence from the start node to the given node."""
    actions = []
    while node['PATH-COST'] > 0:
        actions.insert(0, node['ACTION'])
        node = node['PARENT']
    return actions
```
Quando um algoritmo de busca encontra o objetivo, ele tem na mão o nó
objetivo, mas precisa devolver a **lista de ações** do início até ali
(é isso que `SearchAgent` espera, conforme o glossário do PDF). Essa
função "sobe" a cadeia de pais (`node = node['PARENT']`) recolhendo a
ação de cada nó, sempre inserindo no início da lista (`insert(0, ...)`)
para que a ordem final fique do começo para o fim. A condição de parada
`node['PATH-COST'] > 0` funciona porque o único nó com custo de caminho
zero é a raiz (todas as ações no Pacman/labirinto têm custo positivo);
ao chegar nela, o laço para.

Essas três funções são usadas por **todos** os algoritmos de busca a
seguir. Elas não fazem parte do contrato de `SearchProblem` — são só uma
conveniência interna de implementação.

---

## 2. search.py

### 2.1 Q1 — `depthFirstSearch` (linhas 127–164, código novo em 140–164)

```python
node = getStartNode(problem)
frontier = util.Stack()
frontier.push(node)

closed = set()

while not frontier.isEmpty():
    node = frontier.pop()

    if node['STATE'] in closed:
        continue

    closed.add(node['STATE'])

    if problem.isGoalState(node['STATE']):
        return getActionSequence(node)

    for successor in problem.expand(node['STATE']):
        child_node = getChildNode(successor, node)

        if child_node['STATE'] not in closed:
            frontier.push(child_node)

return []
```

Linha a linha:
1. `node = getStartNode(problem)` — cria o nó raiz.
2. `frontier = util.Stack()` — a **fronteira** (conjunto de nós ainda não
   explorados) é uma **pilha** (LIFO). É isso que faz o algoritmo ser DFS
   e não BFS: o último nó empilhado é o primeiro a ser desempilhado, ou
   seja, a busca sempre "mergulha" no filho mais recente antes de voltar
   para explorar outro ramo.
3. `frontier.push(node)` — coloca a raiz na fronteira.
4. `closed = set()` — conjunto de estados **já expandidos** (busca em
   grafo). É isso que impede o algoritmo de reexpandir um estado e cair
   em loop infinito em labirintos com ciclos.
5. `while not frontier.isEmpty():` — repete enquanto houver nós para
   explorar.
6. `node = frontier.pop()` — tira o nó do topo da pilha.
7. `if node['STATE'] in closed: continue` — se esse estado já foi
   expandido antes (pode ter entrado na pilha duas vezes por caminhos
   diferentes), ele é descartado sem ser processado de novo.
8. `closed.add(node['STATE'])` — marca o estado como expandido **no
   momento em que sai da fronteira** (não quando entra) — esse é o ponto
   que corresponde exatamente à linha `if node not in expanded: expanded.add(node)`
   do pseudocódigo `GRAPH_SEARCH` do PDF.
9. `if problem.isGoalState(node['STATE']): return getActionSequence(node)`
   — teste de objetivo. Só é feito depois de tirar o nó da fronteira,
   igual ao pseudocódigo do PDF.
10. `for successor in problem.expand(node['STATE']):` — gera todos os
    filhos do estado atual (cada `successor` é a tripla
    `(child, action, stepCost)` explicada acima).
11. `child_node = getChildNode(successor, node)` — monta o nó filho.
12. `if child_node['STATE'] not in closed: frontier.push(child_node)` —
    só empilha o filho se o estado dele ainda não foi expandido (evita
    inchar a pilha com estados que sabemos que não vão ser reprocessados,
    embora o `if node['STATE'] in closed: continue` do passo 7 já garanta
    a correção mesmo sem esse filtro — ele é só uma otimização de
    memória).
13. `return []` — se a fronteira esvaziar sem achar o objetivo, não há
    solução (não deveria acontecer nos mapas do trabalho, mas é o
    comportamento correto de uma busca completa).

**Por que a DFS não garante solução ótima?** Porque ela escolhe sempre
aprofundar no filho mais recentemente descoberto, sem nenhuma noção de
"distância percorrida até aqui". Ela pode (e geralmente vai) encontrar o
objetivo por um caminho bem mais longo do que o necessário, só porque
esse caminho foi o primeiro a ser explorado até o fim. É por isso que o
PDF pede para comparar o comprimento 130 (ou 246, dependendo da ordem dos
sucessores) da solução do DFS no `mediumMaze` com o caminho realmente
mais curto (que a BFS encontra, mais curto).

**Por que o Pacman não passa por todos os estados expandidos?** Porque
"expandir" um estado (gerar seus filhos) é diferente de "estar no
caminho final até o objetivo". Muitos estados são expandidos porque a
DFS mergulhou em um ramo sem saída (um corredor que não leva à comida) e
depois teve que voltar (backtrack); esses estados aparecem na lista de
expandidos (pintados no mapa), mas não fazem parte da sequência de ações
finalmente devolvida por `getActionSequence`.

### 2.2 Q2 — `breadthFirstSearch` (linhas 166–192, código novo em 169–192)

O código é **idêntico** ao da DFS, com uma única mudança:
```python
frontier = util.Queue()
```
em vez de `util.Stack()`. Trocar a pilha por uma fila (FIFO) já é
suficiente para transformar DFS em BFS: agora o nó mais **antigo** da
fronteira é o próximo a ser expandido, então a busca explora a árvore
"camada por camada" (todos os nós a distância 1 do início, depois todos
a distância 2, etc.), em vez de mergulhar fundo em um só ramo.

Isso confirma exatamente a dica do enunciado ("Eles diferem
principalmente pela política usada para selecionar nós da borda"): a
única diferença de verdade entre DFS e BFS aqui é o tipo da estrutura de
dados da fronteira.

**Por que a BFS garante solução ótima quando todas as ações têm o mesmo
custo?** Porque a BFS expande os nós em ordem crescente de **profundidade**
(número de passos desde a raiz). Como cada passo custa o mesmo (custo 1),
profundidade e custo de caminho são a mesma coisa multiplicada por uma
constante. Logo, o primeiro nó objetivo que a BFS encontra é, por
construção, o que está à menor profundidade — ou seja, o de menor custo.
(Isso deixa de valer se as ações tiverem custos diferentes: aí seria
preciso usar busca de custo uniforme/A*, não BFS.)

### 2.3 Q3 — `aStarSearch` (linhas 201–238, código novo em 204–238)

```python
node = getStartNode(problem)
fn_total_cost_for_node = lambda a_node: a_node['PATH-COST'] + heuristic(a_node['STATE'], problem=problem)

frontier = util.PriorityQueueWithFunction(fn_total_cost_for_node)
frontier.push(node)

explored = set()
best_path_cost_by_state = {node['STATE']: node['PATH-COST']}

while not frontier.isEmpty():
    node = frontier.pop()

    if node['STATE'] in explored:
        continue

    explored.add(node['STATE'])

    if problem.isGoalState(node['STATE']):
        return getActionSequence(node)

    successors = problem.expand(node['STATE'])

    for successor in successors:
        child_node = getChildNode(successor, node)
        child_state = child_node['STATE']
        child_path_cost = child_node['PATH-COST']

        if child_state in explored:
            continue

        if child_path_cost < best_path_cost_by_state.get(child_state, float('inf')):
            best_path_cost_by_state[child_state] = child_path_cost
            frontier.push(child_node)

return []
```

Linha a linha (só o que muda de verdade em relação à BFS/DFS):
1. `fn_total_cost_for_node = lambda a_node: a_node['PATH-COST'] + heuristic(a_node['STATE'], problem=problem)`
   — esta é a função de prioridade **f(n) = g(n) + h(n)**:
   - `a_node['PATH-COST']` é `g(n)`, o custo real já percorrido até o nó.
   - `heuristic(a_node['STATE'], problem=problem)` é `h(n)`, a estimativa
     de custo restante até o objetivo (a heurística é passada como
     parâmetro da função `aStarSearch`, com `nullHeuristic` — que sempre
     devolve 0 — como padrão; quando `h(n) = 0` sempre, A* vira busca de
     custo uniforme, exatamente como o PDF observa na Q6).
   - A soma das duas é `f(n)`, a prioridade usada para decidir qual nó
     explorar primeiro.
2. `frontier = util.PriorityQueueWithFunction(fn_total_cost_for_node)` —
   a fronteira agora é uma **fila de prioridade**: o próximo nó
   desenfileirado é sempre o de menor `f(n)` entre todos os que estão na
   fronteira.
3. `explored = set()` e `best_path_cost_by_state = {...}` — além do
   conjunto de estados já expandidos (igual à BFS/DFS), é mantido um
   dicionário com o **melhor `g(n)` conhecido até agora** para cada
   estado. Isso é necessário porque, diferente de BFS/DFS, em A* pode
   valer a pena colocar o mesmo estado na fronteira mais de uma vez, se
   for descoberto um caminho mais barato até ele depois.
4. No laço interno, ao gerar um filho:
   - `if child_state in explored: continue` — se o estado já foi
     definitivamente expandido, ignora (ele já tem o menor `g` possível,
     porque a heurística é consistente — ver Q5/Q6).
   - `if child_path_cost < best_path_cost_by_state.get(child_state, float('inf')):`
     — só re-enfileira o filho se o caminho atual até ele for **melhor**
     do que qualquer caminho até esse mesmo estado já visto antes. Isso é
     o tratamento de estados repetidos pedido explicitamente no
     enunciado da Q3: em vez de simplesmente ignorar um estado repetido
     (o que poderia jogar fora um caminho mais barato), o algoritmo
     compara os custos e só descarta o pior.
5. O resto (teste de objetivo ao desenfileirar, reconstrução do caminho
   com `getActionSequence`) é igual aos outros dois algoritmos.

---

## 3. Q4 — `CornersProblem`

Arquivo `searchAgents.py`.

### Representação de estado escolhida

O enunciado pede um estado da forma `((x, y), ____)` (dica 3 da Q4) e
proíbe usar o `GameState` completo como estado de busca (porque ele
carrega informação irrelevante ao problema — posição dos fantasmas,
comida fora dos cantos, pontuação, etc. — o que deixaria o espaço de
estados gigantesco e a busca lentíssima e, pior, tecnicamente incorreta,
já que dois `GameState` quase idênticos mas com um fantasma em posição
diferente seriam tratados como estados diferentes, quando na prática só
importa "onde o Pacman está e quais cantos ele já visitou").

Foi escolhido:
```python
(posição_do_pacman, frozenset_dos_cantos_já_visitados)
```
Um `frozenset` (conjunto imutável) foi usado em vez de, por exemplo, uma
tupla de 4 booleanos, porque:
- É **hashable** (pode ser chave de `set`/`dict`, necessário porque os
  algoritmos de busca guardam estados em `set()` para controlar
  expansão).
- A ordem dos cantos dentro dele não importa (visitar canto A depois B é
  o mesmo estado que visitar B depois A), o que é naturalmente
  representado por um conjunto.

### `__init__` (linhas 296–310) — nada foi adicionado aqui

O construtor já vinha pronto no arquivo original (calcula
`self.walls`, `self.startingPosition` e `self.corners`, que são os
**únicos dados do `GameState` que o problema realmente precisa**, exatamente
como a Dica 1 do PDF descreve). Não foi necessário guardar mais nada
aqui porque o estado (posição + cantos visitados) é construído sob
demanda em `getStartState`/`getNextState`.

### `getStartState` (linhas 312–321, código novo em 318–321)
```python
visitedCorners = frozenset(
    corner for corner in self.corners if corner == self.startingPosition
)
return (self.startingPosition, visitedCorners)
```
O estado inicial é a posição inicial do Pacman, com o conjunto de cantos
visitados **vazio** — a não ser que, por coincidência, o Pacman já comece
exatamente em cima de um canto, caso em que esse canto já entra marcado
como visitado desde o início. Isso evita um bug sutil: se o Pacman
nascesse em um canto e o código sempre começasse com conjunto vazio, ele
precisaria "revisitar" um canto em que já está, o que nem é uma ação
possível de um jeito natural.

### `isGoalState` (linhas 323–329, código novo em 328–329)
```python
_, visitedCorners = state
return len(visitedCorners) == len(self.corners)
```
O objetivo é alcançado quando o número de cantos já visitados é igual ao
número total de cantos (4). Não importa a posição atual do Pacman nem a
ordem em que os cantos foram visitados — só que os quatro já tenham sido
tocados em algum momento do caminho.

### `expand` (linhas 331–352, código novo em 347–349)
```python
nextState = self.getNextState(state, action)
cost = self.getActionCost(state, action, nextState)
children.append((nextState, action, cost))
```
Segue exatamente o contrato pedido: para cada ação legal (calculada por
`getActions`, já pronta no arquivo original, que olha só para
`state[0]`, a posição), calcula o próximo estado e o custo do passo, e
monta a tripla `(nextState, action, cost)` — o mesmo formato usado em
`search.py`.

### `getNextState` (linhas 370–382, código novo em 377–382)
```python
nextPosition = (nextx, nexty)
visitedCorners = state[1]
if nextPosition in self.corners and nextPosition not in visitedCorners:
    visitedCorners = visitedCorners | frozenset([nextPosition])
return (nextPosition, visitedCorners)
```
`nextx, nexty` já tinham sido calculados no código original (posição
resultante de aplicar a ação de movimento). O que foi adicionado:
- Se a nova posição é um dos 4 cantos **e** ele ainda não estava no
  conjunto de visitados, cria um **novo** `frozenset` (união do antigo
  com o canto novo — lembrando que `frozenset` é imutável, não dá pra
  fazer `.add()` nele, por isso o operador `|` de união que cria um novo
  conjunto).
- Se a posição não é canto, ou já era um canto visitado, o conjunto de
  visitados simplesmente se mantém o mesmo.
- Retorna o novo estado `(nextPosition, visitedCorners)`.

`getActionCost` e `getCostOfActionSequence` não precisaram de mudanças —
já vinham prontos, sempre custo 1 por passo.

---

## 4. Q5 — `cornersHeuristic`

Arquivo `searchAgents.py`, linhas 398–428 (código novo em 415–428).

```python
position, visitedCorners = state
remainingCorners = [corner for corner in corners if corner not in visitedCorners]

total = 0
current = position
while remainingCorners:
    nearestDist, nearestCorner = min(
        (util.manhattanDistance(current, corner), corner) for corner in remainingCorners
    )
    total += nearestDist
    current = nearestCorner
    remainingCorners.remove(nearestCorner)

return total
```

**Ideia**: uma heurística "gulosa do vizinho mais próximo". A partir da
posição atual, soma a distância Manhattan até o canto restante mais
próximo, finge que o Pacman foi até lá, e repete até não sobrar canto
nenhum. A soma dessas distâncias é o valor devolvido.

Linha a linha:
1. `position, visitedCorners = state` — desempacota o estado (a mesma
   representação escolhida na Q4).
2. `remainingCorners = [...]` — lista dos cantos que **ainda não** foram
   visitados nesse estado (os que faltam para o objetivo).
3. `total = 0`, `current = position` — acumulador da estimativa de custo
   e "posição hipotética" indo de canto em canto.
4. O laço `while remainingCorners:` repete até visitar (hipoteticamente)
   todos os cantos restantes:
   - `min((util.manhattanDistance(current, corner), corner) for corner in remainingCorners)`
     — calcula a distância Manhattan de `current` até cada canto
     restante e pega o par `(distância, canto)` de menor distância
     (`util.manhattanDistance` já existe pronta em `util.py`).
   - `total += nearestDist` — soma essa distância ao total.
   - `current = nearestCorner` — "anda" até esse canto (só na
     simulação da heurística, não no jogo de verdade).
   - `remainingCorners.remove(nearestCorner)` — remove o canto já
     contabilizado.
5. `return total` — devolve a soma.

**Por que é admissível?** Uma heurística é admissível se nunca
superestima o custo real restante. A distância Manhattan entre dois
pontos é sempre **menor ou igual** à distância real no labirinto (porque
o labirinto tem paredes que só podem alongar o caminho, nunca encurtá-lo
em relação à linha reta "em L"). Como a heurística soma distâncias
Manhattan (nunca maiores que as distâncias reais) ao longo de uma
sequência específica de cantos, e o custo real de visitar todos os
cantos em qualquer ordem é pelo menos a soma das distâncias reais entre
cantos consecutivos nessa mesma ordem gulosa, a heurística nunca
ultrapassa o custo real. (Na pior das hipóteses ela é apenas menos
precisa por escolher uma ordem "gulosa" que pode não ser a ordem ótima
verdadeira — mas nunca superestima.)

**Por que é consistente?** Porque satisfaz `h(n) ≤ c(n, n') + h(n')`
para qualquer sucessor `n'`. Isso decorre diretamente da desigualdade
triangular da distância Manhattan: mover-se um passo (`c(n,n') = 1`)
muda a posição do Pacman em no máximo 1 de distância Manhattan, então a
estimativa gulosa não pode cair mais que 1 de um estado para o seu
sucessor. Como a heurística é construída inteiramente a partir de somas
de distâncias Manhattan — que respeitam a desigualdade triangular — a
soma inteira também respeita.

**Evidência empírica**: o mediumCorners com essa heurística expandiu
**692 nós** (testado e reportado no terminal), bem abaixo do limite de
1.200 nós que dá a pontuação máxima de eficiência na rubrica da Q5.

---

## 5. Q6 — `foodHeuristic`

Arquivo `searchAgents.py`, linhas 514–563 (código novo em 545–563).

```python
def getMazeDistance(start, end):
    try:
        return problem.heuristicInfo[(start, end)]
    except KeyError:
        dist = mazeDistance(start, end, problem.startingGameState)
        problem.heuristicInfo[(start, end)] = dist
        return dist

foodList = foodGrid.asList()
if not foodList:
    return 0

distancesFromPacman = [getMazeDistance(position, food) for food in foodList]
foodPairDistances = [0]
for food in foodList:
    for otherFood in foodList:
        foodPairDistances.append(getMazeDistance(food, otherFood))

return min(distancesFromPacman) + max(foodPairDistances)
```

**Ideia**: em vez de distância Manhattan (que ignora paredes), aqui a
heurística usa **distância real de labirinto** (`mazeDistance`, função
já pronta no final do arquivo, que roda uma BFS internamente). O valor
devolvido é:

```
h(n) = distância da comida mais próxima do Pacman
     + maior distância entre duas comidas quaisquer (o "diâmetro" do conjunto de comida)
```

Linha a linha:
1. `getMazeDistance(start, end)` — função auxiliar interna que calcula a
   distância real (não Manhattan) entre dois pontos do labirinto,
   **cacheando** o resultado em `problem.heuristicInfo` (um dicionário
   que o próprio enunciado da Q6 sugere usar para não recalcular a
   mesma distância toda hora — calcular `mazeDistance` roda uma busca
   BFS inteira por trás, então é caro repetir).
   - `try/except KeyError` — tenta pegar do cache; se não estiver lá
     (`KeyError`), calcula com `mazeDistance(...)`, guarda no cache e
     devolve.
2. `foodList = foodGrid.asList()` — converte a grade de comida (`Grid`
   de booleanos) em uma lista de coordenadas `(x, y)` com comida.
3. `if not foodList: return 0` — se não sobrou comida nenhuma, o estado
   já é objetivo, então o custo restante estimado é 0 (requisito de toda
   heurística admissível: `h = 0` em estados objetivo).
4. `distancesFromPacman = [...]` — distância real do Pacman até **cada**
   comida restante.
5. `foodPairDistances = [0]` (começa com um 0 para o caso de só existir
   uma comida — nesse caso não há "par" de comidas e o diâmetro deve ser
   0) — depois, os dois `for` aninhados calculam a distância real entre
   **todo par** de comidas (incluindo uma comida com ela mesma, que dá
   distância 0 e não afeta o `max` no final).
6. `return min(distancesFromPacman) + max(foodPairDistances)` — soma a
   distância até a comida mais próxima com o "diâmetro" (maior distância
   entre duas comidas quaisquer).

**Por que é admissível?** Pense nas duas comidas mais distantes entre si
no labirinto, `f1` e `f2`, separadas pela distância real `D` (o
diâmetro). Qualquer solução válida precisa visitar as duas em algum
momento; entre visitar uma e visitar a outra, o Pacman precisa percorrer
pelo menos `D` de distância real (não existe atalho mais curto que a
distância real, por definição). Além disso, antes de visitar a
**primeira** comida do seu percurso, o Pacman já andou pelo menos a
distância até a comida mais próxima da posição atual (não existe comida
mais perto do que a mais próxima). Somando as duas parcelas obtemos uma
estimativa que nunca supera o custo real de terminar de coletar toda a
comida — logo é admissível.

**Por que é consistente?** `mazeDistance` é uma distância de caminho
mínimo em um grafo (o labirinto), então ela sempre respeita a
desigualdade triangular. A heurística é construída somando/comparando
apenas distâncias desse tipo, então a "queda" de `h(n)` para `h(n')` ao
longo de qualquer aresta do grafo de busca nunca é maior que o custo
daquela aresta (`c(n, n') = 1`), o que é exatamente a definição de
consistência.

**Evidência empírica**: `testSearch` deu custo total 7 (bate com o valor
de referência do PDF) e `trickySearch` expandiu **719 nós** em 0,3
segundos — muito abaixo do teto de 9.000 nós que dá pontuação máxima de
eficiência na Q6 (e do próprio UCS de referência do PDF, que levava 13s e
~16.000 nós).

---

## 6. Q7 — `AnyFoodSearchProblem` + `findPathToClosestDot`

Arquivo `searchAgents.py`.

### `AnyFoodSearchProblem.isGoalState` (linhas 622–630, código novo na 630)
```python
def isGoalState(self, state):
    x,y = state
    "*** YOUR CODE HERE ***"
    return self.food[x][y]
```
`AnyFoodSearchProblem` herda de `PositionSearchProblem`, então o estado é
simplesmente a posição `(x, y)` do Pacman (não precisa de nenhuma
representação nova). `self.food` é a grade de comida do estado inicial
(`Grid` de booleanos, guardada no `__init__` da classe, já pronto). O
objetivo é alcançado assim que o Pacman chega em **qualquer** posição
que tenha comida — daí `self.food[x][y]` (True se há comida ali, False
caso contrário) já ser exatamente o teste de objetivo certo.

### `findPathToClosestDot` (linhas 582–594, código novo na 594)
```python
def findPathToClosestDot(self, gameState):
    startPosition = gameState.getPacmanPosition()
    food = gameState.getFood()
    walls = gameState.getWalls()
    problem = AnyFoodSearchProblem(gameState)

    "*** YOUR CODE HERE ***"
    return search.bfs(problem)
```
O problema `AnyFoodSearchProblem(gameState)` já monta um problema de
busca cujo objetivo é "chegar em qualquer comida". Como todas as ações
têm custo 1 (herdado de `PositionSearchProblem`), a busca que garante o
caminho **mais curto** (em número de passos) até essa comida mais
próxima é a **BFS** — por isso a implementação é literalmente uma linha:
`return search.bfs(problem)`, reaproveitando o algoritmo já implementado
na Q2. Isso confirma a dica do enunciado ("a solução deve ser muito
curta!").

Importante: "pílula mais próxima" aqui significa a comida com **menor
distância de caminho no labirinto** (não Manhattan) — e é exatamente
isso que a BFS sobre o grafo real do labirinto calcula, diferente de
simplesmente escolher a comida com menor distância em linha reta.

**Por que o agente guloso (`ClosestDotSearchAgent`) nem sempre acha o
caminho mais curto global?** Porque a cada iteração ele resolve só o
subproblema "qual o caminho mais curto até a comida mais próxima **a
partir de onde estou agora**", sem nenhuma visão do resto do mapa. Uma
escolha gulosa localmente ótima pode obrigar o Pacman a "voltar" por um
corredor que ele já tinha percorrido para pegar uma comida que ficou
para trás, gerando um percurso total mais longo do que se ele tivesse
planejado a ordem de coleta de forma global (como faz o
`AStarFoodSearchAgent` da Q6, que otimiza o caminho completo de uma vez).
Um contraexemplo simples de desenhar no vídeo: um corredor reto com
comida nas duas pontas e o Pacman no meio, ligeiramente mais perto de um
lado — a estratégia gulosa vai primeiro no lado mais próximo e depois
percorre o corredor inteiro de volta para pegar a comida do outro lado,
enquanto o caminho ótimo (se o Pacman começasse virado para o lado mais
longe) percorreria o corredor uma vez só.

---

## 7. deliveryrobot.py — Q8

Este arquivo **não existia** no repositório original do trabalho (o PDF
menciona que ele seria fornecido, mas, no momento em que este trabalho
foi feito, o arquivo ainda não estava publicado). Ele foi criado do zero,
seguindo o padrão sugerido pela Dica da Q8: mesma estrutura de
`EightPuzzleState` / `EightPuzzleSearchProblem`, do arquivo
`eightpuzzle.py` (uma classe separada para o **estado** do problema, e
outra que implementa `search.SearchProblem` para o **problema de
busca**).

### Modelagem do problema (antes do código)

- **Locais**: A, B, C, D, E.
- **Conexões bidirecionais**: A–B, A–C, B–D, C–D, D–E.
- **Estação de recarga**: C.
- **Capacidade máxima de bateria**: 3 unidades.
- **Estado inicial**: robô em A, bateria = 2.
- **Objetivo**: robô em E (não importa a bateria restante).
- **Ações**: mover para um local diretamente conectado (custa 1 unidade
  de bateria, só é possível com bateria > 0), ou `RECARREGAR` (só em C,
  só se a bateria não está cheia, restaura para 3). Todas as ações têm
  custo unitário (1), inclusive `RECARREGAR`.

### `DeliveryRobotState` (linhas ~19–46)

```python
class DeliveryRobotState:
    def __init__(self, location, battery):
        self.location = location
        self.battery = battery

    def __eq__(self, other):
        return (
            isinstance(other, DeliveryRobotState)
            and self.location == other.location
            and self.battery == other.battery
        )

    def __hash__(self):
        return hash((self.location, self.battery))

    def __str__(self):
        return 'local=%s, bateria=%d' % (self.location, self.battery)
```

- `__init__`: guarda os dois dados que definem completamente um estado:
  **onde** o robô está e **quanta bateria** ele tem.
- `__eq__`: dois estados são iguais se, e somente se, têm o mesmo local
  **e** a mesma bateria. **Isso é o ponto central da questão** (e é
  exatamente o que o PDF pede para explicar no vídeo): se a igualdade
  considerasse só o local, o algoritmo trataria "robô em D com bateria 2"
  e "robô em D com bateria 0" como o **mesmo** estado — mas eles não são
  equivalentes, porque a partir de um o robô ainda pode se mover e do
  outro não pode mais (bateria 0 é um beco sem saída, a menos que D fosse
  estação de recarga, o que não é o caso). Colapsar os dois em um único
  estado faria a busca "esquecer" que um dos casos está preso, podendo
  gerar planos inválidos ou perder soluções válidas.
- `__hash__`: precisa ser consistente com `__eq__` (dois objetos iguais
  devem ter o mesmo hash) porque os algoritmos de busca guardam estados
  em `set()`/`dict` (nos conjuntos `closed`/`explored` de `search.py`).
  Usa `hash((location, battery))`, a forma padrão de gerar um hash a
  partir dos mesmos campos usados na igualdade.
- `__str__`: só para impressão legível nos testes (`local=D, bateria=2`).

### `DeliveryRobotSearchProblem` (linhas ~49 em diante)

```python
CONNECTIONS = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C', 'E'],
    'E': ['D'],
}
RECHARGE_STATION = 'C'
MAX_BATTERY = 3
RECHARGE_ACTION = 'RECARREGAR'
```
O grafo de locais é guardado como um dicionário de listas de adjacência
— já construído bidirecionalmente (por exemplo, `'A': ['B', 'C']` e
`'B': ['A', 'D']` juntos representam a aresta A–B nos dois sentidos).
As constantes `RECHARGE_STATION`, `MAX_BATTERY` e `RECHARGE_ACTION`
deixam essas "regras do mundo" nomeadas em vez de espalhadas como valores
soltos pelo código.

```python
def __init__(self, startLocation='A', startBattery=2, goalLocation='E'):
    self.startState = DeliveryRobotState(startLocation, startBattery)
    self.goalLocation = goalLocation
```
Os parâmetros já vêm com os valores padrão exigidos pelo enunciado
(começa em A com bateria 2, objetivo é E), mas continuam configuráveis
caso se queira testar outras variações do problema.

```python
def getStartState(self):
    return self.startState
```
Devolve o estado inicial — exigido pelo contrato de `search.SearchProblem`.

```python
def isGoalState(self, state):
    return state.location == self.goalLocation
```
O objetivo só depende do **local**, não da bateria — igual o enunciado
diz ("independentemente da carga restante").

```python
def getActions(self, state):
    actions = []
    if state.battery > 0:
        actions.extend(self.CONNECTIONS[state.location])
    if state.location == self.RECHARGE_STATION and state.battery < self.MAX_BATTERY:
        actions.append(self.RECHARGE_ACTION)
    return actions
```
Lista as ações **legais** a partir de um estado:
- Se há bateria (`battery > 0`), todos os locais vizinhos do local atual
  (`self.CONNECTIONS[state.location]`) viram ações possíveis (mover-se
  para lá).
- Se o robô está na estação de recarga **e** a bateria não está cheia,
  `RECARREGAR` também é uma ação possível.
- Note que, com bateria 0 fora da estação C, a lista fica **vazia** — o
  robô fica preso ali (não pode se mover nem recarregar), o que é
  exatamente a regra do enunciado.

```python
def getNextState(self, state, action):
    assert action in self.getActions(state), (
        "getNextState() chamado com uma acao invalida.")
    if action == self.RECHARGE_ACTION:
        return DeliveryRobotState(state.location, self.MAX_BATTERY)
    return DeliveryRobotState(action, state.battery - 1)
```
A **função de transição**:
- `assert` garante que a ação é de fato uma das legais para aquele
  estado (proteção contra uso incorreto).
- Se a ação é `RECARREGAR`, o novo estado fica no mesmo local, com
  bateria cheia (`MAX_BATTERY`).
- Senão, a ação **é o próprio nome do local de destino** (decisão de
  design: em vez de inventar nomes como `"IR_PARA_B"`, a ação de mover
  é identificada diretamente pelo local para onde o robô vai, o que
  deixa `getNextState` bem direto: `action` já é o novo local). O novo
  estado fica no local `action`, com a bateria decrementada em 1.

```python
def getActionCost(self, state, action, next_state):
    assert next_state == self.getNextState(state, action), (
        "getActionCost() chamado com um next_state invalido.")
    return 1
```
Custo unitário para **toda** ação, incluindo `RECARREGAR` — exatamente
como pedido no enunciado ("Considere custo unitário para todas as ações,
inclusive RECARREGAR").

```python
def expand(self, state):
    children = []
    for action in self.getActions(state):
        next_state = self.getNextState(state, action)
        children.append((next_state, action, self.getActionCost(state, action, next_state)))
    return children
```
Segue o mesmo contrato `(child, action, stepCost)` usado em todo o
trabalho: para cada ação legal, calcula o estado resultante e o custo, e
monta a tripla.

```python
def getCostOfActionSequence(self, actions):
    if actions is None:
        return 999999
    state = self.startState
    cost = 0
    for action in actions:
        if action not in self.getActions(state):
            return 999999
        state = self.getNextState(state, action)
        cost += 1
    return cost
```
Percorre uma sequência de ações a partir do estado inicial, validando a
cada passo se a ação é legal naquele ponto (se não for, retorna
`999999`, convenção usada em todo o projeto Pacman para "sequência
inválida"); se todas forem legais, soma 1 por ação (custo unitário) e
devolve o total.

### Bloco de teste (`if __name__ == '__main__':`)

No fim do arquivo, um pequeno script roda os três algoritmos de busca já
implementados (`breadthFirstSearch`, `depthFirstSearch`, `aStarSearch`)
sobre esse problema e imprime a sequência completa de estados e ações —
isso é o "código fornecido no fim do arquivo" que o PDF pede para usar
como evidência da Q8 (rodando `python deliveryrobot.py`).

Testado: os três algoritmos encontram a solução de **custo 4**
(`A -[C]-> C, RECARREGAR, C -[D]-> D, D -[E]-> E`), igual ao valor de
referência do PDF.

---

## 8. Relação com o GRAPH_SEARCH do PDF

O pseudocódigo do PDF (seção 5) é:
```
frontier = { startNode }
expanded = {}
while frontier is not empty:
    node = frontier.pop()
    if isGoal(node): return path_to_node
    if node not in expanded:
        expanded.add(node)
        for each child of node's children:
            frontier.push(child)
return failed
```

O código de `depthFirstSearch`/`breadthFirstSearch`/`aStarSearch`
implementa exatamente essa lógica, com duas pequenas diferenças
propositais (mesmo comportamento, só mais eficiente):
- O teste de objetivo é feito **depois** de marcar o nó como expandido
  (não muda o resultado, porque o teste de objetivo não depende de
  `expanded`).
- Em vez de só checar `if node not in expanded` antes de expandir, o
  código também filtra, ao empilhar/enfileirar um filho, se o estado
  dele já está em `expanded`/`closed` — isso evita colocar na fronteira
  nós que sabemos, de antemão, que serão descartados, economizando
  memória e tempo sem mudar o resultado final.

Isso é útil de mencionar no vídeo: os três algoritmos usam **a mesma
estrutura de laço**, e a única diferença entre eles é (a) o tipo de
fronteira (`Stack`, `Queue`, `PriorityQueueWithFunction`) e (b), no caso
do A*, o rastreamento extra de "melhor custo conhecido por estado" para
tratar corretamente estados repetidos com custos diferentes.
