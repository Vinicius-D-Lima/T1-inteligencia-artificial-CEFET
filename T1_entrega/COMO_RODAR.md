# Como rodar o Trabalho 1 (GCC1734) em outra máquina

Este guia explica como pegar os três arquivos desta pasta (`search.py`,
`searchAgents.py`, `deliveryrobot.py`), encaixá-los no projeto Pacman do
CS188/CEFET e rodar tanto o jogo quanto o autoavaliador, em qualquer
máquina (Linux, macOS, Windows ou um Codespace).

---

## 1. Requisitos

### 1.1 Python

- **Recomendado: Python 3.8 a 3.11.**
  O projeto original (`autograder.py`, `grading.py`) usa os módulos
  `imp` e `cgi` da biblioteca padrão. Eles foram removidos do Python:
  - `imp` → removido no **Python 3.12**
  - `cgi` → removido no **Python 3.13**

  Ou seja, **em Python 3.12 ou mais novo o `python autograder.py` quebra**
  com `ModuleNotFoundError: No module named 'imp'` (ou `cgi`). O jogo em
  si (`pacman.py`) roda normalmente em qualquer versão — o problema é só
  no autoavaliador.

- Se sua máquina só tem Python 3.12+ instalado (caso comum em instalações
  novas, incluindo GitHub Codespaces), veja a seção **5. Rodando o
  autograder em Python 3.12+** para um contorno rápido, sem precisar
  instalar outra versão do Python.

- Verifique sua versão com:
  ```bash
  python3 --version
  ```

### 1.2 Tkinter (opcional — só para gráficos em janela)

O jogo desenha uma janela gráfica usando `tkinter`. Isso exige:
1. O pacote `tkinter` instalado no Python (em Ubuntu/Debian:
   `sudo apt-get install python3-tk`).
2. Um **display gráfico** disponível (variável de ambiente `DISPLAY`).

Se você estiver em um ambiente **sem display** (ex.: GitHub Codespaces,
um servidor SSH, um container Docker "puro"), a janela gráfica não vai
abrir e o programa vai travar com o erro:
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```
Nesse caso, use os modos sem gráfico descritos na seção 3 (`-t` ou `-q`).
Isso **não afeta a nota** — o autoavaliador e os resultados de busca são
idênticos com ou sem gráficos.

### 1.3 Nenhuma biblioteca externa é necessária

Todo o projeto usa apenas a biblioteca padrão do Python. Não há
`requirements.txt` nem pacotes de terceiros para instalar.

---

## 2. Onde colocar os arquivos

Os três arquivos desta pasta são **substitutos** dos arquivos originais
(que vêm com stubs vazios / `"*** YOUR CODE HERE ***"`) do repositório
do trabalho:

```
https://github.com/AILAB-CEFET-RJ/gcc1734/
```

Passo a passo:

```bash
# 1. Clone o repositório do trabalho (se ainda não tiver)
git clone https://github.com/AILAB-CEFET-RJ/gcc1734.git
cd gcc1734/src/base/search

# 2. Copie os três arquivos desta pasta para cá, sobrescrevendo
#    search.py e searchAgents.py, e criando deliveryrobot.py
cp /caminho/para/T1_entrega/search.py .
cp /caminho/para/T1_entrega/searchAgents.py .
cp /caminho/para/T1_entrega/deliveryrobot.py .
```

A pasta `src/base/search` do repositório já contém todos os outros
arquivos necessários (`pacman.py`, `game.py`, `util.py`, `layout.py`,
`layouts/`, `test_cases/`, `autograder.py` etc.) — **não é preciso**
copiar mais nada, só esses três.

---

## 3. Rodando o jogo (pacman.py)

Sempre execute os comandos de dentro de `gcc1734/src/base/search`.

### 3.1 Com janela gráfica (precisa de tkinter + display)
```bash
python pacman.py
```

### 3.2 Sem janela gráfica — modo texto (recomendado em servidores/Codespaces)
Mostra o labirinto em ASCII no próprio terminal:
```bash
python pacman.py -t -p SearchAgent
```

### 3.3 Sem nenhum desenho — modo silencioso (mais rápido, só mostra o resultado)
```bash
python pacman.py -q -p SearchAgent
```

### 3.4 Exemplos usados na correção deste trabalho

```bash
# Q1 - DFS
python pacman.py -l tinyMaze   -p SearchAgent -q
python pacman.py -l mediumMaze -p SearchAgent -q
python pacman.py -l bigMaze -z .5 -p SearchAgent -q

# Q2 - BFS
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs -q
python pacman.py -l bigMaze    -p SearchAgent -a fn=bfs -z .5 -q
python eightpuzzle.py

# Q3 - A*
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic -q
python pacman.py -l openMaze -p SearchAgent -a fn=bfs -q
python pacman.py -l openMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic -q

# Q4 - CornersProblem
python pacman.py -l tinyCorners   -p SearchAgent -a fn=bfs,prob=CornersProblem -q
python pacman.py -l mediumCorners -p SearchAgent -a fn=bfs,prob=CornersProblem -q

