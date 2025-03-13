import os
import shutil
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QGridLayout
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QGridLayout, QListWidgetItem
# 资源文件（背景图 & 字体）
BACKGROUND_IMAGE = "2025-03-10 122931.jpg"
FONT_PATH = "darkest_dungeon.ttf"  # Gothic 风格字体

# 1. Steam 存档路径
STEAM_ROOT = r"C:\Program Files (x86)\Steam\userdata"
GAME_ID = "262060"
REMOTE_PATH = None  # 目标 remote 文件夹路径

# 2. 存档保存目录（当前 EXE 所在目录）
SAVE_DIR = os.path.abspath(os.getcwd())

class SteamBackupApp(QWidget):
    def __init__(self):
        super().__init__()

        # **确保背景图片存在**
        if not os.path.exists(BACKGROUND_IMAGE):
            print(f"❌ 背景图片 {BACKGROUND_IMAGE} 不存在，使用默认窗口大小")
            self.image_width, self.image_height = 800, 450
        else:
            # **获取背景图片尺寸**
            pixmap = QPixmap(BACKGROUND_IMAGE)
            self.image_width = pixmap.width()
            self.image_height = pixmap.height()
            print(f"✅ 设定窗口大小: {self.image_width}x{self.image_height}")

        # **窗口大小 & 禁止调整**
        self.setGeometry(300, 300, self.image_width, self.image_height)
        self.setFixedSize(self.image_width, self.image_height)  # ✅ **固定窗口大小**

        self.setWindowTitle("Darkest Dungeon Saver")



        # **加载字体**
        self.custom_font = self.load_custom_font(FONT_PATH, 24)  # 字体大小提升 2 号

        # **设置背景图片**
        self.set_background()

        # 主布局（水平布局）
        main_layout = QHBoxLayout()

        # **左侧按钮**
        button_layout = QVBoxLayout()
        self.btn_scan = self.create_button("Check")
        self.btn_scan.clicked.connect(self.scan_remote_folder)
        button_layout.addWidget(self.btn_scan)

        self.btn_save = self.create_button("Save")
        self.btn_save.clicked.connect(self.save_remote_folder)
        button_layout.addWidget(self.btn_save)

        self.btn_load = self.create_button("Load")
        self.btn_load.clicked.connect(self.restore_remote_folder)
        button_layout.addWidget(self.btn_load)

        self.btn_delete = self.create_button("Delete")  # 新增删除按钮
        self.btn_delete.clicked.connect(self.delete_selected_backup)
        button_layout.addWidget(self.btn_delete)

        main_layout.addLayout(button_layout)  # 把按钮放在最左侧

        # **右侧存档列表**
        list_layout = QGridLayout()  # 网格布局，每 6 个换列
        self.list_widget = QListWidget()
        self.list_widget.setFont(self.custom_font)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #FFD700;  /* 亮金色 */
                font-size: 24px;
                spacing: 15px; /* 增加存档之间的间距 */
            }
            QListWidget::item {
                background: transparent;
            }
        """)
        list_layout.addWidget(self.list_widget, 0, 1)  # 存档列表向右对齐 Check 按钮
        main_layout.addSpacing(150)  # 控制列表的距离
        main_layout.addLayout(list_layout)

        # 设置主窗口布局
        self.setLayout(main_layout)

    # 📌 创建按钮（亮金色 + 无边框）
    def create_button(self, text):
        button = QPushButton(text)
        button.setFont(self.custom_font)
        button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #FFD700; /* 亮金色 */
                font-size: 26px;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        return button

    # 📌 加载自定义字体
    def load_custom_font(self, font_path, size):
        if not font_path or not os.path.exists(font_path):
            print(f"⚠️ 字体文件 {font_path} 不存在，使用默认字体")
            return QFont("Times New Roman", size)

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"⚠️ 无法加载字体 {font_path}")
            return QFont("Times New Roman", size)

        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        print(f"✅ 加载字体成功: {font_family}")
        return QFont(font_family, size)

    # 📌 设置背景图片（适配窗口）
    def set_background(self):
        if not os.path.exists(BACKGROUND_IMAGE):
            print(f"❌ 背景图片 {BACKGROUND_IMAGE} 不存在！")
            return

        # 使用 QLabel 作为背景
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap(BACKGROUND_IMAGE))
        self.bg_label.setGeometry(0, 0, self.image_width, self.image_height)
        self.bg_label.lower()  # 确保按钮在上面

  
        # 📌 Gothic 血浆风格弹窗（成功提示完整 + 按钮缩小）
    def show_message(self, text="Successful"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Dark")  
        msg_box.setText(text)  
        msg_box.setFont(self.custom_font)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: black;
                color: #8B0000; /* 血浆红 */
                font-size: 28px;
                min-width: 500px;  /* 增加宽度 */
                min-height: 160px;  /* 增加高度 */
            }
            QLabel {
                qproperty-alignment: AlignCenter;
                font-size: 30px;  /* 调整字体大小 */
                color: #8B0000;  /* 血浆色 */
                padding: 10px;  /* 增加内边距 */
                word-wrap: true;  /* 允许换行 */
            }
            QPushButton {
                background-color: #8B0000;
                color: white;
                font-size: 18px;
                border: none;
                padding: 5px;
                min-width: 60px;  /* 缩小按钮 */
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)
        msg_box.exec()



    # 📌 1. 检索 remote 文件夹
    def scan_remote_folder(self):
        global REMOTE_PATH
        found = False

        for user_id in os.listdir(STEAM_ROOT):
            possible_path = os.path.join(STEAM_ROOT, user_id, GAME_ID, "remote")
            if os.path.exists(possible_path):
                REMOTE_PATH = possible_path
                found = True
                break

        if found:
            self.show_message("Successful")
        else:
            self.show_message("Error: Remote Folder Not Found!")

    # 📌 2. 备份 remote 文件夹至当前目录
    def save_remote_folder(self):
        if not REMOTE_PATH or not os.path.exists(REMOTE_PATH):
            self.show_message("Error: No Remote Folder Found!")
            return

        existing_folders = [int(f) for f in os.listdir(SAVE_DIR) if f.isdigit()]
        next_num = max(existing_folders) + 1 if existing_folders else 1
        new_backup_path = os.path.join(SAVE_DIR, str(next_num))

        shutil.copytree(REMOTE_PATH, new_backup_path)
        self.show_message(f"Saved Backup {next_num}")

        self.update_folder_list()
   
    # 📌 3. 读取存档并覆盖到 Remote
    def restore_remote_folder(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Select Backup Folder", SAVE_DIR)

        if not folder_name:
            return

        if not REMOTE_PATH or not os.path.exists(REMOTE_PATH):
            self.show_message("Error: No Remote Folder Found!")
            return

        # 清空 remote 目录
        for item in os.listdir(REMOTE_PATH):
            item_path = os.path.join(REMOTE_PATH, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)

        # 复制选定的存档内容回 remote 目录
        for item in os.listdir(folder_name):
            src = os.path.join(folder_name, item)
            dst = os.path.join(REMOTE_PATH, item)

            if os.path.isfile(src):  # 处理文件
                shutil.copy2(src, dst)
            elif os.path.isdir(src):  # 处理文件夹
                shutil.copytree(src, dst, dirs_exist_ok=True)

        self.show_message(f"Loaded Backup from {folder_name}")

       # 📌 删除选中的存档（确保删除后刷新列表）
    def delete_selected_backup(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            backup_path = os.path.join(SAVE_DIR, selected_item.text())

            if os.path.exists(backup_path):  # 确保存档存在
                shutil.rmtree(backup_path)  # 删除存档
                self.show_message(f"Deleted Backup {selected_item.text()}")
                self.update_folder_list()  # 删除后刷新存档列表
            else:
                self.show_message("Error: Backup Not Found!")
        else:
            self.show_message("Error: No Backup Selected!")


    # 📌 更新存档列表（让 1 对齐 X 位置，并从 7 开始换列）
    def update_folder_list(self):
        self.list_widget.clear()  # 清空旧存档

        existing_folders = sorted([f for f in os.listdir(SAVE_DIR) if f.isdigit()], key=int)

        # **让存档 1 对齐 X 位置**
        row = 0
        col = 0
        max_columns = 7  # **每 7 列换行**

        for index, folder in enumerate(existing_folders):
            item = QListWidgetItem(folder)
            item.setFont(self.custom_font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_widget.addItem(item)

            # **存档 1 放在 X 位置**
            if index == 0:  
                self.list_widget.setGeometry(180, 30, 100, 200)  # **调整 `1` 的显示位置**
            
            # **每 7 个换列**
            if (index + 1) % max_columns == 0:
                row += 1
                col = 0
            else:
                col += 1
        
        # **隐藏滚动条**
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


                


# 运行 GUI
app = QApplication(sys.argv)
window = SteamBackupApp()
window.show()
sys.exit(app.exec())
