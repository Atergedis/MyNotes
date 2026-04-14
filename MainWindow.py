import sys
import json
import os
from pathlib import Path
from note import Note
from NotesStorage import NotesStorage

from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QMenuBar,
    QStatusBar,
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
)

from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QFont,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.storage = NotesStorage()
        self.current_note = None
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_current_note)
        self.setWindowTitle("My Notes")
        self.setGeometry(100, 100, 900, 600)
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.refresh_notes_list()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 12, 12, 12)       
        title_label = QLabel("Notes")
        title_label.setObjectName("panelTitle")
        header_layout.addWidget(title_label)   
        header_layout.addStretch()
        new_btn = QPushButton("+ New Note")
        new_btn.setObjectName("newNoteButton")
        new_btn.clicked.connect(self.create_new_note)
        header_layout.addWidget(new_btn)
        left_layout.addWidget(header_widget)
        self.notes_list = QListWidget()
        self.notes_list.setObjectName("notesList")
        self.notes_list.itemClicked.connect(self.on_note_selected)
        left_layout.addWidget(self.notes_list)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(10)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.title_input.setObjectName("titleInput")
        self.title_input.textChanged.connect(self.on_content_changed)
        right_layout.addWidget(self.title_input)
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.addStretch()
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.clicked.connect(self.delete_current_note)
        self.delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_btn)
        right_layout.addWidget(toolbar_widget)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Go to writing...")
        self.text_input.setObjectName("textInput")
        self.text_input.textChanged.connect(self.on_content_changed)
        right_layout.addWidget(self.text_input)
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([300, 600])
        main_layout.addWidget(self.splitter)

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        export_action = QAction("Export in JSON...", self)
        export_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_action.triggered.connect(self.export_notes)
        file_menu.addAction(export_action)
        import_action = QAction("Import from JSON...", self)
        import_action.setShortcut(QKeySequence("Ctrl+Shift+I"))
        import_action.triggered.connect(self.import_notes)
        file_menu.addAction(import_action)
        file_menu.addSeparator()
        exit_action = QAction("Entrance", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.count_label = QLabel()
        self.statusbar.addPermanentWidget(self.count_label)
        self.save_status_label = QLabel("Ready")
        self.statusbar.addWidget(self.save_status_label)
        self.update_statusbar()

    def update_statusbar(self):
        count = len(self.storage.notes)
        if count % 10 == 1 and count % 100 != 11:
            word = "note"
        elif 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
            word = "note"
        else:
            word = "note"

        self.count_label.setText(f"{count} {word}")
    
    def refresh_notes_list(self):
        self.notes_list.clear()
        
        for note in self.storage.notes:
            item = QListWidgetItem()
            title = note.title if note.title else "Not title"
            item.setText(title)
            item.setData(Qt.UserRole, note.id)
            preview = note.text[:50] + "..." if len(note.text) > 50 else note.text
            item.setToolTip(preview)
            self.notes_list.addItem(item)
    
    def create_new_note(self):
        new_note = Note(title="", text="")
        self.storage.add_note(new_note)
        self.refresh_notes_list()

        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.UserRole) == new_note.id:
                self.notes_list.setCurrentItem(item)
                break
        
        self.load_note_to_editor(new_note)
        self.title_input.setFocus()
        self.update_statusbar()
    
    def on_note_selected(self, item):
        note_id = item.data(Qt.UserRole)
        note = self.storage.get_note(note_id)
        
        if note:
            self.load_note_to_editor(note)
    
    def load_note_to_editor(self, note):
        self.current_note = note
        self.title_input.blockSignals(True)
        self.text_input.blockSignals(True)
        self.title_input.setText(note.title)
        self.text_input.setText(note.text)
        self.title_input.blockSignals(False)
        self.text_input.blockSignals(False)
        self.delete_btn.setEnabled(True)

        if note.updated_at:
            dt = datetime.fromisoformat(note.updated_at)
            date_str = dt.strftime("%d.%m.%Y %H:%M")
            self.save_status_label.setText(f"Changed: {date_str}")
    
    def on_content_changed(self):

        if not self.current_note:
            return

        self.save_timer.start(1000)
        self.save_status_label.setText("Saving...")
    
    def save_current_note(self):

        if not self.current_note:
            return

        self.current_note.update(
            title=self.title_input.text(),
            text=self.text_input.toPlainText()
        )

        if self.storage.save():
            self.refresh_notes_list()
            self.save_status_label.setText("Save")
            self.update_statusbar()
    
    def delete_current_note(self):

        if not self.current_note:
            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            note_id = self.current_note.id
            self.storage.delete_note(note_id)
            self.current_note = None
            self.title_input.clear()
            self.text_input.clear()
            self.delete_btn.setEnabled(False)
            self.refresh_notes_list()
            self.update_statusbar()
            self.save_status_label.setText("Ready")
    
    def export_notes(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export notes",
            str(Path.home() / f"notes_backup_{datetime.now().strftime('%Y%m%d')}.json"),
            "JSON files (*.json)"
        )
        
        if file_path:
            try:
                data = [note.to_dict() for note in self.storage.notes]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Success", f"Notes exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export notes:\n{e}")
    
    def import_notes(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importing notes",
            str(Path.home()),
            "JSON files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                reply = QMessageBox.question(
                    self,
                    "Import",
                    "Replace current notes with imported ones?\n"
                    "(Click 'No' to append to existing notes)",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Cancel:
                    return
                
                imported_notes = [Note.from_dict(note_data) for note_data in data]
                
                if reply == QMessageBox.Yes:
                    self.storage.notes = imported_notes
                else:
                    self.storage.notes = imported_notes + self.storage.notes
                
                self.storage.save()
                self.refresh_notes_list()
                self.update_statusbar()
                QMessageBox.information(self, "Success", f"Imported {len(imported_notes)} notes")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import notes:\n{e}")
    
    def apply_styles(self):
        self.setStyleSheet("""
            /* Основное окно */
            QMainWindow {
                background-color: #ffffff;
            }
            
            /* Заголовок панели */
            #panelTitle {
                font-size: 20px;
                font-weight: bold;
                color: #1a1a1a;
            }
            
            /* Кнопка новой заметки */
            #newNoteButton {
                background-color: #808080;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            
            #newNoteButton:hover {
                background-color: #666666;
            }
            
            /* Список заметок */
            #notesList {
                background-color: #f5f5f5;
                border: none;
                outline: none;
            }
            
            #notesList::item {
                padding: 12px;
                margin: 2px 8px;
                background-color: white;
                border: 1px solid #d4d4d4;
                border-radius: 6px;
            }
            
            #notesList::item:hover {
                background-color: #e8e8e8;
            }
            
            #notesList::item:selected {
                background-color: #808080;
                color: white;
            }
            
            /* Поле заголовка */
            #titleInput {
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #d4d4d4;
                padding: 8px 0;
                background: transparent;
            }
            
            #titleInput:focus {
                border-bottom-color: #808080;
            }
            
            /* Поле текста */
            #textInput {
                border: none;
                background: transparent;
                font-size: 14px;
                line-height: 1.5;
            }
            
            /* Кнопка удаления */
            #deleteButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }
            
            #deleteButton:hover {
                background-color: #c82333;
            }
            
            /* Статус-бар */
            QStatusBar {
                background-color: #f5f5f5;
                color: #666666;
                border-top: 1px solid #d4d4d4;
            }
        """)