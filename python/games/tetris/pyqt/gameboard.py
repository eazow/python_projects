import random
from utils import *
from shapes import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame


class InnerBoard:
    def __init__(self, width=10, height=22):
        self.width = width
        self.height = height
        self.reset()

    def can_move(self, coord, direction=None):
        assert len(coord) == 2
        if direction is None:
            direction = self.current_direction
        for x, y in self.current_tetris.get_absolute_coords(
            direction, coord[0], coord[1]
        ):
            # 超出边界
            if x >= self.width or x < 0 or y >= self.height or y < 0:
                return False
            # 该位置有俄罗斯方块了
            if self.get_coord_value([x, y]) > 0:
                return False
        return True

    def move_right(self):
        if self.can_move([self.current_coord[0] + 1, self.current_coord[1]]):
            self.current_coord[0] += 1

    def move_left(self):
        if self.can_move([self.current_coord[0] - 1, self.current_coord[1]]):
            self.current_coord[0] -= 1

    def rotate_clockwise(self):
        """顺时针转"""
        if self.can_move(self.current_coord, (self.current_direction - 1) % 4):
            self.current_direction = (self.current_direction - 1) % 4

    def rotate_anticlockwise(self):
        """逆时针转"""
        if self.can_move(self.current_coord, (self.current_direction + 1) % 4):
            self.current_direction = (self.current_direction + 1) % 4

    def move_down(self):
        removed_lines = 0
        if self.can_move([self.current_coord[0], self.current_coord[1] + 1]):
            self.current_coord[1] += 1
        else:
            x_min, x_max, y_min, y_max = self.current_tetris.get_relative_boundary(
                self.current_direction
            )
            # 简单起见, 有超出屏幕就判定游戏结束
            if self.current_coord[1] + y_min < 0:
                self.is_gameover = True
                return removed_lines
            self.merge_tetris()
            removed_lines = self.remove_full_lines()
            self.create_tetris()
        return removed_lines

    def drop_down(self):
        removed_lines = 0
        while self.can_move([self.current_coord[0], self.current_coord[1] + 1]):
            self.current_coord[1] += 1
        x_min, x_max, y_min, y_max = self.current_tetris.get_relative_boundary(
            self.current_direction
        )
        # 超出屏幕就判定游戏结束
        if self.current_coord[1] + y_min < 0:
            self.is_gameover = True
            return removed_lines
        self.merge_tetris()
        removed_lines = self.remove_full_lines()
        self.create_tetris()
        return removed_lines

    def merge_tetris(self):
        """合并俄罗斯方块(最下面定型不能再动的那些)"""

        for x, y in self.current_tetris.get_absolute_coords(
            self.current_direction, self.current_coord[0], self.current_coord[1]
        ):
            self.board_data[x + y * self.width] = self.current_tetris.shape
        self.current_coord = [-1, -1]
        self.current_direction = 0
        self.current_tetris = TetrisShape()

    """移出整行都有小方块的"""

    def remove_full_lines(self):
        new_board_data = [0] * self.width * self.height
        new_y = self.height - 1
        removed_lines = 0
        for y in range(self.height - 1, -1, -1):
            cell_count = sum(
                [
                    1 if self.board_data[x + y * self.width] > 0 else 0
                    for x in range(self.width)
                ]
            )
            if cell_count < self.width:
                for x in range(self.width):
                    new_board_data[x + new_y * self.width] = self.board_data[
                        x + y * self.width
                    ]
                new_y -= 1
            else:
                removed_lines += 1
        self.board_data = new_board_data
        return removed_lines

    def create_tetris(self):
        """创建新的俄罗斯方块(即将next_tetris变为current_tetris)"""
        x_min, x_max, y_min, y_max = self.next_tetris.get_relative_boundary(0)
        # y_min肯定是-1
        if self.can_move([self.init_x, -y_min]):
            self.current_coord = [self.init_x, -y_min]
            self.current_tetris = self.next_tetris
            self.next_tetris = self.get_next_tetris()
        else:
            self.is_gameover = True
        self.shape_statistics[self.current_tetris.shape] += 1

    def get_next_tetris(self):
        """获得下个俄罗斯方块"""
        return TetrisShape(random.randint(1, 7))

    def get_board_data(self):
        """获得板块数据"""
        return self.board_data

    def get_coord_value(self, coord):
        """获得板块数据上某坐标的值"""
        return self.board_data[coord[0] + coord[1] * self.width]

    def get_current_tetris_coords(self):
        """获得俄罗斯方块各个小块的绝对坐标"""

        return self.current_tetris.get_absolute_coords(
            self.current_direction, self.current_coord[0], self.current_coord[1]
        )

    def reset(self):
        # 记录板块数据
        self.board_data = [0] * self.width * self.height
        # 当前俄罗斯方块的旋转状态
        self.current_direction = 0
        # 当前俄罗斯方块的坐标, 单位长度为小方块边长
        self.current_coord = [-1, -1]
        # 下一个俄罗斯方块
        self.next_tetris = self.get_next_tetris()
        # 当前俄罗斯方块
        self.current_tetris = TetrisShape()
        # 游戏是否结束
        self.is_gameover = False
        # 俄罗斯方块的初始x位置
        self.init_x = self.width // 2
        # 形状数量统计
        self.shape_statistics = [0] * 8


class ExternalBoard(QFrame):
    score_signal = pyqtSignal(str)

    def __init__(self, parent, grid_size, inner_board):
        super(ExternalBoard, self).__init__(parent)
        self.grid_size = grid_size
        self.inner_board = inner_board
        self.setFixedSize(grid_size * inner_board.width, grid_size * inner_board.height)
        self.score = 0

    def paintEvent(self, event):
        """把内部板块结构画出来"""
        painter = QPainter(self)
        for x in range(self.inner_board.width):
            for y in range(self.inner_board.height):
                shape = self.inner_board.get_coord_value([x, y])
                draw_cell(
                    painter,
                    x * self.grid_size,
                    y * self.grid_size,
                    shape,
                    self.grid_size,
                )
        for x, y in self.inner_board.get_current_tetris_coords():
            shape = self.inner_board.current_tetris.shape
            draw_cell(
                painter, x * self.grid_size, y * self.grid_size, shape, self.grid_size
            )
        painter.setPen(QColor(0x777777))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())
        painter.drawLine(0, self.height(), self.width(), self.height())

    def updateData(self):
        self.score_signal.emit(str(self.score))
        self.update()


class SidePanel(QFrame):
    def __init__(self, parent, grid_size, inner_board):
        super(SidePanel, self).__init__(parent)
        self.grid_size = grid_size
        self.inner_board = inner_board
        self.setFixedSize(grid_size * 5, grid_size * inner_board.height)
        self.move(grid_size * inner_board.width, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        x_min, x_max, y_min, y_max = self.inner_board.next_tetris.get_relative_boundary(
            0
        )
        dy = 3 * self.grid_size
        dx = (self.width() - (x_max - x_min) * self.grid_size) / 2
        shape = self.inner_board.next_tetris.shape
        for x, y in self.inner_board.next_tetris.get_absolute_coords(0, 0, -y_min):
            draw_cell(
                painter,
                x * self.grid_size + dx,
                y * self.grid_size + dy,
                shape,
                self.grid_size,
            )

    def updateData(self):
        self.update()
