from queue import Queue
import chess, random, _thread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

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

workers = 500000
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

PercentBlack = "Black Wins ≈ %s" % ('{0:.2%}'.format(len(black.index)/Total))
PercentWhite = "White Wins ≈ %s" % ('{0:.2%}'.format(len(white.index)/Total))
PercentDraw = "Draw ≈ %s" % ('{0:.2%}'.format(len(draw.index)/Total))
AllTitle = 'Distribution of Moves by All Outcomes (nSample = %s)' % workers

a = draw.moves
b = black.moves
c = white.moves

kdea = scipy.stats.gaussian_kde(a)
kdeb = scipy.stats.gaussian_kde(b)
kdec = scipy.stats.gaussian_kde(c)

grid = np.arange(700)

#weighted kde curves
wa = kdea(grid)*(len(a)/float(len(a)+len(b)+len(c)))
wb = kdeb(grid)*(len(b)/float(len(a)+len(b)+len(c)))
wc = kdec(grid)*(len(c)/float(len(a)+len(b)+len(c)))

total = wa+wb+wc
wtotal = wb+wc

plt.figure(figsize=(10,5))
plt.plot(grid, total, lw=2, label="Total")
plt.plot(grid, wa, lw=1, label=PercentDraw)
plt.plot(grid, wb, lw=1, label=PercentBlack)
plt.plot(grid, wc, lw=1, label=PercentWhite)
plt.title(AllTitle)
plt.ylabel('Density')
plt.xlabel('Number of Moves')
plt.legend()
plt.show()

ExpectedBlack = "EV Black Wins ≈ %s" % ('{0:.2%}'.format(len(black.index)/Wins))
ExpectedWhite = "EV White Wins ≈ %s" % ('{0:.2%}'.format(len(white.index)/Wins))
WinTitle = 'Distribution of Moves by Wins (nWins = %s)' % Wins

plt.figure(figsize=(10,5))
plt.plot(grid, wtotal, lw=2, label="Wins")
plt.plot(grid, wb, lw=1, label=ExpectedBlack)
plt.plot(grid, wc, lw=1, label=ExpectedWhite)
plt.title(WinTitle)
plt.ylabel('Density')
plt.xlabel('Number of Moves')
plt.legend()
plt.show()

print("Most frequent moves of All:", grid[total.argmax()], round(max(total), 4), "for", Total, "games")
print("Most frequent moves of Draws:", grid[wa.argmax()], round(max(wa), 4), "for", len(draw.index), "games")
print("Most frequent moves of Wins:", grid[wtotal.argmax()], round(max(wtotal), 4), "for", Wins, "games")
print("Most frequent moves of Black wins:", grid[wb.argmax()], round(max(wb), 4), "for", len(black.index), "games")
print("Most frequent moves of White wins:", grid[wc.argmax()], round(max(wc), 4), "for", len(white.index), "games")
