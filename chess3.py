from matplotlib import pyplot as plt
from queue import Queue
import chess, random, _thread
import pandas as pd
import seaborn as sns

def outcome(board):
    if board.is_checkmate():
        if board.turn:
            return "Black"
        else:
            return "White"
    else:
        return "Draw"

#calc total moves
def moves(board):
    if board.turn:
        return board.fullmove_number * 2 - 1
    else:
        return board.fullmove_number * 2 - 2

def play(i):
    board = chess.Board()
    while not board.is_game_over():
        board.push(random.choice(list(board.legal_moves)))
    return i, outcome(board), moves(board)

def thread_wrapper(i, func, stat, q):
    def run():
        q.put(func)
        stat[i] = True
    return run

workers = 1000
status = [False for i in range(workers)]
q = Queue()
for i in range(workers):
    _thread.start_new_thread(thread_wrapper(i, play(i), status, q), tuple())

while not all(status):
    pass

results = []
while not q.empty():
    results.append(q.get())
results_df = pd.DataFrame(results, columns=['game_n', 'outcome', 'moves'])
#TODO process the results

results_df.to_csv('my_file.csv')

black = results_df.loc[results_df['outcome'] == 'Black']
white = results_df.loc[results_df['outcome'] == 'White']
draw = results_df.loc[results_df['outcome'] == 'Draw']
win = results_df.loc[results_df['outcome'] != 'Draw']

Total = len(results_df.index)
Wins = len(win.index)

PercentBlack = "Black Wins ≈ %s" %('{0:.2%}'.format(len(black.index)/Total))
PercentWhite = "White Wins ≈ %s" %('{0:.2%}'.format(len(white.index)/Total))
PercentDraw = "Draw ≈ %s" %('{0:.2%}'.format(len(draw.index)/Total))
AllTitle = 'Distribution of Moves by All Outcomes (nSample = %s)' %(workers)

sns.distplot(results_df.moves, hist=False, label = "All")
sns.distplot(black.moves, hist=False, label=PercentBlack)
sns.distplot(white.moves, hist=False, label=PercentWhite)
sns.distplot(draw.moves, hist=False, label=PercentDraw)
plt.title(AllTitle)
plt.ylabel('Density')
plt.xlabel('Number of Moves')
plt.legend()
plt.show()

results_df.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = "All")
draw.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = PercentDraw)
white.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = PercentWhite)
black.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = PercentBlack)
plt.title(AllTitle)
plt.ylabel('Frequency')
plt.xlabel('Number of Moves')
plt.legend()
plt.show()

ExpectedBlack = "EV Black Wins ≈ %s" %('{0:.2%}'.format(len(black.index)/Wins))
ExpectedWhite = "EV White Wins ≈ %s" %('{0:.2%}'.format(len(white.index)/Wins))
WinTitle = 'Distribution of Moves by Wins (nWins = %s)' %(Wins)

sns.distplot(win.moves, hist=False, label = "Wins")
sns.distplot(black.moves, hist=False, label=ExpectedBlack)
sns.distplot(white.moves, hist=False, label=ExpectedWhite)
sns.plt.title(WinTitle)
plt.ylabel('Density')
plt.xlabel('Number of Moves')
plt.legend()
plt.show()

win.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = "Wins")
white.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = ExpectedWhite)
black.moves.hist(alpha=0.4, bins=range(0, 700, 10), label = ExpectedBlack)
plt.title(WinTitle)
plt.ylabel('Frequency')
plt.xlabel('Number of Moves')
plt.legend()
plt.show()