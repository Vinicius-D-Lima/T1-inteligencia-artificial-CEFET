# deliveryrobot.py
# -----------------
# Q8: formulacao e implementacao de um problema de busca para um robo de
# entrega que precisa levar um pacote ate um destino administrando o nivel
# de bateria, com uma unica estacao de recarga no caminho.
#
# Baseado na estrutura de EightPuzzleState / EightPuzzleSearchProblem
# (ver eightpuzzle.py).

import search


class DeliveryRobotState:
    """
    Representa um estado do problema do robo de entrega.

    Um estado precisa registrar tanto a localizacao do robo quanto o nivel
    atual de bateria: dois estados com a mesma localizacao mas niveis de
    bateria diferentes podem admitir conjuntos de acoes diferentes (por
    exemplo, um deles pode nao ter carga suficiente para se deslocar), logo
    nao podem ser tratados como o mesmo estado de busca.
    """

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

    def __repr__(self):
        return 'DeliveryRobotState(%r, %r)' % (self.location, self.battery)


class DeliveryRobotSearchProblem(search.SearchProblem):
    """
    Formalizacao do problema de busca do robo de entrega descrito no
    enunciado:

      - Locais: A, B, C, D e E;
      - Conexoes bidirecionais: A-B, A-C, B-D, C-D e D-E;
      - Estacao de recarga: C;
      - Capacidade maxima da bateria: 3 unidades;
      - Estado inicial: robo no local A, com 2 unidades de bateria;
      - Objetivo: chegar ao local E.

    Acoes:
      - Mover para um local diretamente conectado (nomeada com o proprio
        local de destino), que consome 1 unidade de bateria e so pode ser
        executada se houver carga disponivel;
      - RECARREGAR, disponivel apenas no local C, que restaura a bateria
        para a capacidade maxima e so e aplicavel quando a bateria nao
        esta cheia.

    Todas as acoes tem custo unitario.
    """

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

    def __init__(self, startLocation='A', startBattery=2, goalLocation='E'):
        self.startState = DeliveryRobotState(startLocation, startBattery)
        self.goalLocation = goalLocation

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        return state.location == self.goalLocation

    def getActions(self, state):
        actions = []
        if state.battery > 0:
            actions.extend(self.CONNECTIONS[state.location])
        if state.location == self.RECHARGE_STATION and state.battery < self.MAX_BATTERY:
            actions.append(self.RECHARGE_ACTION)
        return actions

    def getNextState(self, state, action):
        assert action in self.getActions(state), (
            "getNextState() chamado com uma acao invalida.")
        if action == self.RECHARGE_ACTION:
            return DeliveryRobotState(state.location, self.MAX_BATTERY)
        return DeliveryRobotState(action, state.battery - 1)

    def getActionCost(self, state, action, next_state):
        assert next_state == self.getNextState(state, action), (
            "getActionCost() chamado com um next_state invalido.")
        return 1

    def expand(self, state):
        """
        Returns list of (child, action, stepCost) triples, seguindo o mesmo
        contrato de search.SearchProblem.expand.
        """
        children = []
        for action in self.getActions(state):
            next_state = self.getNextState(state, action)
            children.append((next_state, action, self.getActionCost(state, action, next_state)))
        return children

    def getCostOfActionSequence(self, actions):
        """
        Returns the total cost of a particular sequence of actions. If those
        actions include an illegal move, return 999999.
        """
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


if __name__ == '__main__':
    problem = DeliveryRobotSearchProblem()

    print('Estado inicial:', problem.getStartState())
    print('Acoes aplicaveis no estado inicial:', problem.getActions(problem.getStartState()))

    for searchFunctionName in ('breadthFirstSearch', 'depthFirstSearch', 'aStarSearch'):
        searchFunction = getattr(search, searchFunctionName)
        actions = searchFunction(problem)
        cost = problem.getCostOfActionSequence(actions)
        print('\n%s encontrou %d acao(oes) com custo total %d:' % (searchFunctionName, len(actions), cost))

        state = problem.getStartState()
        print('  Estado inicial -> %s' % state)
        for action in actions:
            state = problem.getNextState(state, action)
            print('  Acao: %-12s -> %s' % (action, state))
