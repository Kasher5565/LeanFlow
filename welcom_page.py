import tkinter as tk
from tkinter import ttk
from Project_1STR import Registr
import requests
import json

class WelcomeApp:
    def __init__(self):
        self.root = tk.Tk() # делаем это окно главным
        self.root.title('LeanFlow') # название приложения при отображении окна
        self.root.configure(bg='#EADEBD') # цвет фона
        self.root.state('zoomed') # окно появляется на весь экран

        self.BACKEND_URL = "http://localhost:8000"  # URL FastAPI сервера

        # Цветовая палитра
        self.colors = {
            'beige': '#EADEBD',
            'saddle_brown': '#8B4513',
            'saddle_brown_hover': '#A0522D',
            'slate_gray': '#64748B',
            'white': '#FFFFFF'
        }

        self.create_widgets()

    def create_widgets(self):
        # Главный контейнер
        self.main_frame = tk.Frame(self.root, bg=self.colors['beige'])
        self.main_frame.pack(expand=True, fill='both')

        # Контейнер для центрирования текста
        self.text_frame = tk.Frame(self.main_frame, bg=self.colors['beige'])
        self.text_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Название приложения в центре страницы
        self.title_label = tk.Label(
            self.text_frame,
            text='LeanFlow',
            font=('Roboto', 48, 'bold'),
            fg=self.colors['saddle_brown'],
            bg=self.colors['beige']
        )
        self.title_label.pack(anchor="center") # Расположение в центре

        # Приветственная надпись
        self.welcome_label = tk.Label(
            self.text_frame,
            text='Добро пожаловать в приложение',
            font=('Roboto', 32),
            fg=self.colors['slate_gray'],
            bg=self.colors['beige']
        )
        self.welcome_label.pack(anchor='center')

        # Дополнительный текст
        self.subtitle_label = tk.Label(
            self.text_frame,
            text='Мы рады вас видеть!',
            font=('Roboto', 24),
            fg=self.colors['slate_gray'],
            bg=self.colors['beige']
        )
        self.subtitle_label.pack(anchor='center')

        # Кнопка
        self.button_frame = tk.Frame(self.main_frame, bg=self.colors['beige'])
        self.button_frame.pack(side='bottom', anchor='se', padx=20, pady=20)

        self.action_button = tk.Button(
            self.button_frame,
            text='Продолжить',
            font=('Roboto', 12),
            bg=self.colors['saddle_brown'],
            fg='white',
            activebackground=self.colors['saddle_brown'],
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=10, # отступы от раниц фрейма
            cursor='hand2',  # Изменение курсора при наведении
            command=self.next
        )
        self.action_button.pack()

        # Добавляем эффект изменения цвета при наведении
        self.action_button.bind('<Enter>', self.on_button_enter)
        self.action_button.bind('<Leave>', self.on_button_leave)

    def on_button_enter(self, event):
        """Эффект при наведении курсора на кнопку - меняем цвет на более светлый"""
        self.action_button.configure(bg=self.colors['saddle_brown_hover'])

    def on_button_leave(self, event):
        """Эффект при уходе курсора с кнопки - возвращаем исходный цвет"""
        self.action_button.configure(bg=self.colors['saddle_brown'])

    def next(self):
        self.root.withdraw()  # Скрываем текущее окно
        register_window = Registr()
        register_window.BACKEND_URL = self.BACKEND_URL
    
    def run(self):
        self.root.mainloop() # зацикливаем окно


# запуск приложения
if __name__ == '__main__':
    app = WelcomeApp()
    app.run()