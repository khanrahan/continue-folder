"""
Script Name: Continue Folder
Written By: Kieran Hanrahan

Script Version: 1.0.2
Flame Version: 2021.1

URL: http://www.github.com/khanrahan/continue-folder

Creation Date: 04.10.23
Update Date: 07.05.23

Description:

    Create a new reel on the Desktop and/or folder in the MediaHub Files tab using
    tokens, including a token to continue a number sequence in a sequence of existing
    folders.

    Tested on 2021.1 & 2024 PR180

Menus:

    Right-click selected folders in the Media Hub --> Create... --> Continue Folder

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user, copy this file to:
    /opt/Autodesk/user/<user name>/python
"""


import datetime as dt
import os
import re
import xml.etree.ElementTree as ETree
from functools import partial

import flame
from PySide2 import QtCore, QtGui, QtWidgets

TITLE = 'Continue Folder'
VERSION_INFO = (1, 0, 2, 'dev')
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'


class FlameButton(QtWidgets.QPushButton):
    """Custom Qt Flame Button Widget v2.1

    button_name: button text [str]
    connect: execute when clicked [function]
    button_color: (optional) normal, blue [str]
    button_width: (optional) default is 150 [int]
    button_max_width: (optional) default is 150 [int]

    Usage:
        button = FlameButton(
            'Button Name', do_something__when_pressed, button_color='blue')
    """
    def __init__(self, button_name, connect, button_color='normal', button_width=150,
                 button_max_width=150):
        super().__init__()

        self.setText(button_name)
        self.setMinimumSize(QtCore.QSize(button_width, 28))
        self.setMaximumSize(QtCore.QSize(button_max_width, 28))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(connect)
        if button_color == 'normal':
            self.setStyleSheet("""
                QPushButton {
                    color: rgb(154, 154, 154);
                    background-color: rgb(58, 58, 58);
                    border: none;
                    font: 14px 'Discreet'}
                QPushButton:hover {
                    border: 1px solid rgb(90, 90, 90)}
                QPushButton:pressed {
                    color: rgb(159, 159, 159);
                    background-color: rgb(66, 66, 66);
                    border: 1px solid rgb(90, 90, 90)}
                QPushButton:disabled {
                    color: rgb(116, 116, 116);
                    background-color: rgb(58, 58, 58);
                    border: none}
                QToolTip {
                    color: rgb(170, 170, 170);
                    background-color: rgb(71, 71, 71);
                    border: 10px solid rgb(71, 71, 71)}""")
        elif button_color == 'blue':
            self.setStyleSheet("""
                QPushButton {
                    color: rgb(190, 190, 190);
                    background-color: rgb(0, 110, 175);
                    border: none;
                    font: 12px 'Discreet'}
                QPushButton:hover {
                    border: 1px solid rgb(90, 90, 90)}
                QPushButton:pressed {
                    color: rgb(159, 159, 159);
                    border: 1px solid rgb(90, 90, 90)
                QPushButton:disabled {
                    color: rgb(116, 116, 116);
                    background-color: rgb(58, 58, 58);
                    border: none}
                QToolTip {
                    color: rgb(170, 170, 170);
                    background-color: rgb(71, 71, 71);
                    border: 10px solid rgb(71, 71, 71)}""")


class FlameLabel(QtWidgets.QLabel):
    """Custom Qt Flame Label Widget v2.1

    label_name:  text displayed [str]
    label_type:  (optional) select from different styles:
                 normal, underline, background. default is normal [str]
    label_width: (optional) default is 150 [int]

    Usage:
        label = FlameLabel('Label Name', 'normal', 300)
    """
    def __init__(self, label_name, label_type='normal', label_width=150):
        super().__init__()

        self.setText(label_name)
        self.setMinimumSize(label_width, 28)
        self.setMaximumHeight(28)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set label stylesheet based on label_type

        if label_type == 'normal':
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    font: 14px 'Discreet'}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")
        elif label_type == 'underline':
            self.setAlignment(QtCore.Qt.AlignCenter)
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    border-bottom: 1px inset rgb(40, 40, 40);
                    font: 14px 'Discreet'}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")
        elif label_type == 'background':
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    font: 14px 'Discreet'}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")