# Q5 - cornersHeuristic (A*)
python pacman.py -l mediumCorners -p AStarCornersAgent -z 0.5 -q

# Q6 - foodHeuristic (A*)
python pacman.py -l testSearch    -p AStarFoodSearchAgent -q
python pacman.py -l trickySearch  -p AStarFoodSearchAgent -q

# Q7 - ClosestDotSearchAgent
python pacman.py -l bigSearch -p ClosestDotSearchAgent -z .5 -q
```

Retire o `-q` (ou troque por `-t`) se quiser ver a execução passo a
passo. Todos os comandos também estão em `commands.txt`, dentro da
mesma pasta do projeto.

### 3.5 Rodando a Q8 (deliveryrobot.py)

Esse arquivo não depende do Pacman — é um problema de busca isolado.
Basta rodar diretamente:
```bash
python deliveryrobot.py
```
Isso imprime o estado inicial e a solução encontrada por BFS, DFS e A*,
mostrando a sequência completa de estados e ações.

---

## 4. Rodando o autoavaliador (autograder.py)

Com um Python 3.8–3.11:
```bash
python autograder.py            # roda todas as questões
python autograder.py -q q1      # roda só a questão 1
python autograder.py -q q2
python autograder.py -q q3
python autograder.py -q q4
python autograder.py -q q5
python autograder.py -q q6
python autograder.py -q q7
```
(Não existe `-q q8`: a Q8, do robô de entrega, não tem autoavaliador —
veja a seção 3.5.)

---

## 5. Rodando o autograder em Python 3.12+ (contorno)

Se sua máquina só tem Python 3.12 ou mais novo (não é possível instalar
uma versão mais antiga), o autograder falha porque os módulos `imp` e/ou
`cgi` foram removidos da biblioteca padrão. Isso **não é um problema no
código do trabalho**, é uma incompatibilidade do script antigo do
autoavaliador com Python novo.

Contorno: criar um "shim" (substituto mínimo) do módulo que falta e
apontar o Python para ele via `PYTHONPATH`, sem alterar nenhum arquivo
do projeto.

1. **Python 3.12 e 3.13**: falta só `imp`. Crie um arquivo `imp.py`
   numa pasta separada (ex.: `~/pyshim/imp.py`) com este conteúdo:

   ```python
   import sys
   import types

   PY_SOURCE = 1

   def new_module(name):
       return types.ModuleType(name)

   def load_module(name, file, pathname, description):
       source = file.read()
       module = types.ModuleType(name)
       module.__file__ = pathname
       sys.modules[name] = module
       exec(compile(source, pathname, 'exec'), module.__dict__)
       return module
   ```

   E rode:
   ```bash
   PYTHONPATH=~/pyshim python3.12 autograder.py -q q1
   ```

2. **Python 3.13+**: além do `imp`, também falta `cgi` (usado só para um
   `import`, nunca chamado de fato). Crie também um `cgi.py` vazio na
   mesma pasta:
   ```python
   # cgi.py vazio, só para satisfazer o "import cgi" do grading.py
   ```
   E rode da mesma forma:
   ```bash
   PYTHONPATH=~/pyshim python3.13 autograder.py -q q1
   ```

Esse shim é só uma muleta para testar localmente; **não faz parte da
entrega** e não deve ser copiado para a pasta `src/base/search` do
projeto nem para o zip final.

---

## 6. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `_tkinter.TclError: no display name and no $DISPLAY environment variable` | Sem display gráfico disponível (Codespaces, SSH, container) | Use `-t` (texto) ou `-q` (silencioso) |
| `ModuleNotFoundError: No module named 'imp'` ao rodar `autograder.py` | Python 3.12+ | Veja a seção 5, ou use Python ≤ 3.11 |
| `ModuleNotFoundError: No module named 'cgi'` ao rodar `autograder.py` | Python 3.13+ | Veja a seção 5, ou use Python ≤ 3.11 |
| `AttributeError: ... is not a search function in search.py` | Você não copiou o `search.py` desta pasta para dentro de `src/base/search` | Repita o passo 2 |
| `Warning: this does not look like a regular search maze` | Mensagem normal do `PositionSearchProblem` quando o layout não tem exatamente 1 comida | Pode ignorar; não é erro |

---

## 7. Estrutura esperada da pasta do projeto após copiar os arquivos

```
gcc1734/src/base/search/
├── autograder.py          (original, não editado)
├── deliveryrobot.py        <-- desta pasta (Q8, arquivo novo)
├── eightpuzzle.py         (original, não editado)
├── game.py                (original, não editado)
├── layouts/                (original)
├── pacman.py               (original, não editado)
├── search.py                <-- desta pasta (Q1, Q2, Q3)
├── searchAgents.py          <-- desta pasta (Q4, Q5, Q6, Q7)
├── test_cases/              (original)
├── util.py                 (original, não editado)
└── ... (demais arquivos originais)
```
