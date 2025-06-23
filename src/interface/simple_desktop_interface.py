import os.path
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2

from src.core import ImageProcessor


class StylishImageViewerApp:
    def __init__(self, root_window):
        self.processor = ImageProcessor()

        self.report_text = None
        self.report_label = None
        self.image_placeholder = None
        self.image_frame = None
        self.select_button = None

        self.root = root_window
        self.root.title("Система оценки поведения водителя")
        self.root.geometry("800x700")
        self.root.configure(bg="#1a1a1a")  # Тёмно-серый фон

        # Цветовая схема
        self.bg_dark = "#1a1a1a"  # Основной фон (тёмно-серый)
        self.bg_medium = "#252525" # Цвет поля с изображением
        self.bg_light = "#2d2d2d"  # Вторичный фон (серый)
        self.accent = "#800020"  # Бардовый акцент
        self.text_light = "#ffffff"  # Белый текст
        self.text_muted = "#cccccc"  # Серый текст

        # Переменные
        self.image_path = None
        self.image_label = None

        # Настройка стиля для ttk (более современные виджеты)
        self.__setup_styles()

        # Создание интерфейса
        self.__create_widgets()

    def __setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')  # Современная основа для кастомизации

        # Настройка стиля кнопки
        style.configure(
            "Accent.TButton",
            foreground=self.text_light,
            background=self.accent,
            bordercolor=self.accent,
            font=('Helvetica', 10, 'bold'),
            padding=8,
            focuscolor=self.bg_light
        )
        style.map(
            "Accent.TButton",
            background=[('active', '#600018'), ('pressed', '#400010')],
            bordercolor=[('active', '#600018')]
        )

        # Стиль текстового поля
        style.configure(
            "Dark.TEntry",
            fieldbackground=self.bg_light,
            foreground=self.text_light,
            insertcolor=self.text_light,
            bordercolor=self.bg_light,
            lightcolor=self.bg_light,
            darkcolor=self.bg_light
        )

        # Стиль фрейма
        style.configure(
            "Dark.TFrame",
            background=self.bg_dark
        )

    def __create_widgets(self):
        # Основной контейнер для центрирования
        main_frame = ttk.Frame(self.root, style="Dark.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Область для изображения (с рамкой)
        self.image_frame = ttk.Frame(
            main_frame,
            style="Dark.TFrame",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Метка для отображения изображения
        self.image_placeholder = ttk.Label(
            self.image_frame,
            text="Изображение не выбрано",
            foreground=self.text_muted,
            background=self.bg_medium,
            font=('Helvetica', 12)
        )
        self.image_placeholder.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Кнопка выбора изображения
        self.select_button = ttk.Button(
            main_frame,
            text="Выбрать изображение",
            style="Accent.TButton",
            command=self.__open_image
        )
        self.select_button.pack(pady=(0, 15))

        # Метка "Отчёт"
        self.report_label = ttk.Label(
            main_frame,
            text="Отчёт по обработке:",
            foreground=self.text_light,
            background=self.bg_dark,
            font=('Helvetica', 10, 'bold')
        )
        self.report_label.pack(anchor=tk.W, pady=(0, 5))

        # Текстовая зона для отчёта
        self.report_text = tk.Text(
            main_frame,
            height=10,
            wrap=tk.WORD,
            bg=self.bg_light,
            fg=self.text_light,
            insertbackground=self.text_light,
            selectbackground=self.accent,
            font=('Helvetica', 9),
            padx=10,
            pady=10,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.accent,
            highlightbackground=self.bg_light,
            state="disabled"
        )
        self.report_text.pack(fill=tk.BOTH, expand=False)

    def __open_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if not file_path:
            return

        self.image_path = file_path

        try:
            warnings, image_with_boxes = self.__start_process(file_path)
            extension = os.path.splitext(file_path)[1]
            height = image_with_boxes.height
            width = image_with_boxes.width

            # Удаляем плейсхолдер, если он есть
            if self.image_placeholder:
                self.image_placeholder.destroy()
                self.image_placeholder = None

            # Очищаем предыдущее изображение
            if self.image_label:
                self.image_label.destroy()

            # Масштабируем изображение
            max_width = self.image_frame.winfo_width() - 20
            max_height = 400
            image_with_boxes.thumbnail((max_width, max_height), Image.LANCZOS)

            # Конвертируем для Tkinter
            photo = ImageTk.PhotoImage(image_with_boxes)

            # Отображаем изображение
            self.image_label = ttk.Label(self.image_frame, image=photo, background=self.bg_dark)
            self.image_label.image = photo
            self.image_label.pack(pady=10, padx=10)

            # Записываем отчёт
            self.report_text.config(state='normal')
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, f"🖼 Изображение загружено: {file_path}\n", "bold")
            self.report_text.insert(tk.END, f"📏 Размер: {width}x{height}\n")
            self.report_text.insert(tk.END, f"🎨 Формат: {extension}\n\n")
            self.report_text.insert(tk.END, "")

            if len(warnings) != 0:
                self.report_text.insert(tk.END, "⚠️ Предупреждения:\n")
                self.__show_warnings(warnings)
            else:
                self.report_text.insert(tk.END, "✔️ Некорректного поведения не обнаружено!")

            # Настройка тегов для форматирования текста
            self.report_text.tag_config("bold", font=('Helvetica', 9, 'bold'))
            self.report_text.config(state='disabled')

        except Exception as e:
            self.report_text.config(state='normal')
            self.report_text.insert(tk.END, f"❌ Ошибка: {str(e)}\n", "error")
            self.report_text.tag_config("error", foreground="#ff4444")
            self.report_text.config(state='disabled')

    def __show_warnings(self, warnings):
        for i in range(len(warnings)):
            self.report_text.insert(tk.END, f"  {i + 1}) {warnings[i]}\n")

    def __start_process(self, image_path):
        image = cv2.imread(image_path)

        warnings, image_with_boxes = self.processor(image)

        if image_with_boxes is None:
            image_with_boxes = image

        rgb_image = cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)
        rgb_image = Image.fromarray(rgb_image)

        return warnings, rgb_image


if __name__ == "__main__":
    root = tk.Tk()
    app = StylishImageViewerApp(root)
    root.mainloop()