class FlameLineEdit(QtWidgets.QLineEdit):
    """Custom Qt Flame Line Edit Widget v2.1

    Main window should include this: window.setFocusPolicy(QtCore.Qt.StrongFocus)

    text: text show [str]
    width: (optional) width of widget. default is 150. [int]
    max_width: (optional) maximum width of widget. default is 2000. [int]

    Usage:
        line_edit = FlameLineEdit('Some text here')
    """
    def __init__(self, text, width=150, max_width=2000):
        super().__init__()

        self.setText(text)
        self.setMinimumHeight(28)
        self.setMinimumWidth(width)
        self.setMaximumWidth(max_width)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setStyleSheet("""
            QLineEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: 1px solid rgb(55, 65, 75);
                padding-left: 5px;
                font: 14px 'Discreet'}
            QLineEdit:focus {background-color: rgb(73, 86, 99)}
            QLineEdit:hover {border: 1px solid rgb(90, 90, 90)}
            QLineEdit:disabled {
                color: rgb(106, 106, 106);
                background-color: rgb(55, 55, 55);
                border: 1px solid rgb(55, 55, 55)}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: none}""")


class FlamePushButton(QtWidgets.QPushButton):
    """Custom Qt Flame Push Button Widget v2.1

    button_name: text displayed on button [str]
    button_checked: True or False [bool]
    connect: execute when button is pressed [function]
    button_width: (optional) default is 150. [int]

    Usage:
        pushbutton = FlamePushButton('Button Name', False)
    """
    def __init__(self, button_name, button_checked, connect=None, button_width=150):
        super().__init__()

        self.setText(button_name)
        self.setCheckable(True)
        self.setChecked(button_checked)
        self.setMinimumSize(button_width, 28)
        self.setMaximumSize(button_width, 28)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.clicked.connect(connect)  # produces error on 2021.1
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(44, 54, 68));
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(44, 54, 68));
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(44, 54, 68));
                border-left: 1px solid rgb(58, 58, 58);
                border-right: 1px solid rgb(44, 54, 68);
                padding-left: 5px; font: 14px 'Discreet'}
            QPushButton:checked {
                color: rgb(217, 217, 217);
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(71, 71, 71),
                    stop: .94 rgb(50, 101, 173));
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(71, 71, 71),
                    stop: .94 rgb(50, 101, 173));
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(71, 71, 71),
                    stop: .94 rgb(50, 101, 173));
                border-left: 1px solid rgb(71, 71, 71);
                border-right: 1px solid rgb(50, 101, 173);
                padding-left: 5px;
                font: italic}
            QPushButton:hover {
                border: 1px solid rgb(90, 90, 90)}
            QPushButton:disabled {
                color: #6a6a6a;
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(50, 50, 50));
                font: light;
                border: none}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")


class FlamePushButtonMenu(QtWidgets.QPushButton):
    """Custom Qt Flame Menu Push Button Widget v3.1

    button_name: text displayed on button [str]
    menu_options: list of options show when button is pressed [list]
    menu_width: (optional) width of widget. default is 150. [int]
    max_menu_width: (optional) set maximum width of widget. default is 2000. [int]
    menu_action: (optional) execute when button is changed. [function]

    Usage:
        push_button_menu_options = ['Item 1', 'Item 2', 'Item 3', 'Item 4']
        menu_push_button = FlamePushButtonMenu(
            'push_button_name', push_button_menu_options)

        or

        push_button_menu_options = ['Item 1', 'Item 2', 'Item 3', 'Item 4']
        menu_push_button = FlamePushButtonMenu(
            push_button_menu_options[0], push_button_menu_options)

    Notes:
        Started as v2.1
        v3.1 adds a functionionality to set the width of the menu to be the same as the
        button.
    """
    def __init__(self, button_name, menu_options, menu_width=240, max_menu_width=2000,
                 menu_action=None):
        super().__init__()

        self.button_name = button_name
        self.menu_options = menu_options
        self.menu_action = menu_action

        self.setText(button_name)
        self.setMinimumHeight(28)
        self.setMinimumWidth(menu_width)
        self.setMaximumWidth(max_menu_width)  # is max necessary?
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none;
                font: 14px 'Discreet';
                padding-left: 9px;
                text-align: left}
            QPushButton:disabled {
                color: rgb(116, 116, 116);
                background-color: rgb(45, 55, 68);
                border: none}
            QPushButton:hover {
                border: 1px solid rgb(90, 90, 90)}
            QPushButton::menu-indicator {image: none}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")

        # Menu
        def match_width():
            """Match menu width to the parent push button width."""
            self.pushbutton_menu.setMinimumWidth(self.size().width())

        self.pushbutton_menu = QtWidgets.QMenu(self)
        self.pushbutton_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushbutton_menu.aboutToShow.connect(match_width)
        self.pushbutton_menu.setStyleSheet("""
            QMenu {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none; font: 14px 'Discreet'}
            QMenu::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(58, 69, 81)}""")

        self.populate_menu(menu_options)
        self.setMenu(self.pushbutton_menu)

    def create_menu(self, option, menu_action):
        """Create menu item."""
        self.setText(option)

        if menu_action:
            menu_action()

    def populate_menu(self, options):
        """Empty the menu then reassemble the options."""
        self.pushbutton_menu.clear()

        for option in options:
            self.pushbutton_menu.addAction(
                option, partial(self.create_menu, option, self.menu_action))


