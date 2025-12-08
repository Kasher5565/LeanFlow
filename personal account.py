import tkinter as tk
from tkinter import messagebox


class PersonalAccount:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Личный кабинет')
        self.root.configure(bg='#EADEBD')
        self.root.state('zoomed')

        # Цветовая палитра
        self.colors = {
            'beige': '#EADEBD',  # Основной фон
            'saddle_brown': '#8B4513',  # Основной акцентный цвет
            'saddle_brown_hover': '#A0522D',  # Более светлый коричневый для hover
            'slate_gray': '#64748B',  # Вторичный текст
            'slate_gray_light': '#94A3B8',  # Светлый для текста при hover
            'white': '#FFFFFF',  # Белый
            'light_beige': '#F5F0E6',  # Светлый бежевый для карточек
            'card_bg': '#FFFFF0'  # Фон карточек
        }

        # Данные пользователя должны браться из бд
        self.user_data = {
            'name': 'Иван Иванов',
            'email': 'ivan.ivanov@mail.ru',
            'phone': '+7(999)123-45-67',
            'registration_date': '10.12.2025',
        }

        self.create_widgets()

    def create_widgets(self):
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.colors['beige'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Заголовок
        self.create_header(main_container)

        # Основной контент
        content_frame = tk.Frame(main_container, bg=self.colors['beige'])
        content_frame.pack(fill='both', expand=True, pady=20)

        # Левая колонка (информация о пользователе)
        self.create_user_info_section(content_frame)

        # Правая колонка (проекты и статистика)
        self.create_projects_section(content_frame)

        # Нижняя панель (быстрые действия)
        self.create_actions_panel(main_container)

    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['saddle_brown'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        # Логотип и название
        title_frame = tk.Frame(header_frame, bg=self.colors['saddle_brown'])
        title_frame.pack(side='left', padx=30)

        title_label = tk.Label(
            title_frame,
            text='LeanFlow',
            font=('Roboto', 24, 'bold'),
            fg='white',
            bg=self.colors['saddle_brown']
        )
        title_label.pack(anchor='w')

        subtitle_label = tk.Label(
            title_frame,
            text='Личный кабинет',
            font=('Roboto', 12),
            fg=self.colors['slate_gray_light'],
            bg=self.colors['saddle_brown']
        )
        subtitle_label.pack(anchor='w')

        # фрейм для кнопки
        user_panel = tk.Frame(header_frame, bg=self.colors['saddle_brown'])
        user_panel.pack(side='right', padx=30)

        settings_button = tk.Button(
            user_panel,
            text='Настройки',
            font=('Roboto', 10),
            bg=self.colors['light_beige'],
            fg=self.colors['saddle_brown'],
            activebackground=self.colors['beige'],
            activeforeground=self.colors['saddle_brown'],
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.open_settings
        )
        settings_button.pack(fill='x', pady=5)


    def create_user_info_section(self, parent):
        # Левая колонка
        left_column = tk.Frame(parent, bg=self.colors['beige'], width=400)
        left_column.pack(side='left', fill='y', padx=(0, 10))
        left_column.pack_propagate(False)

        # Карточка пользователя
        user_card = tk.Frame(
            left_column,
            bg=self.colors['card_bg'],
            relief='flat',
            highlightbackground=self.colors['slate_gray'],
            highlightthickness=1
        )
        user_card.pack(fill='x', pady=(0, 15))

        # Аватар и основная информация
        avatar_frame = tk.Frame(user_card, bg=self.colors['card_bg'], height=100)
        avatar_frame.pack(fill='x', padx=20, pady=20)

        # Иконка аватара
        avatar_label = tk.Label(
            avatar_frame,
            text='👨‍💼',
            font=('Roboto', 48),
            bg=self.colors['card_bg']
        )
        avatar_label.pack(side='left')

        # Информация пользователя
        info_frame = tk.Frame(avatar_frame, bg=self.colors['card_bg'])
        info_frame.pack(side='left', fill='both', expand=True, padx=20)

        # имя
        name_label = tk.Label(
            info_frame,
            text=self.user_data['name'],
            font=('Roboto', 16, 'bold'),
            fg=self.colors['saddle_brown'],
            bg=self.colors['card_bg'],
            anchor='w'
        )
        name_label.pack(fill='x')

        # почта
        email_label = tk.Label(
            info_frame,
            text=self.user_data['email'],
            font=('Roboto', 10),
            fg=self.colors['slate_gray'],
            bg=self.colors['card_bg'],
            anchor='w'
        )
        email_label.pack(fill='x', pady=(5, 0))

        # Детальная информация
        details_frame = tk.Frame(user_card, bg=self.colors['light_beige'])
        details_frame.pack(fill='x', padx=20, pady=15)

        # информация в карте пользователя, должна браться из бд
        details = [
            ('📱 Телефон:', self.user_data['phone']),
            ('📅 Дата регистрации:', self.user_data['registration_date']),
        ]

        # используется для отображения инфы в карточке
        for label_text, value_text in details:
            detail_frame = tk.Frame(details_frame, bg=self.colors['light_beige'])
            detail_frame.pack(fill='x', pady=8)

            label = tk.Label(
                detail_frame,
                text=label_text,
                font=('Roboto', 10),
                fg=self.colors['slate_gray'],
                bg=self.colors['light_beige'],
                width=15,
                anchor='w'
            )
            label.pack(side='left')

            value = tk.Label(
                detail_frame,
                text=value_text,
                font=('Roboto', 10, 'bold'),
                fg=self.colors['saddle_brown'],
                bg=self.colors['light_beige'],
                anchor='w'
            )
            value.pack(side='left', fill='x', expand=True)

        # Кнопки действий
        buttons_frame = tk.Frame(user_card, bg=self.colors['card_bg'])
        buttons_frame.pack(fill='x', padx=20, pady=20)

        edit_button = tk.Button(
            buttons_frame,
            text='Редактировать профиль',
            font=('Roboto', 10),
            bg=self.colors['saddle_brown'],
            fg='white',
            activebackground=self.colors['saddle_brown_hover'],
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.edit_profile
        )
        edit_button.pack(fill='x', pady=5)

        # Добавляем эффект наведения для кнопки
        edit_button.bind('<Enter>', lambda e: edit_button.configure(bg=self.colors['saddle_brown_hover']))
        edit_button.bind('<Leave>', lambda e: edit_button.configure(bg=self.colors['saddle_brown']))

        data_button = tk.Button(
            buttons_frame,
            text='Подробная информация',
            font=('Roboto', 10),
            bg=self.colors['saddle_brown'],
            fg='white',
            activebackground=self.colors['saddle_brown_hover'],
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.show_information
        )
        data_button.pack(fill='x', pady=5)

        # Добавляем эффект наведения для кнопки
        data_button.bind('<Enter>', lambda e: data_button.configure(bg=self.colors['saddle_brown_hover']))
        data_button.bind('<Leave>', lambda e: data_button.configure(bg=self.colors['saddle_brown']))

    def create_projects_section(self, parent):
        # Правая колонка со списком проектов и статистикой(пока пустым)
        right_column = tk.Frame(parent, bg=self.colors['beige'])
        right_column.pack(side='left', fill='both', expand=True, padx=(10, 0))

        # Статистика
        stats_frame = tk.Frame(
            right_column,
            bg=self.colors['card_bg'],
            relief='flat',
            highlightbackground=self.colors['slate_gray'],
            highlightthickness=1
        )
        stats_frame.pack(fill='x', pady=(0, 15))

        stats_label = tk.Label(
            stats_frame,
            text='📊 Статистика',
            font=('Roboto', 14, 'bold'),
            fg=self.colors['saddle_brown'],
            bg=self.colors['card_bg'],
            anchor='w'
        )
        stats_label.pack(fill='x', padx=20, pady=15)

        # Показатели статистики
        stats_grid = tk.Frame(stats_frame, bg=self.colors['card_bg'])
        stats_grid.pack(fill='x', padx=20, pady=(0, 20))

        stats_data = [
            ('Завершено задач', '✅'),
            ('Текущие задачи', '🔄'),
        ]

        # отображает значки и текст в статистике
        for i, (title, icon) in enumerate(stats_data):
            stat_frame = tk.Frame(stats_grid, bg=self.colors['card_bg'])
            stat_frame.grid(row=i // 2, column=i % 2, sticky='ew', padx=10, pady=10)
            stats_grid.columnconfigure(i % 2, weight=1)

            # значки
            icon_label = tk.Label(
                stat_frame,
                text=icon,
                font=('Roboto', 20),
                bg=self.colors['card_bg']
            )
            icon_label.pack(anchor='w')

            # текст
            title_label = tk.Label(
                stat_frame,
                text=title,
                font=('Roboto', 10),
                fg=self.colors['slate_gray'],
                bg=self.colors['card_bg'],
            )
            title_label.pack(anchor='w')

        # Список проектов
        projects_frame = tk.Frame(
            right_column,
            bg=self.colors['card_bg'],
            relief='flat',
            highlightbackground=self.colors['slate_gray'],
            highlightthickness=1
        )
        projects_frame.pack(fill='both', expand=True)

        # окно с проектами
        projects_label = tk.Label(
            projects_frame,
            text='📋 Мои проекты',
            font=('Roboto', 14, 'bold'),
            fg=self.colors['saddle_brown'],
            bg=self.colors['card_bg'],
            anchor='w'
        )
        projects_label.pack(fill='x', padx=20, pady=15)

        # Кнопка открытия проекта
        project_buttons = tk.Frame(projects_frame, bg=self.colors['card_bg'])
        project_buttons.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        open_btn = tk.Button(
            project_buttons,
            text='Открыть проект',
            font=('Roboto', 10),
            bg=self.colors['saddle_brown'],
            fg='white',
            activebackground=self.colors['saddle_brown_hover'],
            activeforeground='white',
            relief='flat',
            padx=15,
            pady=6,
            cursor='hand2',
            command=self.open_project
        )
        open_btn.pack(side='bottom', anchor='e', padx=(0, 10), pady=10)
        open_btn.bind('<Enter>', lambda e: open_btn.configure(bg=self.colors['saddle_brown_hover']))
        open_btn.bind('<Leave>', lambda e: open_btn.configure(bg=self.colors['saddle_brown']))


    def create_actions_panel(self, parent):
        actions_frame = tk.Frame(parent, bg=self.colors['saddle_brown'], height=70)
        actions_frame.pack(fill='x', side='bottom')
        actions_frame.pack_propagate(False)

        quick_actions = [
            ('Импорт', self.import_data),
            ('Экспорт', self.export_data),
            ('Печать', self.print_report),
            ('Уведомления', self.show_notifications),
            ('Помощь', self.show_help)
        ]

        for text, command in quick_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                font=('Roboto', 10),
                bg=self.colors['saddle_brown_hover'],
                fg='white',
                activebackground=self.colors['slate_gray'],
                activeforeground='white',
                relief='flat',
                padx=15,
                pady=8,
                cursor='hand2',
                command=command
            )
            btn.pack(side='left', padx=10, pady=15)

            # Эффект наведения для кнопок быстрых действий
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.colors['slate_gray']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.colors['saddle_brown_hover']))

    # Методы-заглушки для функциональности
    def edit_profile(self):
        messagebox.showinfo("Редактирование", "Переход в режим редактирования профиля")

    def show_information(self):
        messagebox.showinfo("Информация", "Показ полной информации")

    def open_settings(self):
        messagebox.showinfo("Настройки", "Открытие настроек приложения")

    def open_project(self):
        messagebox.showinfo("Проект", "Открытие выбранного проекта")

    def import_data(self):
        messagebox.showinfo("Импорт", "Импорт данных")

    def export_data(self):
        messagebox.showinfo("Экспорт", "Экспорт данных")

    def print_report(self):
        messagebox.showinfo("Печать", "Печать отчета")

    def show_notifications(self):
        messagebox.showinfo("Уведомления", "Просмотр уведомлений")

    def show_help(self):
        messagebox.showinfo("Помощь", "Открытие справки")

    def run(self):
        self.root.mainloop()


# Запуск приложения
if __name__ == '__main__':
    app = PersonalAccount()
    app.run()