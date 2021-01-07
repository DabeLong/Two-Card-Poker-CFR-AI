import matplotlib.pyplot as plt
from matplotlib.table import Table

from cfr import CFR

cfr = CFR()
ante = 1.0
bet1 = 2.0
bet2 = 8.0

util = cfr.train(40000000, ante, bet1, bet2)

label = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
rank_index_map = {
    'A': 0, 'K': 1, 'Q': 2,
    'J': 3, 'T': 4, '9': 5,
    '8': 6, '7': 7, '6': 8,
    '5': 9, '4': 10, '3': 11, '2': 12,
}


def get_color(frequency):
    if frequency >= 0.9:
        return 'green'
    elif frequency >= 0.75:
        return 'yellowgreen'
    elif frequency >= 0.5:
        return 'yellow'
    elif frequency >= 0.25:
        return 'orange'
    elif frequency >= 0.05:
        return 'orangered'
    else:
        return 'red'


def create_table(title, frequencies):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    tb = Table(ax, bbox=[0, 0, 1, 1])

    nrows, ncols = len(label), len(label)
    width, height = 1.0 / ncols, 1.0 / nrows

    # Add cells
    for hand, val in frequencies.items():
        i, j = rank_index_map[hand[0]], rank_index_map[hand[1]]
        if len(hand) == 3 and hand[2] == 'o':
            i, j = j, i

        color = get_color(val)

        value_formatted = '{0:.2f}'.format(val)
        tb.add_cell(i + 1, j, width, height, text=hand,
                    loc='center', facecolor=color)

    # Row Labels...
    for i in range(len(label)):
        tb.add_cell(i + 1, -1, width, height, text=label[i], loc='right',
                    edgecolor='none', facecolor='none')
    # Column Labels...
    for j in range(len(label)):
        tb.add_cell(
            0, j, width, height / 2,
            text=label[j], loc='center', edgecolor='none', facecolor='none')
    ax.add_table(tb)
    plt.title(title)
    return fig


print("Player One Expected Value Per Hand: %f" % util)

result = cfr.get_strategy()

for decision in sorted(result):
    table = create_table(decision, result[decision])

plt.show()