class FlameMessageWindow(QtWidgets.QDialog):
    """Custom Qt Flame Message Window v2.1

    message_title: text shown in top left of window ie. Confirm Operation [str]
    message_type: confirm, message, error, warning [str] confirm and warning return True
                  or False values
    message: text displayed in body of window [str]
    parent: optional - parent window [object]

    Message Window Types:
        confirm: confirm and cancel button / grey left bar - returns True or False
        message: ok button / blue left bar
        error: ok button / yellow left bar
        warning: confirm and cancel button / red left bar - returns True of False

    Usage:
        FlameMessageWindow('Error', 'error', 'some important message')

        or

        if FlameMessageWindow(
            'Confirm Operation', 'confirm', 'some important message', window):
                do something
    """
    def __init__(self, message_title, message_type, message, parent=None):
        super().__init__()

        self.message_type = message_type

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(QtCore.QSize(500, 330))
        self.setMaximumSize(QtCore.QSize(500, 330))
        self.setStyleSheet('background-color: rgb(36, 36, 36)')

        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

        self.setParent(parent)

        self.grid = QtWidgets.QGridLayout()

        self.main_label = FlameLabel(message_title, 'normal', label_width=500)
        self.main_label.setStyleSheet("""
            color: rgb(154, 154, 154);
            font: 18px 'Discreet'""")

        self.message_text_edit = QtWidgets.QTextEdit(message)
        self.message_text_edit.setDisabled(True)
        self.message_text_edit.setStyleSheet("""
            QTextEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(36, 36, 36);
                selection-color: rgb(190, 190, 190);
                selection-background-color: rgb(36, 36, 36);
                border: none;
                padding-left: 20px;
                padding-right: 20px;
                font: 12px 'Discreet'}""")

        if message_type in ('confirm', 'warning'):
            self.confirm_button = FlameButton(
                'Confirm', self.confirm, button_color='blue', button_width=110)
            self.cancel_button = FlameButton('Cancel', self.cancel, button_width=110)

            self.grid.addWidget(self.main_label, 0, 0)
            self.grid.setRowMinimumHeight(1, 30)
            self.grid.addWidget(self.message_text_edit, 2, 0, 4, 8)
            self.grid.setRowMinimumHeight(9, 30)
            self.grid.addWidget(self.cancel_button, 10, 5)
            self.grid.addWidget(self.confirm_button, 10, 6)
            self.grid.setRowMinimumHeight(11, 30)
        else:
            self.ok_button = FlameButton(
                'Ok', self.confirm, button_color='blue', button_width=110)

            self.grid.addWidget(self.main_label, 0, 0)
            self.grid.setRowMinimumHeight(1, 30)
            self.grid.addWidget(self.message_text_edit, 2, 0, 4, 8)
            self.grid.setRowMinimumHeight(9, 30)
            self.grid.addWidget(self.ok_button, 10, 6)
            self.grid.setRowMinimumHeight(11, 30)

        # Why stripping these?
        message = message.replace('<br>', '')
        message = message.replace('<center>', '')
        message = message.replace('<dd>', '')

        self.setLayout(self.grid)
        self.show()
        self.exec_()

    def __bool__(self):
        return self.confirmed

    def cancel(self):
        self.close()
        self.confirmed = False

    def confirm(self):
        self.close()
        self.confirmed = True

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self.message_type == 'confirm':
            line_color = QtGui.QColor(71, 71, 71)
        elif self.message_type == 'message':
            line_color = QtGui.QColor(0, 110, 176)
        elif self.message_type == 'error':
            line_color = QtGui.QColor(200, 172, 30)
        elif self.message_type == 'warning':
            line_color = QtGui.QColor(200, 29, 29)

        painter.setPen(QtGui.QPen(line_color, 6, QtCore.Qt.SolidLine))
        painter.drawLine(0, 0, 0, 330)

        painter.setPen(QtGui.QPen(QtGui.QColor(71, 71, 71), .5, QtCore.Qt.SolidLine))
        painter.drawLine(0, 40, 500, 40)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):

        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()
        except:
            pass


