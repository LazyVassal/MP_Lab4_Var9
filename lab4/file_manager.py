import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import shutil
import sqlite3
from datetime import datetime

# --- Модель: Работа с базой данных SQLite ---
class HistoryDB:
    def __init__(self, db_name='history.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT,
                        path TEXT,
                        timestamp TEXT)''')
        self.conn.commit()

    def log_action(self, action, path):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO history (action, path, timestamp) VALUES (?, ?, ?)",
                       (action, path, timestamp))
        self.conn.commit()

    def get_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT action, path, timestamp FROM history ORDER BY timestamp DESC LIMIT 20")
        return cursor.fetchall()

    def close(self):
        self.conn.close()

# --- Контроллер и Представление (GUI) ---
class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Простой Файловый Менеджер")
        self.current_path = os.path.expanduser("~") # Начальный путь - домашняя директория

        # Инициализация БД
        self.db = HistoryDB()

        self.create_widgets()
        self.update_file_list()

    def create_widgets(self):
        # --- Меню ---
        menubar = tk.Menu(self.root)
        
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Открыть папку", command=self.open_directory)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=helpmenu)
        
        self.root.config(menu=menubar)

        # --- Виджет 1: Панель пути (Entry + Button) ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5, fill='x')

        self.path_var = tk.StringVar(value=self.current_path)
        
        self.path_entry = tk.Entry(top_frame, textvariable=self.path_var, width=80)
        self.path_entry.pack(side='left', expand=True, fill='x', padx=5)
        
        go_btn = tk.Button(top_frame, text="Перейти", command=self.open_directory)
        go_btn.pack(side='left', padx=2)

        # --- Виджет 2: Список файлов (Listbox) ---
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=5, fill='both', expand=True)
        
        self.file_listbox = tk.Listbox(list_frame, width=100, height=25)
        self.file_listbox.pack(side='left', fill='both', expand=True)
        
        # Полоса прокрутки для Listbox
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Привязка события (двойной клик)
        self.file_listbox.bind("<Double-Button-1>", self.on_double_click)

         # --- Виджет 3: Кнопки действий (Frame с Buttons) ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5, fill='x')

        open_btn = tk.Button(btn_frame, text="Открыть", command=self.open_selected_item)
        open_btn.grid(row=0, column=0, padx=2, pady=2)

        new_folder_btn = tk.Button(btn_frame, text="Новая папка", command=self.create_new_folder)
        new_folder_btn.grid(row=0, column=1, padx=2, pady=2)

    def update_file_list(self):
        """Обновление списка файлов в Listbox"""
        self.file_listbox.delete(0, tk.END)
        
        try:
            items = os.listdir(self.current_path)
            # Отображаем папки первыми
            dirs = sorted([d for d in items if os.path.isdir(os.path.join(self.current_path, d))])
            files = sorted([f for f in items if os.path.isfile(os.path.join(self.current_path, f))])
            
            for d in dirs:
                self.file_listbox.insert(tk.END, f"[ПАПКА] {d}")
            for f in files:
                self.file_listbox.insert(tk.END, f)
                
            self.path_var.set(self.current_path) # Обновляем путь в Entry
            
            # Логируем действие просмотра
            self.db.log_action("Просмотр каталога", self.current_path)
            
            # Добавляем команды в контекстное меню
            self.setup_context_menu()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")
            return False

    def open_directory(self):
        """Обработка нажатия кнопки 'Перейти'"""
        new_path = self.path_entry.get()
        
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.update_file_list()
            self.db.log_action("Переход в каталог", new_path)
            
    def on_double_click(self, event):
        """Обработка двойного клика по элементу"""
        selection = self.file_listbox.curselection()
        
        if selection:
            item_name = self.file_listbox.get(selection).replace('[ПАПКА] ', '')
            full_path = os.path.join(self.current_path, item_name)
            
            if os.path.isdir(full_path):
                self.current_path = full_path
                self.update_file_list()
                self.db.log_action("Переход в каталог", full_path)

    def open_selected_item(self):
        """Обработка нажатия кнопки 'Открыть'"""
        selection = self.file_listbox.curselection()
        if selection:
            item_name = self.file_listbox.get(selection).replace('[ПАПКА] ', '')
            full_path = os.path.join(self.current_path, item_name)
             
            if os.path.isdir(full_path):
                 self.current_path = full_path
                 self.update_file_list()
                 self.db.log_action("Переход в каталог", full_path)
            elif os.path.isfile(full_path):
                 try:
                     os.startfile(full_path) # Открывает файл стандартной программой
                     self.db.log_action("Открытие файла", full_path)
                 except Exception as e:
                     messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def create_new_folder(self):
         """Создание новой папки"""
         folder_name = simpledialog.askstring("Новая папка", "Введите имя новой папки:")
         
         if folder_name:
             new_path = os.path.join(self.current_path, folder_name)
             try:
                 os.mkdir(new_path)
                 messagebox.showinfo("Успех", "Папка создана.")
                 self.update_file_list() # Обновляем список
                 self.db.log_action("Создание папки", new_path)
             except Exception as e:
                 messagebox.showerror("Ошибка", f"Не удалось создать папку: {e}")

    def setup_context_menu(self):
         """Создание контекстного меню (правый клик)"""
         try:
             # Удаляем старое меню, если было
             self.file_listbox.context_menu.destroy()
         except AttributeError:
             pass

         self.file_listbox.context_menu = tk.Menu(self.root, tearoff=0)
         
         # Команды меню (добавляются динамически при правом клике)
         def do_copy():
             self.do_operation("copy")
         
         def do_move():
             self.do_operation("move")
         
         def do_delete():
             selection = self.file_listbox.curselection()
             if selection:
                 item_name = self.file_listbox.get(selection).replace('[ПАПКА] ', '')
                 full_path = os.path.join(self.current_path, item_name)
                 
                 if messagebox.askyesno("Удаление", f"Удалить '{item_name}'?"):
                     try:
                         if os.path.isfile(full_path):
                             os.remove(full_path)
                             action = "Удаление файла"
                         else:
                             shutil.rmtree(full_path) # Удаляем непустую папку
                             action = "Удаление папки"
                         
                         messagebox.showinfo("Успех", "Объект удален.")
                         self.update_file_list()
                         self.db.log_action(action, full_path)
                     except Exception as e:
                         messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")
         
         # Добавляем команды в меню
         self.file_listbox.context_menu.add_command(label="Копировать", command=do_copy)
         self.file_listbox.context_menu.add_command(label="Переместить", command=do_move)
         self.file_listbox.context_menu.add_command(label="Удалить", command=do_delete)
         
         # Показываем меню при правом клике
         def popup(event):
             # Показываем меню только если клик был по элементу списка
             if self.file_listbox.curselection():
                 try:
                     self.file_listbox.context_menu.tk_popup(event.x_root, event.y_root)
                 finally:
                     self.file_listbox.context_menu.grab_release()
         
         # Привязываем событие правого клика
         self.file_listbox.bind("<Button-3>", popup) # Button-3 это правая кнопка мыши

    def do_operation(self, operation_type):
         """Логика копирования/перемещения"""
         selection = self.file_listbox.curselection()
         if selection:
             item_name = self.file_listbox.get(selection).replace('[ПАПКА] ', '')
             source_path = os.path.join(self.current_path, item_name)
             
             dest_dir = filedialog.askdirectory(title=f"Выберите папку для {operation_type}")
             
             if dest_dir:
                 dest_path = os.path.join(dest_dir, item_name)
                 
                 try:
                     if operation_type == "copy":
                         if os.path.isdir(source_path):
                             shutil.copytree(source_path, dest_path)
                         else:
                             shutil.copy2(source_path, dest_path) # copy2 сохраняет метаданные
                         action_text = "Копирование"
                         
                     elif operation_type == "move":
                         shutil.move(source_path, dest_path)
                         action_text = "Перемещение"
                         
                     messagebox.showinfo("Успех", "Операция выполнена.")
                     # Если мы переместили файл в текущей папке, обновим список
                     if os.path.dirname(source_path) == self.current_path:
                         self.update_file_list()
                         
                     self.db.log_action(f"{action_text} объекта", f"Из: {source_path} В: {dest_path}")
                     
                 except Exception as e:
                     messagebox.showerror("Ошибка", f"Не удалось выполнить операцию: {e}")
                     
    def show_about(self):
         messagebox.showinfo("О программе", "Простой файловый менеджер\nВерсия 1.0\n\nИспользует tkinter и sqlite3.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()