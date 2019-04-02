import copy
# import time

# define constants
EMPTY_SPACE = 0
MY_EMITTER = 1
OP_EMITTER = 2
BLOCKER = 3
DUP_LASER = 4

UPPER_LEFT = 0
UPPER_CENTER = 1
UPPER_RIGHT = 2
MIDDLE_LEFT = 3
MIDDLE_RIGHT = 4
LOWER_LEFT = 5
LOWER_CENTER = 6
LOWER_RIGHT = 7
NUM_DIRECTION = 8

EMITTER_MIN_RANGE = 1
EMITTER_MAX_RANGE = 3

CUTOFF_DEPTH = 4

NEW_STATE = True
INI_STATE = False


def create_output(index):
    """
    create text file for output
    :param index: <tuple> - two elements
    :return: none
    """
    output_file = open("output.txt", "w")
    out_data = str(index[0]) + " " + str(index[1])
    output_file.write(out_data)
    output_file.close()


def utility_evaluation(state):
    """
    compute evaluation value for minmax algorithm
    :param state: <list> - two-dimensional
    :return: <int>
    """
    my_score = 0
    op_score = 0

    for index_list in state:
        my_score += index_list.count(MY_EMITTER) + index_list.count(DUP_LASER)
        op_score += index_list.count(OP_EMITTER) + index_list.count(DUP_LASER)
    return my_score - op_score


def terminal_test(state):
    """
    terminal condition is when there is no empty in the grid
    :param state: <list> - two-dimensional
    :return: <boolean>
    """
    # terminate stage
    num_empty = 0
    for index_list in state:
        num_empty += index_list.count(EMPTY_SPACE)
    return num_empty == 0


def action_make_index_list(state, grid_size):
    """
    create index list which contains possible movement for players
    :param state: <list> - two-dimensional
    :param grid_size: <int>
    :return: <list> - tuple - two-elements
    """
    return [(i, j) for i in range(grid_size) for j in range(grid_size) if state[i][j] == EMPTY_SPACE]


def max_func(state, grid_size, alpha, beta, depth):
    """
    choose maximum value which are selected as maximum value for us
    :param state: <list> - two-dimensional
    :param grid_size: <int>
    :param alpha <int>
    :param beta <int>
    :param depth <int>
    :return: <int>
    """
    if depth == CUTOFF_DEPTH or terminal_test(state):
        return utility_evaluation(state)
    max_value = -(grid_size * grid_size)
    for index in action_make_index_list(state, grid_size):
        max_value = max(max_value, min_func(result_state(state, index, grid_size, MY_EMITTER, NEW_STATE),
                                            grid_size, alpha, beta, depth + 1))
        if max_value >= beta:
            break
        alpha = max(alpha, max_value)
    return max_value


def min_func(state, grid_size, alpha, beta, depth):
    """
    choose minimum value which are selected as maximum value for us
    :param state: <list> - two-dimensional
    :param grid_size: <int>
    :param alpha <int>
    :param beta <int>
    :param depth <int>
    :return: <int>
    """
    if depth == CUTOFF_DEPTH or terminal_test(state):
        return utility_evaluation(state)
    min_value = grid_size * grid_size
    for index in action_make_index_list(state, grid_size):
        min_value = min(min_value, max_func(result_state(state, index, grid_size, OP_EMITTER, NEW_STATE),
                                            grid_size, alpha, beta, depth + 1))
        if min_value <= alpha:
            break
        beta = min(beta, min_value)
    return min_value


def alpha_beta_search(state, grid_size):
    """
    start minmax algorithm
    :param state:
    :param grid_size:
    :return: <tuple> - two elements
    """
    # find moves from the current state
    alpha = -grid_size * grid_size
    beta = grid_size * grid_size
    depth = 0
    max_value = -grid_size * grid_size

    for index in action_make_index_list(state, grid_size):
        value = min_func(result_state(state, index, grid_size, MY_EMITTER, NEW_STATE),
                         grid_size, alpha, beta, depth + 1)
        if max_value < value:
            max_value = value
            result = index
        if max_value >= beta:
            break
        alpha = max(alpha, value)
    return result