class FlameTokenPushButton(QtWidgets.QPushButton):
    """Custom Qt Flame Token Push Button Widget v2.1

    button_name: Text displayed on button [str]
    token_dict: Dictionary defining tokens. {'Token Name': '<Token>'} [dict]
    token_dest: LineEdit that token will be applied to [object]
    button_width: (optional) default is 150 [int]
    button_max_width: (optional) default is 300 [int]

    Usage:
        token_dict = {'Token 1': '<Token1>', 'Token2': '<Token2>'}
        token_push_button = FlameTokenPushButton('Add Token', token_dict, token_dest)
    """
    def __init__(self, button_name, token_dict, token_dest, button_width=110,
                 button_max_width=300):
        super().__init__()

        self.setText(button_name)
        self.setMinimumHeight(28)
        self.setMinimumWidth(button_width)
        self.setMaximumWidth(button_max_width)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none;
                font: 14px 'Discreet';
                padding-left: 6px;
                text-align: left}
            QPushButton:hover {
                border: 1px solid rgb(90, 90, 90)}
            QPushButton:disabled {
                color: rgb(106, 106, 106);
                background-color: rgb(45, 55, 68);
                border: none}
            QPushButton::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: center right}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")

        def token_action_menu():

            def insert_token(token):
                for key, value in token_dict.items():
                    if key == token:
                        token_name = value
                        token_dest.insert(token_name)

            # the lambda sorts aAbBcC instead of ABCabc
            for key, value in sorted(token_dict.items(), key=lambda v: v[0].upper()):
                del value
                token_menu.addAction(key, partial(insert_token, key))

        token_menu = QtWidgets.QMenu(self)
        token_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        token_menu.setStyleSheet("""
            QMenu {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none; font: 14px 'Discreet'}
            QMenu::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(58, 69, 81)}""")

        self.setMenu(token_menu)
        token_action_menu()


