import sys
import random
from PySide6.QtWidgets import QMainWindow, QLabel, QApplication, QMenu
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt, QTimer, QRect

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        #窗口设置
        self.setWindowTitle("Tairitsu")
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint  # 永远置顶
        )

        self.setAttribute(Qt.WA_TranslucentBackground) # 背景透明

        #固定大小
        self.resize(100, 100)

        #宠物显示
        self.pet_label = QLabel(self)
        self.pet_label.setScaledContents(True)
        self.pet_label.setGeometry(0, 0, 100, 100)
        #加载动画序列
        self.stand = QPixmap("stand.png")#站立
        self.tuodong = QPixmap("tuodong.png")#拖动
        #左走动
        self.left_anim_a = [QPixmap(f"lefta{i}.png") for i in range(1, 3)]
        self.left_anim_b = [QPixmap(f"leftb{i}.png") for i in range(1, 4)]

        #右走动
        self.right_anim_a = [QPixmap(f"righta{i}.png") for i in range(1, 3)]
        self.right_anim_b = [QPixmap(f"rightb{i}.png") for i in range(1, 4)]
        #开启动画
        self.start_anim = [QPixmap(f"start{i}.png") for i in range(1, 6)]
        #关闭动画
        self.close_anim = [QPixmap(f"close{i}.png") for i in range(1, 3)]

        #动画状态
        self.current_frames = []
        self.current_frame = 0
        self.pet_label.setPixmap(self.stand)

        #拖动功能
        self.drag_pos = None
        self.isDragging = False

        #走动
        self.isFreeWalking = False
        self.walkingDirection = random.choice(["left", "right"])
        self.current_suit = None
        self.current_frame = 0


        #动画定时器
        self.state = "start_anim"
        self.start_play_time = 3000  # 开始动画持续时间（毫秒）
        self.close_play_time = 1000  # 结束动画持续时间（毫秒）
        self.frame_interval = 150  # 每帧间隔时间（毫秒）
        #全局统一定时器
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_all)
        self.anim_timer.start(self.frame_interval) # 150ms更新一次动画

        #开启动画倒计时定时器
        self.start_timer = QTimer()
        self.start_timer.setSingleShot(True)
        self.start_timer.timeout.connect(self.finish_start_anim)
        self.start_timer.start(self.start_play_time)

        #右键菜单
        self.right_menu = QMenu(self)
        walk_act = self.right_menu.addAction("走动")
        quit_act = self.right_menu.addAction("退出")

        walk_act.triggered.connect(self.toggleWalk)
        quit_act.triggered.connect(self.begin_end_anim)  # <--- 我帮你改这里

    #动画+移动
    def toggleWalk(self):
        if self.isDragging or self.state in ["start_anim", "close_anim"]:
            return
        self.isFreeWalking = not self.isFreeWalking
        if self.isFreeWalking:
            self.current_suit = random.choice(["a", "b"])
            self.current_frame = 0
        else:
            self.pet_label.setPixmap(self.stand)

    def update_all(self):
        #优先级1：开启动画
        if self.state == "start_anim":
            self.pet_label.setPixmap(self.start_anim[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.start_anim)
            return
        #优先级2：结束动画
        if self.state == "close_anim":  # <--- 统一名称
            self.pet_label.setPixmap(self.close_anim[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.close_anim)
            return

        if self.isDragging:
            self.pet_label.setPixmap(self.tuodong)
            return  

        if not self.isFreeWalking:
            self.pet_label.setPixmap(self.stand)
            return

        self.walk_move()

        if self.walkingDirection == "left":
            frame_list = self.left_anim_a if self.current_suit == "a" else self.left_anim_b
        else:
            frame_list = self.right_anim_a if self.current_suit == "a" else self.right_anim_b

        self.pet_label.setPixmap(frame_list[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(frame_list)

    def walk_move(self):
        screen = self.app.primaryScreen().geometry()
        x, y = self.pos().x(), self.pos().y()

        if self.walkingDirection == "left":
            if x > 0:
                self.move(x - 4, y)
            else:
                self.walkingDirection = "right"
        else:
            if x + self.width() < screen.width():
                self.move(x + 4, y)
            else:
                self.walkingDirection = "left"

    def finish_start_anim(self):
        self.state = "idle"
        self.current_frame = 0

    # ===================== 修复：正确播放结束动画 =====================
    def begin_end_anim(self):
        # 先禁止所有操作
        self.isDragging = False
        self.isFreeWalking = False
        self.state = "close_anim"  # <--- 统一名称
        self.current_frame = 0

        # 播放完一轮关闭动画后退出
        end_time = self.close_play_time
        self.exit_timer = QTimer()
        self.exit_timer.setSingleShot(True)
        self.exit_timer.timeout.connect(self.closePet)
        self.exit_timer.start(end_time)

    #右键弹出
    def contextMenuEvent(self, event):
        self.right_menu.exec(event.globalPos())

    #关闭桌宠
    def closePet(self):
        print("桌宠已退出")
        self.close()
        QApplication.quit()

    #鼠标拖动实现
    def mousePressEvent(self, event):
        if self.state in ["start_anim", "close_anim"]:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.isDragging = True
            self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.isDragging = False
            self.isFreeWalking = False
            self.drag_pos = None
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            trigger_area = QRect(0, 0, self.width(), self.height()//4)
            if trigger_area.contains(event.pos()):
                print("哈气")
            else:
                print("点击身体")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = MainWindow(app)
    pet.show()
    sys.exit(app.exec())