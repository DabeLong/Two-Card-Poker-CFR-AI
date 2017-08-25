import random

class Game():
    BET = '0'
    CALL = '1'
    CHECK = '2'
    FOLD = '3'

    RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    SUITS = ['h', 's', 'd', 'c']
    DECK = [rank + suit for rank in RANKS for suit in SUITS]

    @staticmethod
    def deal_cards():
        sample = random.sample(Game.DECK, 4)
        player_one_cards = sample[0:2]
        player_two_cards = sample[2:]

        return player_one_cards, player_two_cards

    @staticmethod
    def deal_cards_biased(player_one_favored):
        rand_hand = random.sample(Game.DECK, 2)
        strong_hand = list()

        # Strong suited ace
        if random.random() > 0.9:
            strong_hand.append('Ah')
            if random.random() > 0.5:
                strong_hand.append('Kh')
            elif random.random() > 0.5:
                strong_hand.append('Qh')
            else:
                strong_hand.append('Jh')
        # Pocket pair
        else:
            rank = random.choice(Game.RANKS)
            strong_hand.append(rank + 'h')
            strong_hand.append(rank + 's')

        if player_one_favored:
            return strong_hand, rand_hand
        else:
            return rand_hand, strong_hand

    @staticmethod
    def get_higher_rank(rank1, rank2):
        for rank in Game.RANKS:
            if rank1 == rank:
                return rank1
            if rank2 == rank:
                return rank2

        return rank1