class ContinueFolder:
    """Creates a new folder on the Desktop or in the Media Hub using tokens.

    Currently, the only special token is {version} which will look for a number sequence
    and return the next number in the sequence. All of the other tokens are standard
    things like: day, hour, minute.
    """
    def __init__(self, path):

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.path = path

        # New folder destinations
        self.destinations = [
            'Desktop Reel',
            'Desktop Reel && Media Hub',  # double & to cancel QShortcut
            'Media Hub']

        # Load presets
        self.presets_xml = os.path.join(
            os.path.dirname(__file__), 'continue_folder.xml')
        self.presets_xml_tree = ''
        self.presets_xml_root = ''
        self.load_presets()

        # Generate dict containing token names, shorthand, and values
        self.now = dt.datetime.now()
        self.tokens = {}
        self.generate_tokens()

        # Translate the token pattern to a regex
        self.pattern = ''
        self.load_pattern()

        # Translate the token pattern to a regex
        self.pattern_regex = ''
        self.generate_pattern_regex()

        # Find folders that match the regex
        self.folders = []
        self.find_folders()

        # Extract version token from the found folders
        self.version_padding = 0
        self.update_version_token()

        # Replace tokens to generate new folder name
        self.folder_new = ''
        self.resolve_tokens()

        # Starting Dimensions
        self.window_x = 900
        self.window_y = 130
        self.save_window_x = 500
        self.save_window_y = 100

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    def load_presets(self):
        """Load preset file if preset and store XML tree & root."""
        if os.path.isfile(self.presets_xml):
            self.presets_xml_tree = ETree.parse(self.presets_xml)
        else:
            default = """<continue_folder_presets></continue_folder_presets>"""
            self.presets_xml_tree = ETree.ElementTree(ETree.fromstring(default))

        self.presets_xml_root = self.presets_xml_tree.getroot()

    def generate_tokens(self):
        """Generate dictionary of tokens with a list for each.

        Each item has a list with the shorthand token, a token regex, a pattern regex
        and then the value.

        {name : [ token, token_regex, pattern_regex, value ], ...}

        name = full name of the token
        token = this is the shorthand used in the pattern. ie, {token}
        token_regex = optional regex to assist in generating the pattern regex.  only
            necessary on tokens that take optional modifiers, ie. {version###}
        pattern_regex = regex to extract the token data from the folder name
        value = starting value
        """
        self.tokens = {
            'am/pm':
                ['{pp}', None, '[a-z]{2}', self.now.strftime('%p').lower()],
            'AM/PM':
                ['{PP}', None, '[A-Z]{2}', self.now.strftime('%p').upper()],
            'Day':
                ['{DD}', None, '[0-9]{2}', self.now.strftime('%d')],
            'Hour (12hr)':
                ['{hh}', None, '[0-9]{2}', self.now.strftime('%I')],
            'Hour (24hr)':
                ['{HH}', None, '[0-9]{2}', self.now.strftime('%H')],
            'Minute':
                ['{mm}', None, '[0-9]{2}', self.now.strftime('%M')],
            'Month':
                ['{MM}', None, '[0-9]{2}', self.now.strftime('%m')],
            'Version':
                # the regex for Version is a named capture group excluding zero padding
                ['{version}', '{version#*}', '0*(?P<version>[1-9][0-9]*)', '1'],
            'Year (##)':
                ['{YY}', None, '[0-9]{2}', self.now.strftime('%y')],
            'Year (####)':
                ['{YYYY}', None, '[0-9]{4}', self.now.strftime('%Y')]}

    @staticmethod
    def capture_tokens(regex, folder):
        """Capture tokens using regex.

        Args:
            regex (str): regex that match tokens wrapped in curly braces
            folder (str): folder name to be tested

        Returns:
            Regex match object
        """
        try:
            result = re.match(regex, folder)
        except re.error:  # for example, a situation where {version} is passed twice
            result = None

        return result

    def load_pattern(self):
        """Load the first preset's pattern or use the default pattern."""
        if self.presets_xml_root.findall('preset'):
            # load pattern for first element in list of presets
            self.pattern = self.presets_xml_root.findall(
                'preset')[0].find('pattern').text
        else:
            self.pattern = '{version}'

    def generate_pattern_regex(self):
        """Generate a regex based on the token pattern.

        This regex will be used to find matching folders.  Use the token regex if
        available otherwise just token.

        for example, {YYYY}_{MM}_{DD} would become [0-9]{4}_[0-9]{2}_[0-9]{2}
        """
        self.pattern_regex = self.pattern

        for token, values in self.tokens.items():
            del token
            if values[1]:  # token regex available
                self.pattern_regex = re.sub(values[1], values[2], self.pattern_regex)
            else:
                self.pattern_regex = re.sub(values[0], values[2], self.pattern_regex)

    def find_folders(self):
        """Appends tuples to self.folders list.

        The tuples contain the folder name, and then the version number if present.
        """
        # Always clear the list before searching again with new regex
        self.folders = []

        for folder in next(os.walk(self.path))[1]:
            search = self.capture_tokens(self.pattern_regex, folder)

            # append tuples containing matching folder name(str) and version(int)
            match = []

            # folder name match
            if search:  # re returns match object or None
                match.append(search.group(0))

                # version token match
                # version must be integer because strings would sort as 1, 10, 11, 9
                if len(search.groups()) == 1:  # groups only returns named groups
                    match.append(int(search.group(1)))

                self.folders.append(tuple(match))

    def update_version_token(self):
        """Scan folders that matched the pattern regex to find if a version is present.

        If so, find the highest version number and set value in self.tokens to be one
        higher.
        """

        def find_version_padding():
            """Find if the version number is padded with zeroes."""
            # find hashes preceeded by {version and trailed by }
            # using re.match starts searching from beginning of a string so
            # ?:.* is a non-capturing group for anything preceeding {version
            search = '(?:.*{version)(?P<padding>#*)}'

            result = self.capture_tokens(search, self.pattern)

            if result:
                self.version_padding = len(result.group(1))
            else:
                self.version_padding = 0

        find_version_padding()

        try:
            # sort self.folders by the second value in each set
            self.folders.sort(key=lambda item: item[1])
            version = self.folders[-1][1] + 1
        except IndexError:  # if there no folders with version matches
            version = 1

        self.tokens['Version'][3] = str(version).zfill(self.version_padding)

    def resolve_tokens(self):
        """Replace tokens with values."""
        self.folder_new = self.pattern

        for token, values in self.tokens.items():
            del token
            if values[1]:  # token regex available
                self.folder_new = re.sub(values[1], values[3], self.folder_new)
            else:
                self.folder_new = re.sub(values[0], values[3], self.folder_new)

    def create_desktop_reel(self):
        """Create reel on bottom of the current desktop.

        This will start a folder sequence or continue an existing folder sequence.
        """
        desktop = flame.project.current_project.current_workspace.desktop
        # create_real will not take utf-8, only ascii
        desktop.reel_groups[0].create_reel(self.folder_new.encode('ascii', 'ignore'))
        self.message('Reel created!')

    def create_media_hub_folder(self):
        """Create folder in Media Hub.

        This will start a folder sequence or continue the existing folder sequence.
        """
        os.mkdir(os.path.join(self.path, self.folder_new))
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        self.message('MediaHub folder created!')

    def save_preset_window(self):
        """Smaller window with save dialog."""

        def duplicate_check():
            """Check that preset to be saved would not be a duplicate."""
            duplicate = False
            preset_name = self.line_edit_preset_name.text()

            for preset in self.presets_xml_root.findall('preset'):
                if preset.get('name') == preset_name:
                    duplicate = True

            return duplicate

        def save_preset():
            """Save new preset to XML file."""
            new_preset = ETree.Element('preset', name=self.line_edit_preset_name.text())
            new_pattern = ETree.SubElement(new_preset, 'pattern')
            new_pattern.text = self.line_edit_preset_pattern.text()

            self.presets_xml_root.append(new_preset)
            sort_presets()

            try:
                self.presets_xml_tree.write(self.presets_xml)

                self.message(f'{self.line_edit_preset_name.text()} preset saved to ' +
                             f'{self.presets_xml}')
            except OSError:
                FlameMessageWindow(
                    'Error', 'error',
                    f'Check permissions on {os.path.dirname(__file__)}')

        def overwrite_preset():
            """Replace pattern in presets XML tree then save to XML file."""
            preset_name = self.line_edit_preset_name.text()

            for preset in self.presets_xml_root.findall('preset'):
                if preset.get('name') == preset_name:
                    preset.find('pattern').text = self.line_edit_preset_pattern.text()

            try:
                self.presets_xml_tree.write(self.presets_xml)

                self.message(f'{self.line_edit_preset_name.text()} preset saved to ' +
                             f'{self.presets_xml}')
            except OSError:
                FlameMessageWindow(
                    'Error', 'error',
                    f'Check permissions on {os.path.dirname(__file__)}')

        def sort_presets():
            """Alphabetically sort presets by name attribute."""
            self.presets_xml_root[:] = sorted(
                self.presets_xml_root,
                key=lambda child: (child.tag, child.get('name')))

        def save_button():
            """Triggered when the Save button at the bottom is pressed."""
            duplicate = duplicate_check()

            if duplicate:
                if FlameMessageWindow(
                        'Overwrite Existing Preset', 'confirm', 'Are you '
                        + 'sure want to permanently overwrite this preset?' + '<br/>'
                        + 'This operation cannot be undone.'):
                    overwrite_preset()
                    self.btn_preset.populate_menu(
                        [preset.get('name') for preset in
                         self.presets_xml_root.findall('preset')])
                    self.btn_preset.setText(self.line_edit_preset_name.text())
                    self.save_window.close()

            if not duplicate:
                save_preset()
                self.btn_preset.populate_menu(
                    [preset.get('name') for preset in
                     self.presets_xml_root.findall('preset')])
                self.btn_preset.setText(self.line_edit_preset_name.text())
                self.save_window.close()

        def cancel_button():
            """Triggered when the Cancel button at the bottom is pressed."""
            self.save_window.close()

        self.save_window = QtWidgets.QWidget()

        self.save_window.setMinimumSize(self.save_window_x, self.save_window_y)

        self.save_window.setStyleSheet('background-color: #272727')
        self.save_window.setWindowTitle('Save Preset As...')

        # Center Window
        resolution = QtWidgets.QDesktopWidget().screenGeometry()

        self.save_window.move(
            (resolution.width() / 2) - (self.save_window_x / 2),
            (resolution.height() / 2) - (self.save_window_y / 2 + 44))

        # Labels
        self.label_preset_name = FlameLabel('Preset Name', 'normal')
        self.label_preset_pattern = FlameLabel('Pattern', 'normal')

        # Line Edits
        self.line_edit_preset_name = FlameLineEdit(self.pattern)
        self.line_edit_preset_pattern = FlameLineEdit(self.pattern)

        # Buttons
        self.save_btn_save = FlameButton(
            'Save', save_button, button_color='blue', button_width=110)
        self.save_btn_cancel = FlameButton('Cancel', cancel_button, button_width=110)

        # Layout
        self.save_grid1 = QtWidgets.QGridLayout()
        self.save_grid1.setVerticalSpacing(10)
        self.save_grid1.setHorizontalSpacing(10)
        self.save_grid1.addWidget(self.label_preset_name, 0, 0)
        self.save_grid1.addWidget(self.line_edit_preset_name, 0, 1)
        self.save_grid1.addWidget(self.label_preset_pattern, 1, 0)
        self.save_grid1.addWidget(self.line_edit_preset_pattern, 1, 1)

        self.save_hbox01 = QtWidgets.QHBoxLayout()
        self.save_hbox01.addStretch(1)
        self.save_hbox01.addWidget(self.save_btn_cancel)
        self.save_hbox01.addWidget(self.save_btn_save)

        self.save_vbox = QtWidgets.QVBoxLayout()
        self.save_vbox.setMargin(20)
        self.save_vbox.addLayout(self.save_grid1)
        self.save_vbox.addSpacing(20)
        self.save_vbox.addLayout(self.save_hbox01)

        self.save_window.setLayout(self.save_vbox)

        self.save_window.show()

        return self.window

    def main_window(self):
        """The main GUI window."""
        def get_selected_preset():
            """Get preset that should be displayed or return empty string."""
            try:
                selected_preset = self.presets_xml_root.findall('preset')[0].get('name')
            except IndexError:  # if findall() returns empty list
                selected_preset = ''

            return selected_preset

        def get_preset_names():
            """Return just the names of the presets."""
            try:
                preset_names = [
                    preset.get('name') for preset in
                    self.presets_xml_root.findall('preset')]
            except IndexError:  # if findall() returns empty list
                preset_names = []

            return preset_names

        def update_folder():
            """Update folder when pattern is changed."""
            self.pattern = self.line_edit_pattern.text()
            self.generate_pattern_regex()
            self.find_folders()
            self.update_version_token()
            self.resolve_tokens()
            self.line_edit_folder.setText(self.folder_new)

        def update_pattern():
            """Update pattern when preset is changed."""
            preset_name = self.btn_preset.text()

            if preset_name:  # might be empty str if all presets were deleted
                for preset in self.presets_xml_root.findall('preset'):
                    if preset.get('name') == preset_name:
                        self.line_edit_pattern.setText(preset.find('pattern').text)
                        break  # should not be any duplicates

        def preset_delete_button():
            """Triggered when the Delete button on the Preset line is pressed."""
            if FlameMessageWindow(
                    'Confirm Operation', 'confirm', 'Are you sure want to'
                    + ' permanently delete this preset?' + '<br/>' + 'This operation'
                    + ' cannot be undone.'):
                preset_name = self.btn_preset.text()

                for preset in self.presets_xml_root.findall('preset'):
                    if preset.get('name') == preset_name:
                        self.presets_xml_root.remove(preset)
                        self.message(
                            f'{preset_name} preset deleted from {self.presets_xml}')

                self.presets_xml_tree.write(self.presets_xml)

            # Reload presets button
            self.load_presets()
            self.btn_preset.populate_menu(get_preset_names())
            self.btn_preset.setText(get_selected_preset())
            update_pattern()

        def preset_save_button():
            """Triggered when the Save button the Presets line is pressed."""
            self.save_preset_window()

        def okay_button():
            """Triggered when the Okay button at the bottom is pressed."""
            if self.btn_destination_reel.isChecked():  # Desktop Reel
                self.create_desktop_reel()
            if self.btn_destination_folder.isChecked():  # Media Hub
                self.create_media_hub_folder()

            self.message('Done!')
            self.window.close()

        def cancel_button():
            """Triggered when the Cancel button at the bottom is pressed."""
            self.message('Cancelled!')
            self.window.close()

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(self.window_x, self.window_y)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Center Window
        resolution = QtWidgets.QDesktopWidget().screenGeometry()

        self.window.move(
                (resolution.width() / 2) - (self.window_x / 2),
                (resolution.height() / 2) - (self.window_y / 2 + 44))

        # Labels
        self.label_preset = FlameLabel('Preset', 'normal')
        self.label_pattern = FlameLabel('Pattern', 'normal')
        self.label_folder = FlameLabel('New Folder', 'normal')
        self.label_destination = FlameLabel('Destination', 'normal')

        # Lines
        self.line_edit_pattern = FlameLineEdit(self.pattern)
        self.line_edit_pattern.textChanged.connect(update_folder)
        self.line_edit_folder = FlameLabel(self.folder_new, 'background')

        # Buttons
        self.btn_preset = FlamePushButtonMenu(
            get_selected_preset(), get_preset_names(), menu_action=update_pattern)
        self.btn_preset.setMaximumSize(QtCore.QSize(4000, 28))  # span over to Save btn

        self.btn_preset_save = FlameButton('Save', preset_save_button, button_width=110)
        self.btn_preset_delete = FlameButton(
            'Delete', preset_delete_button, button_width=110)
        self.btn_tokens = FlameTokenPushButton(
            'Add Token',
            # self.tokens is a dict with a nested set for each key
            # FlameTokenPushButton wants a dict that is only {token_name: token}
            # so need to simplify it with a dict comprehension
            {key: values[0] for key, values in self.tokens.items()},
            self.line_edit_pattern)
        self.btn_ok = FlameButton(
            'Ok', okay_button, button_color='blue', button_width=110)

        self.btn_cancel = FlameButton('Cancel', cancel_button, button_width=110)

        self.btn_destination_reel = FlamePushButton('Desktop Reel', True)
        self.btn_destination_folder = FlamePushButton('MediaHub Folder', False)

        # Layout
        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addWidget(self.btn_destination_reel)
        self.hbox1.addWidget(self.btn_destination_folder)
        self.hbox1.addStretch()

        self.grid1 = QtWidgets.QGridLayout()
        self.grid1.setVerticalSpacing(10)
        self.grid1.setHorizontalSpacing(10)
        self.grid1.addWidget(self.label_preset, 0, 0)
        self.grid1.addWidget(self.btn_preset, 0, 1)
        self.grid1.addWidget(self.btn_preset_save, 0, 2)
        self.grid1.addWidget(self.btn_preset_delete, 0, 3)
        self.grid1.addWidget(self.label_pattern, 1, 0)
        self.grid1.addWidget(self.line_edit_pattern, 1, 1)
        self.grid1.addWidget(self.btn_tokens, 1, 2)
        self.grid1.addWidget(self.label_folder, 2, 0)
        self.grid1.addWidget(self.line_edit_folder, 2, 1)
        self.grid1.addWidget(self.label_destination, 3, 0)
        self.grid1.addLayout(self.hbox1, 3, 1)

        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(self.btn_cancel)
        self.hbox2.addWidget(self.btn_ok)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setMargin(20)
        self.vbox.addLayout(self.grid1)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox2)

        self.window.setLayout(self.vbox)

        self.window.show()

        return self.window


def process_selection(selection):
    """Execute script on all selected folders in MediaHub."""
    for folder in selection:
        ContinueFolder(folder.path)


def scope_folders(selection):
    """Determine if selection is a folder in the MediaHub > Files tab."""
    return any(isinstance(item, flame.PyMediaHubFilesFolder) for item in selection)


def get_mediahub_files_custom_ui_actions():
    """Add right click menu items."""
    return [{'name': 'Create...',
             'actions': [{'name': 'Continue Folder',
                          'isVisible': scope_folders,
                          'execute': process_selection,
                          'minimumVersion': '2022'}]
            }]
