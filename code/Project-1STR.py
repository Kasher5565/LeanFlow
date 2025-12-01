import tkinter as tk


class Registr:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('LeanFlow')
        self.root.configure(background='#F8FAFC')
        self.root.state('zoomed')

        self.colors = {
            'background': '#F8FAFC',
            'card_bg': '#FFFFFF',
            'primary': '#3B82F6',
            'primary_hover': '#2563EB',
            'secondary': '#64748B',
            'text_dark': '#1E293B',
            'text_light': '#64748B',
            'border': '#E2E8F0',
            'success': '#10B981'
        }

        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)

        # Центральная карточка
        card_frame = tk.Frame(
            main_frame,
            bg=self.colors['card_bg'],
            highlightbackground=self.colors['border'],
            highlightthickness=1,
            relief='flat'
        )
        card_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=550)

        # Заголовок
        title_label = tk.Label(
            card_frame,
            text='LeanFlow',
            font=('Roboto', 36, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['card_bg']
        )
        title_label.pack(pady=(50, 40))

        # Подзаголовок
        subtitle_label = tk.Label(
            card_frame,
            text='Создайте свой аккаунт',
            font=('Roboto', 16),
            fg=self.colors['text_light'],
            bg=self.colors['card_bg']
        )
        subtitle_label.pack(pady=(0, 40))

        # Фрейм для формы ввода
        form_frame = tk.Frame(card_frame, bg=self.colors['card_bg'])
        form_frame.pack(padx=50, fill='x')

        # Поле для ввода email
        email_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        email_frame.pack(fill='x', pady=(0, 25))

        email_label = tk.Label(
            email_frame,
            text='Email',
            font=('Roboto', 12, 'bold'),
            fg=self.colors['text_dark'],
            bg=self.colors['card_bg']
        )
        email_label.pack(anchor='w', pady=(0, 8))

        self.email_entry = tk.Entry(
            email_frame,
            font=('Roboto', 14),
            width=30,
            bg=self.colors['background'],
            relief='flat',
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            highlightthickness=2
        )
        self.email_entry.pack(fill='x', ipady=12)

        # Поле для ввода пароля
        password_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        password_frame.pack(fill='x', pady=(0, 40))

        password_label = tk.Label(
            password_frame,
            text='Пароль',
            font=('Roboto', 12, 'bold'),
            fg=self.colors['text_dark'],
            bg=self.colors['card_bg']
        )
        password_label.pack(anchor='w', pady=(0, 8))

        self.password_entry = tk.Entry(
            password_frame,
            font=('Roboto', 14),
            width=30,
            show='•',
            bg=self.colors['background'],
            relief='flat',
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            highlightthickness=2
        )
        self.password_entry.pack(fill='x', ipady=12)

        # Кнопка регистрации
        self.register_button = tk.Button(
            form_frame,
            text='Зарегистрироваться',
            font=('Roboto', 14, 'bold'),
            fg='white',
            bg=self.colors['primary'],
            activebackground=self.colors['primary_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            width=20,
            height=1,
            bd=0
        )
        self.register_button.pack(fill='x', pady=(0, 30), ipady=15)

        # Ссылка на вход (заглушка)
        login_label = tk.Label(
            form_frame,
            text='Уже есть аккаунт? Войти',
            font=('Roboto', 12),
            fg=self.colors['primary'],
            bg=self.colors['card_bg'],
            cursor='hand2'
        )
        login_label.pack()

        # Добавляем эффекты при наведении на кнопку
        def on_enter(e):
            self.register_button['bg'] = self.colors['primary_hover']

        def on_leave(e):
            self.register_button['bg'] = self.colors['primary']

        self.register_button.bind("<Enter>", on_enter)
        self.register_button.bind("<Leave>", on_leave)

        # Фокус на поле email при запуске
        self.email_entry.focus_set()

    def run(self):
        self.root.mainloop()


# Запуск приложения
if __name__ == "__main__":
    app = Registr()
    app.run()