class CFR():
    def __init__(self):
        self.game_states_ = dict() # maps history to node

    def simplify_hand(self, hand):
        ''' Takes a hand (array of size two) and compresses the hand into simpler representation
            Also puts higher card in front

            i.e. Th 9h becomes T9s as both cards share the same suit
                Th 9s becomes T9o as both cards do not share the same suit (off-suit)
                Th Ts becomes TT (pair of tens)
        '''
        rank1 = hand[0][0]
        suit1 = hand[0][1]
        rank2 = hand[1][0]
        suit2 = hand[1][1]

        # pair
        if rank1 == rank2:
            return rank1 + rank2

        hand = Game.get_higher_rank(rank1, rank2)
        hand += rank2 if hand==rank1 else rank1
        hand += 's' if suit1==suit2 else 'o'

        return hand

    def get_winner(self, hand1, hand2):
        ''' Gets the winner between the two hands
            Pair > Suited > Off-suited
            If two hands are in the same category, then the higher card of each hand
            breaks the tie, followed by the second card

            returns 1 if the first hand wins
            returns 2 if the second hand wins
            returns 0 if the hands are tied
        '''

        is_hand1_pair = hand1[0]==hand1[1]
        is_hand2_pair = hand2[0]==hand2[1]

        # both pair
        if is_hand1_pair and is_hand2_pair:
            if hand1[0] == hand2[0]:
                return 0
            if hand1[0] == Game.get_higher_rank(hand1[0],hand2[0]):
                return 1
            else:
                return 2
        elif is_hand1_pair:
            return 1
        elif is_hand2_pair:
            return 2

        is_hand1_suited = hand1[2]=='s'
        is_hand2_suited = hand2[2]=='s'

        # both suited
        if is_hand1_suited and is_hand2_suited:
            if hand1[0] == hand2[0]:
                if hand1[1] == hand2[1]:
                    return 0
                if hand1[1] == Game.get_higher_rank(hand1[1], hand2[1]):
                    return 1
                return 2
            if hand1[0] == Game.get_higher_rank(hand1[0],hand2[0]):
                return 1
            else:
                return 2
        elif is_hand1_suited:
            return 1
        elif is_hand2_suited:
            return 2

        # both unsuited
        if hand1[0] == hand2[0]:
            if hand1[1] == hand2[1]:
                return 0
            if hand1[1] == Game.get_higher_rank(hand1[1], hand2[1]):
                return 1
            return 2
        if hand1[0] == Game.get_higher_rank(hand1[0],hand2[0]):
            return 1
        else:
            return 2

    def train(self, iterations, ante=1.0, bet1=2.0, bet2=8.0, print_interval=1000000):
        ''' Do ficticious self-play to find optimal strategy'''
        util = 0.0

        self.ante = ante
        self.bet1 = bet1
        self.bet2 = bet2

        print "Ante: %f   Bet-1: %f   Bet-2: %f" % (ante, bet1, bet2)

        for i in range(iterations):
            if i % print_interval == 0 and i != 0:
                print "P1 expected value after %i iterations: %f" % (i, util/i)

            # if random.random() < 0.08:
            #     if random.random() < 0.5:
            #         player_one_cards, player_two_cards = Game.deal_cards_biased(True)
            #     else:
            #         player_one_cards, player_two_cards = Game.deal_cards_biased(False)
            # else:
            #     player_one_cards, player_two_cards = Game.deal_cards()

            player_one_cards, player_two_cards = Game.deal_cards()
            p1_hand = self.simplify_hand(player_one_cards)
            p2_hand = self.simplify_hand(player_two_cards)
            cards = [p1_hand, p2_hand]
            history = list()
            util += self.cfr(cards, history, 1, 1)

        return util/iterations

    def get_strategy(self):
        result = dict()
        p1_bet = 'Player One Betting Range'
        p1_bet_call = 'Player One Call All-in Range'
        p1_check_call = 'Player One Check-Call Range'
        p1_check_raise = 'Player One Check-Raise All-in Range'

        p2_call = 'Player Two Calling Range'
        p2_raise = 'Player Two All-in Range'
        p2_bet = 'Player Two Betting Range'
        p2_bet_call = 'Player Two Call All-in Range'

        result[p1_bet] = dict()
        result[p1_bet_call] = dict()
        result[p1_check_raise] = dict()
        result[p1_check_call] = dict()

        result[p2_call] = dict()
        result[p2_raise] = dict()
        result[p2_bet] = dict()
        result[p2_bet_call] = dict()

        for state, node in self.game_states_.items():
            hand = state[0:2] if state[0] == state[1] else state[0:3]
            history = state[2:] if len(hand) == 2 else state[3:]

            # player 1
            if len(history) == 0:
                result[p1_bet][hand] = node.strategy_[Game.BET]
            # player 2
            elif len(history) == 1:
                if history[0] == Game.CHECK:
                    result[p2_bet][hand] = node.strategy_[Game.BET]
                else:
                    result[p2_raise][hand] = node.strategy_[Game.BET]
                    result[p2_call][hand] = node.strategy_[Game.CALL]
            #player 1
            elif len(history) == 2:
                if history[0] == Game.BET:
                    result[p1_bet_call][hand] = node.strategy_[Game.CALL]
                else:
                    result[p1_check_raise][hand] = node.strategy_[Game.BET]
                    result[p1_check_call][hand] = node.strategy_[Game.CALL]
            #player 2
            elif len(history) == 3:
                result[p2_bet_call][hand] = node.strategy_[Game.CALL]

        # clean graphs
        tol = 0.005
        for hand, frequency in result[p1_bet].items():
            if frequency > 1 - tol and hand in result[p1_check_raise]:
                result[p1_check_raise][hand] = 0.0
            if frequency > 1 - tol and hand in result[p1_check_call]:
                result[p1_check_call][hand] = 0.0
            if frequency < tol and hand in result[p1_bet_call]:
                result[p1_bet_call][hand] = 0.0
        for hand, frequency in result[p2_bet].items():
            if frequency < tol and hand in result[p2_bet_call]:
                result[p2_bet_call][hand] = 0.0

        return result

    # @cards - the cards the players have, with index 0 being the card that player one has
    # and index 1 being the card that player two has
    # @history - a list of moves used to reach this game state
    # @probability1 - the probability of reaching this game state for player 1
    # @probability2 - the probability of reaching this game state for player 2
    def cfr(self, cards, history, probability1, probability2):
        num_moves = len(history)
        player = num_moves % 2
        opponent = 1 - player
        player_hand = cards[player]
        opponent_hand = cards[opponent]

        probability_weight = probability1 if player == 0 else probability2

        # can only end if at least 2 moves
        if num_moves >= 2:
            # Opponent folded
            if history[-1] == Game.FOLD:
                num_bets = 0
                for action in history:
                    if action == Game.BET:
                        num_bets += 1

                if num_bets == 2:
                    return self.ante + self.bet1

                return self.ante
            # Opponent called a bet
            if history[-1] == Game.CALL:
                winner = self.get_winner(player_hand, opponent_hand)
                if winner == 0:
                    return 0

                reward = self.ante
                num_bets = 0
                for action in history:
                    if action == Game.BET:
                        num_bets += 1
                if num_bets == 2:
                    reward += self.bet2
                elif num_bets == 1:
                    reward += self.bet1
                return reward if winner==1 else -reward

            # Check check
            if history[-1] == Game.CHECK:
                winner = self.get_winner(player_hand, opponent_hand)

                if winner == 0:
                    return 0
                return self.ante if winner==1 else -self.ante

        state = str(player_hand)
        for action in history:
            state += action

        if state in self.game_states_:
            node = self.game_states_[state] # Get our node if it already exists
            possible_actions = node.actions_
        else:
            # Create new Node with possible actions we can perform
            if len(history) == 0:
                possible_actions = [Game.CHECK, Game.BET]
            else:
                if history[-1] == Game.BET:
                    possible_actions = [Game.CALL, Game.FOLD]

                    num_bets = 0
                    for action in history:
                        if action == Game.BET:
                            num_bets += 1

                    if num_bets == 1:
                        possible_actions.append(Game.BET)
                else:
                    possible_actions = [Game.CHECK, Game.BET]

            node = Node(possible_actions)
            self.game_states_[state] = node

        strategy = node.get_strategy(probability_weight)
        util = dict()
        node_util = 0
        # for each of our possible actions, compute the utility of it
        # thus, finding the overall utility of this current state
        for action in possible_actions:
            next_history = list(history) # copy
            next_history.append(action)

            if player == 0:
                util[action] = -self.cfr(cards, next_history, probability1 * strategy[action], probability2)
            else:
                util[action] = -self.cfr(cards, next_history, probability1, probability2 * strategy[action])


            node_util += strategy[action] * util[action]

        # compute regret and update Game State for the node based on utility of all actions
        for action in possible_actions:
            regret = util[action] - node_util
            if player == 0:
                node.regret_sum_[action] += regret * probability2
            else:
                node.regret_sum_[action] += regret * probability1

        return node_util

class Node():
    def __init__(self, actions):
        self.actions_ = actions
        self.regret_sum_ = dict()
        self.strategy_ = dict()
        self.strategy_sum_ = dict()

        for action in actions:
            self.regret_sum_[action] = 0.0
            self.strategy_[action] = 0.0
            self.strategy_sum_[action] = 0.0

    def get_strategy(self, realization_weight):
        normalizing_sum = 0

        for action in self.actions_:
            self.strategy_[action] = self.regret_sum_[action] if self.regret_sum_[action] > 0 else 0
            normalizing_sum += self.strategy_[action]

        for action in self.actions_:
            if normalizing_sum > 0:
                self.strategy_[action] /= normalizing_sum
            else:
                self.strategy_[action] = 1.0 / len(self.actions_)

            self.strategy_sum_[action] += realization_weight * self.strategy_[action]

        return self.strategy_

    def get_average_strategy(self):
        average_strategy = dict
        normalizing_sum = 0

        for action in self.actions_:
            normalizing_sum += self.strategy_sum_[action]

        for action in self.actions_:
            if normalizing_sum > 0:
                average_strategy[action] = self.strategy_sum_[action] / normalizing_sum
            else:
                average_strategy[action] = 1.0 / len(self.actions_);

        return average_strategy
