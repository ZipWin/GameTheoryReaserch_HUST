import numpy as np 
import matplotlib.pyplot as plt 
import argparse

GAME_TURNS = 1000   # 每次游戏包含的囚徒博弈次数
GENERATION_SIZE = 100   # 每代群体包含的参与者数
MUTATION_RATE = 0.05    # 基因突变概率

def get_payoff(choices):
    # 囚徒困境收益矩阵
    # 合作：0
    # 背叛：1
    PAYOFF = [
        [(3, 3), (0, 5)],
        [(5, 0), (1, 1)]
    ]    
    A_choice, B_choice = choices
    return PAYOFF[A_choice][B_choice]

class Player():
    def __init__(self, strategy=False):
        self.scores = 0
        if type(strategy) == bool:
             self.strategy = np.random.randint(0, 1, GAME_TURNS)
        else:
            self.strategy = strategy

def game(player1, player2):
    for i in range(GAME_TURNS):
        choices = (player1.strategy[i], player2.strategy[i])
        payoff1, payoff2 = get_payoff(choices)
        player1.scores += payoff1
        player2.scores += payoff2

def generate(player1, player2, number=GENERATION_SIZE):
    players = list(np.zeros(GENERATION_SIZE))
    for i in range(GENERATION_SIZE):
        cp = np.random.randint(0, GAME_TURNS)
        r = np.random.randint(0, 2)
        if r == 0:
            gene_part1 = player1.strategy[:cp]
            gene_part2 = player2.strategy[cp:]
        elif r == 1:
            gene_part1 = player2.strategy[:cp]
            gene_part2 = player1.strategy[cp:]
        strategy = np.concatenate((gene_part1, gene_part2), axis=0)
        for s in range(len(strategy)):
            r = np.random.rand()
            if r <= MUTATION_RATE:
                strategy[s] = 1 - strategy[s]
        players[i] = Player(strategy)

    return players

def main():
    parser = argparse.ArgumentParser(description='重复无记忆囚徒博弈')
    parser.add_argument('--generations', type=int, default=10, help='演化的代数，默认为10代')
    parser.add_argument('--save', action='store_true', default=False, help='是否保存每一代参与者数据，默认不保存')
    parser.add_argument('--plot-results', action='store_false', default=True, help='是否将结果可视化，默认为是')

    arg = parser.parse_args()
    generations = arg.generations

    players = list(np.zeros(generations))
    players[0] = list(np.zeros(GENERATION_SIZE))
    for i in range(len(players[0])):
        players[0][i] = Player()

    s = []
    for g in range(generations - 1):
        # Games
        for p1 in range(len(players[g])):
            for p2 in range(p1+1, len(players[g])):
                player1, player2 = players[g][p1], players[g][p2]
                game(player1, player2)
        
        # Find winners
        scores = list(np.zeros(len(players[g])))
        for p in range(len(players[g])):
            scores[p] = players[g][p].scores
        sorted_scores = sorted(scores)
        m1 = sorted_scores[-1]
        m2 = sorted_scores[-2]
        for i in range(len(scores)):
            if scores[i] == m1:
                m1_p = i
                break
        for i in range(len(scores)):
            if (scores[i] == m2) and (i != m1_p):
                m2_p = i
                break
        
        s.append(np.mean(scores))

        # Create next generation
        player1, player2 = players[g][m1_p], players[g][m2_p]
        players[g+1] = generate(player1, player2)
        
        print('Generation %i average score: %d, winners: %i, %i'
            %(g, np.mean(scores), m1_p, m2_p))

    if arg.save:
        np.save('players.npy', players)
        print('Players have been saved.')

    if arg.plot_results:
        MAX_SCORES = GAME_TURNS * GENERATION_SIZE * 3
        # plt.figure(figsize=(12, 8))
        plt.plot(range(len(s)), np.array(s)/MAX_SCORES)
        plt.xlabel('Generations', fontsize=16)
        plt.ylabel('Mean score rate', fontsize=16)
        plt.title('Mean score rate evolution', fontsize=16)
        # plt.savefig('得分率的进化.png')
        plt.show()

if __name__ == "__main__":
    main()