def result_state(state, index, grid_size, emitter, new_state):
    """
    definition of coordinates
                Left      Center      Right
    Upper  :(i-k, j-k) | (i-k, j) | (i-k, j+k)
    -------------------------------------------
    Middle :(i  , j-k) | (i  , j) | (i,   j+k)
    -------------------------------------------
    Lower  :(i+k, j-k) | (i+k, j) | (i+k, j+k)

    :param state: <list> - two-dimensional
    :param index: <tuple> - two elements
    :param grid_size: <int>
    :param emitter: <constant> - MY_EMITTER or OP_EMITTER
    :param new_state: <boolean> - initialize state or create new state
    :return: none when flag is INIT, otherwise matrix
    """
    # set start index
    i = index[0]
    j = index[1]

    # create new list when minmax function works
    if new_state:
        dummy_state = copy.deepcopy(state)
    else:
        dummy_state = state
    dummy_state[i][j] = emitter

    # select situation
    if emitter == MY_EMITTER:
        cur_laser = MY_EMITTER
        past_laser = OP_EMITTER
    else:
        cur_laser = OP_EMITTER
        past_laser = MY_EMITTER

    blocked_direction = [True] * NUM_DIRECTION

    for k in range(EMITTER_MIN_RANGE, EMITTER_MAX_RANGE + 1):
        # upper left
        if blocked_direction[UPPER_LEFT] and 0 <= i - k and 0 <= j - k:
            if dummy_state[i - k][j - k] == past_laser:
                dummy_state[i - k][j - k] = DUP_LASER
            elif dummy_state[i - k][j - k] == EMPTY_SPACE:
                dummy_state[i - k][j - k] = cur_laser
            elif dummy_state[i - k][j - k] == BLOCKER:
                blocked_direction[UPPER_LEFT] = False
        # upper center
        if blocked_direction[UPPER_CENTER] and 0 <= i - k:
            if dummy_state[i - k][j] == past_laser:
                dummy_state[i - k][j] = DUP_LASER
            elif dummy_state[i - k][j] == EMPTY_SPACE:
                dummy_state[i - k][j] = cur_laser
            elif dummy_state[i - k][j] == BLOCKER:
                blocked_direction[UPPER_CENTER] = False
        # upper right
        if blocked_direction[UPPER_RIGHT] and 0 <= i - k and j + k < grid_size:
            if dummy_state[i - k][j + k] == past_laser:
                dummy_state[i - k][j + k] = DUP_LASER
            elif dummy_state[i - k][j + k] == EMPTY_SPACE:
                dummy_state[i - k][j + k] = cur_laser
            elif dummy_state[i - k][j + k] == BLOCKER:
                blocked_direction[UPPER_RIGHT] = False
        # middle left
        if blocked_direction[MIDDLE_LEFT] and 0 <= j - k:
            if dummy_state[i][j - k] == past_laser:
                dummy_state[i][j - k] = DUP_LASER
            elif dummy_state[i][j - k] == EMPTY_SPACE:
                dummy_state[i][j - k] = cur_laser
            elif dummy_state[i][j - k] == BLOCKER:
                blocked_direction[MIDDLE_LEFT] = False
        # middle right
        if blocked_direction[MIDDLE_RIGHT] and j + k < grid_size:
            if dummy_state[i][j + k] == past_laser:
                dummy_state[i][j + k] = DUP_LASER
            elif dummy_state[i][j + k] == EMPTY_SPACE:
                dummy_state[i][j + k] = cur_laser
            elif dummy_state[i][j + k] == BLOCKER:
                blocked_direction[MIDDLE_RIGHT] = False
        # lower left
        if blocked_direction[LOWER_LEFT] and i + k < grid_size and 0 <= j - k:
            if dummy_state[i + k][j - k] == past_laser:
                dummy_state[i + k][j - k] = DUP_LASER
            elif dummy_state[i + k][j - k] == EMPTY_SPACE:
                dummy_state[i + k][j - k] = cur_laser
            elif dummy_state[i + k][j - k] == BLOCKER:
                blocked_direction[LOWER_LEFT] = False
        # lower center
        if blocked_direction[LOWER_CENTER] and i + k < grid_size:
            if dummy_state[i + k][j] == past_laser:
                dummy_state[i + k][j] = DUP_LASER
            elif dummy_state[i + k][j] == EMPTY_SPACE:
                dummy_state[i + k][j] = cur_laser
            elif dummy_state[i + k][j] == BLOCKER:
                blocked_direction[LOWER_CENTER] = False
        # lower right
        if blocked_direction[LOWER_RIGHT] and i + k < grid_size and j + k < grid_size:
            if dummy_state[i + k][j + k] == past_laser:
                dummy_state[i + k][j + k] = DUP_LASER
            elif dummy_state[i + k][j + k] == EMPTY_SPACE:
                dummy_state[i + k][j + k] = cur_laser
            elif dummy_state[i + k][j + k] == BLOCKER:
                blocked_direction[LOWER_RIGHT] = False
    if new_state:
        # when create new child
        return dummy_state


def create_initial_state(initial_state, initial_state_list_str):
    """
    Fill the grid to create a initial state for the game
    :param initial_state: <list> - two-dimensional
    :param initial_state_list_str: <list> - string
    :return: none
    """
    index_my_emitter = []
    index_op_emitter = []
    # create matrix from the str input list
    i = 0
    j = 0
    for state_str in initial_state_list_str:
        for element in state_str:
            if element == str(MY_EMITTER):
                index_my_emitter.append((i, j))
            elif element == str(OP_EMITTER):
                index_op_emitter.append((i, j))
            elif element == "\n":
                break
            initial_state[i][j] = int(element)
            j += 1
        i += 1
        j = 0
    # create my laser area
    for my_index in index_my_emitter:
        result_state(initial_state, my_index, i, MY_EMITTER, INI_STATE)
    # create opponent laser area
    for op_index in index_op_emitter:
        result_state(initial_state, op_index, i, OP_EMITTER, INI_STATE)


def open_file():
    """
    open the text file and read data into a list
    :return: <list> - string
    """
    input_file = open("input.txt")
    grid_size = input_file.readline()
    input_list = input_file.readlines()
    input_file.close()
    return grid_size, input_list


def main():
    # get data from the file
    initial_state_list_str = open_file()
    # get the size of the square
    grid_size = int(initial_state_list_str[0])
    # Create initial state
    initial_state = [[0] * grid_size for j in range(grid_size)]
    create_initial_state(initial_state, initial_state_list_str[1])

    result = alpha_beta_search(initial_state, grid_size)
    create_output(result)


# Program starts here
if __name__ == "__main__":
    main()
