# Two Card Poker AI
Previously, I worked on One Card Poker and used Counter Factual Regret Minimization (CFR) to computer the game theory optimal (GTO) solution to the game from scratch. I was happy to find that the solution developed through self-play by the CFR agent closely matched the GTO solution proposed by a CMU professor who computed it through linear constraint solving.

Now with a stronger background in how the CFR algorithm worked, I wanted to try a game with more depth and breadth than just One Card Poker, which featured only 13 cards and one bet maximum. Consequently, I moved on to Two Card poker, which features a full 52 card deck and allows multiple bets in the betting round. So now an artificial intelligence agent must be able to decide upon 1326 different possible hands and what to do with each and every possible combination in the game. It must learn the relative strength of each hand from scratch and discover the optimal strategy for each hand. Additionally, it must develop an overall balanced strategy, and decide a range of hands it should bet and a range of hands it should check-call, check-raise, or check-fold.

This idea of range is integral to much more complicated games like No Limit Texas Hold'Em. The idea is no longer how a single, particular hand should be played, but what hands overall should be played and how. And to win in the long run, players adjust their ranges until it is perfect and game theory optimal.

So the biggest challenge is for the CFR agent to construct a GTO ranges for both players, and do so from scratch.

# Rules of Two Card Poker:
The game is played using a standard 52 card deck. At the beginning of the round, both players pay a $1 ante. Each player is dealt two private cards, and then there is a round of betting. Players take turns in this round of betting. Initially, the player may check or bet (put more money in the middle). If both players check, then showdown is reached and both players reveal their cards, and the player with the strong hand wins the money in the middle.
If a player bets, the other player has the option to raise, call, or fold. If the player folds, the other player wins the money in the middle. If the player calls, then showdown is reached. If the player decides to raise, then action is on the other player, who has the option to raise, call, or fold.
For this game, I decided to put a limit to a maximum of 2 bets. So this means that only one raise is allowed.
The first bet is set to $2, so a player will be betting $2 into a pot of $2.
The raise is set to $8, so a player will be betting $8 into a pot of $4.

Showdown/Card Strength:
In Two Card Poker, the strength of the category of hands (from strongest to weakest):
* pairs (two cards with the same rank, like Ah As)
* suited cards (two cards with the same suit, like As Ts)
* unsuited cards (two cards with different suits, like Ks 5d)

Card ranks, from strongest to weakest, goes from A, K, Q, J, T, 9, 8, ..., 3, 2

When comparing two hands, if the hands are in different categories, then the hand in the better category wins. If hands are in the same category, then the hand with the higher rank wins. If both hands have the same high rank, then the second card determines which hand wins). If it is still a tie, then the pot is split.

# Results
After training the CFR agent to play itself for 40 million hands, the agent has developed a pretty balanced strategy for both players. It was capable of developing an optimal ranges and taught itself how to bluff and slowplay, and to not always do one or the other. The strategy it developed is balanced and difficult, if not almost impossible, for an opponent to exploit. I also created a visual using python matlibplot to summarize the hand ranges for differing strategies the bot developed autonomously.

So before we get into results, we first need to understand how the game can possible progress. In other words, look at the game decision tree:
* P1 Bets
   * P2 Folds
   * P2 Calls
   * P2 Raises
      * P1 Calls
      * P1 Folds
* P1 Checks
   * P2 Checks
   * P2 Bets
   * P1 Raises
      * P2 Calls
      * P2 Folds
   * P1 Folds
   * P1 Calls

Additionally, we need to understand what a range chart means:
![Alt text](/strategy_charts/p1_check_raise.png?raw=true "P1 Check-Raise Range")

There are 1326 different possible hands (choose two cards from 52), but we can bucket all these hands into 169 different kinds of hands. 13 different pairs, 79 suited hands, and 79 off-suited hands. In this chart, the hands along the diagonal represent pairs, the upper-right corner represents suited hands, and the bottom left corner represents off-suited hands.

This particular chart is for player one and what kind of hands the CFR agent decides to check and then raise when facing a bet. Green represents 100% of the time or almost always, yellow represents around 50-75% of the time, orange represents 25-50% of the time, and red is never or almost never. There are two other colors, but they are not on this graph (yellow-green 75-90%, and orange-red 5-25%)

So this chart is saying that the player should always raise AA, KK, QQ, ... 88, AKs, AQs, A9o, and K9o. The player should sometimes raise AJs, A8o, and K3o.
When we interpret this chart, we notice that there are a lot of strong hands, like the pairs and strong suited hands like AKs, AQs, and AJs. Additionally, the player does have some bluffs sometimes, like A9o, A8o, and K3o.

