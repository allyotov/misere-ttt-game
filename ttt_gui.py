# import logging
from  functools import partial
import sys
import random

import numpy

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG, format='%(filename)s | %(levelname)s: %(message)s')

EMPTY_MARK = '_'
PLAYER_MARK = 'X'
COMP_MARK = '0'

class MisereTTTGameClass(QMainWindow):
    """
    Class of UI
    """

    def __init__(self):
        super(MisereTTTGameClass, self).__init__(parent=None)

        self.setAttribute(Qt.WA_DeleteOnClose)

        #main window
        self.setWindowTitle('Misere TTT Game')
        self.central_wdg = QWidget()
        self.setCentralWidget(self.central_wdg)

        #main layout
        self.grid_lo = QGridLayout(self.central_wdg)

        i = 0
        self.buttons = []
        self.labels = []
        for y in range(10):
            label_row = []
            buttons_row = []
            for x in range(10):
                label_row.append(None)
                bt = QPushButton()
                buttons_row.append(bt)
                bt.setFixedHeight(30)
                bt.setFixedWidth(30)
                self.grid_lo.addWidget(bt, y, x)
                bt.clicked.connect(partial(self.make_user_turn, [bt, y, x]))
                i += 1
            self.buttons.append(buttons_row)
            self.labels.append(label_row)

    def make_user_turn(self, args):
        bt, y, x = args
        bt.deleteLater()
        new_label = QLabel('   X')
        self.labels[y][x] = new_label
        self.grid_lo.addWidget(new_label, y, x)
        self.player_position = [x, y]
        if not self.end_turn():
            self.make_computer_turn()
        
    def get_next_turn(self):
        return (9, self.sudden_death)

    def space_check(self, position):
        return self.play_board[position[0]][position[1]] == EMPTY_MARK

    def get_unchecked_position(self, checked_positions):
        while True:
            position = (random.randint(0, 9), random.randint(0, 9))
            if (position not in checked_positions) and (self.space_check(position)):
                return position

    def get_marks_count_around(self, x, y, dir_x, dir_y):
        x = x + dir_x
        y = y + dir_y
        count = 0
        while (x < 10) and (y < 10) and (x >= 0) and (y >= 0) and (self.play_board[x][y] == self.mark):
            count += 1
            x = x + dir_x
            y = y + dir_y
        return count

    def get_max_marks_count_around(self, position_tuple):
        x = position_tuple[0]
        y = position_tuple[1]
        counts = [self.get_marks_count_around(x, y, 1, 0) + self.get_marks_count_around(x, y, -1, 0),
                self.get_marks_count_around(x, y, 0, -1) + self.get_marks_count_around(x, y, 0, 1),
                self.get_marks_count_around(x, y, 1, 1) + self.get_marks_count_around(x, y, -1, -1),
                self.get_marks_count_around(x, y, 1, -1) + self.get_marks_count_around(x, y, -1, 1)]
        return max(counts)

    def pc_choice(self):
        checked_positions = []

        current_min_count_around = self.min_pc_around

        count = 5
        while count != current_min_count_around and len(checked_positions) != self.amount_free_positions:
            position_tuple = self.get_unchecked_position(checked_positions)
            checked_positions.append(position_tuple)
            max_count_around = self.get_max_marks_count_around(position_tuple)
            if max_count_around <= count:
                choice = {'position_tuple': position_tuple, 'max_count_around': max_count_around}
                count = max_count_around
        return choice
    
    def make_computer_turn(self):
        dic_pc_position = self.pc_choice()
        if dic_pc_position['max_count_around'] > self.min_pc_around:
            self.min_pc_around = dic_pc_position['max_count_around']
        self.player_position = dic_pc_position['position_tuple']

        x, y = self.player_position
        self.buttons[y][x].deleteLater()
        new_label = QLabel('   O')
        self.labels[y][x] = new_label
        self.grid_lo.addWidget(new_label, y, x)
        self.end_turn()

    def ask_who_plays_first(self):
        button = QMessageBox.question(self, "Очередность ходов", "Хотите ходить первым?")
        if button == QMessageBox.Yes:
            self.user_mark = 'X'
            return True
        self.user_mark = '0'
        return False
    
    def ask_to_replay(self):
        button = QMessageBox.question(self, "Конец игры", "{} Cыграем ещё?".format(self.game_over_msg))
        if button == QMessageBox.Yes:
            self.init_new_game()
        else:
            self.close()

    def init_new_game(self):
        self.play_board = None
        self.player_marks = None
        self.current_player_mark = None
        self.amount_free_positions = 100
        self.min_pc_around = 0
        self.new_play_board()
        self.refresh_ui()
        self.min_pc_around = 0
        self.mark = PLAYER_MARK
        if not self.ask_who_plays_first():
            self.mark = COMP_MARK
            self.make_computer_turn()

    def new_play_board(self):
        self.play_board = [['_' for j in range(0, 10)] for i in range(0, 10)]

    def refresh_ui(self):
        for y in range(0, 10):
            for x in range(0, 10):
                label = self.labels[y][x]
                if label is not None:
                    label.deleteLater()
                    bt = QPushButton()
                    bt.setFixedHeight(30)
                    bt.setFixedWidth(30)
                    self.grid_lo.addWidget(bt, y, x)
                    self.buttons[y][x] = bt
                    bt.clicked.connect(partial(self.make_user_turn, [bt, y, x]))
                    self.labels[y][x] = None

    def place_marker(self):
        self.play_board[self.player_position[0]][self.player_position[1]] = self.mark

    def vertical_horizontal_loss(self, horizontal=False):
        i = 0
        while i < 10:
            count = 0
            j = 0
            while j < 10:
                if horizontal:
                    cell = self.play_board[i][j]
                else:
                    cell = self.play_board[j][i]
                if cell == self.mark:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0
                j += 1
            i += 1
        return False

    def diagonal_loss(self, flip=False):
        board = self.play_board
        if flip:
            board = numpy.fliplr(self.play_board)
        for i in range(-5, 5):
            ar = numpy.diagonal(board, i)
            count = 0
            for el in ar:
                if el == self.mark:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0
        return False

    def loss_check(self):
        if self.vertical_horizontal_loss() or self.vertical_horizontal_loss(True) or \
                self.diagonal_loss() or self.diagonal_loss(flip=True):
            return True
        return False

    def check_game_finish(self):
        if self.loss_check():
            if self.mark == PLAYER_MARK:
                self.game_over_msg = 'Вы проиграли!'
            else:
                self.game_over_msg = 'Вы выиграли!'
            return True

        if self.amount_free_positions == 0:
            self.game_over_msg = 'Ничья.'
            return True

        return False
        
    def switch_player(self):
        self.mark = COMP_MARK if self.mark == PLAYER_MARK else PLAYER_MARK

    def end_turn(self):
        self.place_marker()
        self.amount_free_positions -= 1
        if_game_finished = self.check_game_finish()
        self.switch_player()
        if if_game_finished:
            self.ask_to_replay()
        
        return if_game_finished

def run_gui():
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = MisereTTTGameClass()
    form.show()
    form.init_new_game()
    # Run the main Qt loop
    sys.exit(app.exec())


if __name__ == '__main__':
    run_gui()