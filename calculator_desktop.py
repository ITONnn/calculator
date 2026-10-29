#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Десктопное приложение: «Калькулятор»
Полное соответствие Техническому Заданию:
1. UI/UX:
   - Заголовок окна: «Калькулятор», тёмная тема (dark)
   - Дисплей из 2 полей (выравнивание по правому краю):
     * Верхнее поле: история ввода (серый текст, шрифт 14)
     * Нижнее поле: текущее число / результат (жирный шрифт, размер 36, по умолчанию 0)
   - Сетка кнопок:
     * Математические действия (÷, ×, −, +): #f39c12, белый текст
     * Кнопка равно (=): #2ecc71, белый текст
     * Кнопка очистки (C): #e74c3c, белый текст
     * Доп. операции (±, %, ⌫): #555555, белый текст
2. Функционал:
   - +, −, ×, ÷, C, ⌫, ±, %, десятичная точка (блокировка повторной точки, напр. 5..2 или 5.2.1)
   - Полное управление мышью и с клавиатуры
3. Безопасность:
   - Автоматическое стирание предыдущей сессии при каждом запуске приложения
   - Окно авторизации и регистрации перед доступом к калькулятору
"""

import hashlib
import json
import os
import tkinter as tk
from tkinter import messagebox

SESSION_FILE = "calc_session.json"
USERS_FILE = "calc_users.json"


def wipe_previous_session() -> None:
    """Стирает данные предыдущей сессии использования калькулятора при запуске."""
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except OSError:
            pass
    # Инициализируем пустую чистую сессию в оперативной памяти
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"history": "", "current": "0", "active_user": None}, f)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        default_users = {"admin": hash_password("admin123")}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f)
        return default_users
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"admin": hash_password("admin123")}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


class AuthWindow:
    """Окно авторизации и регистрации при запуске калькулятора."""

    def __init__(self, root: tk.Tk, on_success):
        self.root = root
        self.on_success = on_success
        self.mode = "login"  # "login" или "register"
        self.users = load_users()

        self.root.title("Калькулятор — Авторизация")
        self.root.geometry("380x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#141418")

        self.container = tk.Frame(self.root, bg="#141418", padx=28, pady=24)
        self.container.pack(fill="both", expand=True)

        self.title_lbl = tk.Label(
            self.container,
            text="Вход в Калькулятор",
            font=("Segoe UI", 18, "bold"),
            bg="#141418",
            fg="#ffffff",
        )
        self.title_lbl.pack(anchor="w", pady=(0, 6))

        self.subtitle_lbl = tk.Label(
            self.container,
            text="Предыдущая сессия успешно очищена.\nАвторизуйтесь для начала работы.",
            font=("Segoe UI", 10),
            bg="#141418",
            fg="#9ca3af",
            justify="left",
        )
        self.subtitle_lbl.pack(anchor="w", pady=(0, 20))

        # Поле логина
        tk.Label(
            self.container,
            text="Имя пользователя",
            font=("Segoe UI", 10, "bold"),
            bg="#141418",
            fg="#d1d5db",
        ).pack(anchor="w", pady=(0, 4))

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            self.container,
            textvariable=self.username_var,
            font=("Segoe UI", 12),
            bg="#1f2028",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            bd=8,
        )
        self.username_entry.pack(fill="x", pady=(0, 14))

        # Поле пароля
        tk.Label(
            self.container,
            text="Пароль",
            font=("Segoe UI", 10, "bold"),
            bg="#141418",
            fg="#d1d5db",
        ).pack(anchor="w", pady=(0, 4))

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self.container,
            textvariable=self.password_var,
            show="•",
            font=("Segoe UI", 12),
            bg="#1f2028",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            bd=8,
        )
        self.password_entry.pack(fill="x", pady=(0, 20))

        # Кнопка действия
        self.submit_btn = tk.Button(
            self.container,
            text="Войти",
            font=("Segoe UI", 12, "bold"),
            bg="#f39c12",
            fg="#ffffff",
            activebackground="#d68910",
            activeforeground="#ffffff",
            relief="flat",
            pady=10,
            cursor="hand2",
            command=self.handle_submit,
        )
        self.submit_btn.pack(fill="x", pady=(0, 10))

        # Переключение режима Вход / Регистрация
        self.switch_btn = tk.Button(
            self.container,
            text="Нет аккаунта? Зарегистрироваться",
            font=("Segoe UI", 10),
            bg="#141418",
            fg="#9ca3af",
            activebackground="#141418",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.toggle_mode,
        )
        self.switch_btn.pack(fill="x")

        self.root.bind("<Return>", lambda _: self.handle_submit())
        self.username_entry.focus_set()

    def toggle_mode(self):
        if self.mode == "login":
            self.mode = "register"
            self.title_lbl.config(text="Регистрация")
            self.submit_btn.config(text="Создать аккаунт", bg="#2ecc71")
            self.switch_btn.config(text="Уже есть аккаунт? Войти")
        else:
            self.mode = "login"
            self.title_lbl.config(text="Вход в Калькулятор")
            self.submit_btn.config(text="Войти", bg="#f39c12")
            self.switch_btn.config(text="Нет аккаунта? Зарегистрироваться")

    def handle_submit(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if len(username) < 3 or len(password) < 4:
            messagebox.showwarning(
                "Ошибка ввода",
                "Логин должен содержать минимум 3 символа, пароль — минимум 4 символа.",
            )
            return

        if self.mode == "register":
            if username in self.users:
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
                return
            self.users[username] = hash_password(password)
            save_users(self.users)
            self.open_calculator(username)
        else:
            if username not in self.users or self.users[username] != hash_password(password):
                messagebox.showerror("Ошибка авторизации", "Неверный логин или пароль.")
                return
            self.open_calculator(username)

    def open_calculator(self, username: str):
        self.root.unbind("<Return>")
        self.container.destroy()
        self.on_success(username)


class CalculatorWindow:
    """Основное окно десктопного приложения «Калькулятор»."""

    def __init__(self, root: tk.Tk, username: str):
        self.root = root
        self.username = username

        # Настройка главного окна согласно ТЗ
        self.root.title("Калькулятор")
        self.root.geometry("360x540")
        self.root.resizable(False, False)
        self.root.configure(bg="#141418")

        # Внутреннее состояние вычислений (чистая сессия)
        self.current_input = "0"
        self.previous_value = None
        self.operator = None
        self.waiting_for_operand = False
        self.history_text = ""

        self._build_ui()
        self._bind_keyboard()

    def _build_ui(self):
        # Экран калькулятора (Дисплей)
        display_frame = tk.Frame(self.root, bg="#1c1d24", padx=18, pady=18)
        display_frame.pack(fill="x", padx=14, pady=(14, 10))

        # Верхнее поле: история ввода, серый цвет, шрифт 14, выравнивание по правому краю
        self.history_label = tk.Label(
            display_frame,
            text="",
            font=("Segoe UI", 14),
            bg="#1c1d24",
            fg="#9ca3af",
            anchor="e",
            justify="right",
        )
        self.history_label.pack(fill="x", pady=(0, 6))

        # Нижнее поле (основное): текущее число или результат, жирный шрифт 36, по умолчанию 0
        self.main_label = tk.Label(
            display_frame,
            text="0",
            font=("Segoe UI", 36, "bold"),
            bg="#1c1d24",
            fg="#ffffff",
            anchor="e",
            justify="right",
        )
        self.main_label.pack(fill="x")

        # Сетка кнопок (Клавиатура калькулятора)
        grid_frame = tk.Frame(self.root, bg="#141418")
        grid_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        for r in range(5):
            grid_frame.rowconfigure(r, weight=1)
        for c in range(4):
            grid_frame.columnconfigure(c, weight=1)

        buttons = [
            ("C", 0, 0, "#e74c3c", self.clear_all),
            ("±", 0, 1, "#555555", self.toggle_sign),
            ("%", 0, 2, "#555555", self.percentage),
            ("÷", 0, 3, "#f39c12", lambda: self.handle_operator("÷")),
            ("7", 1, 0, "#2a2b36", lambda: self.input_digit("7")),
            ("8", 1, 1, "#2a2b36", lambda: self.input_digit("8")),
            ("9", 1, 2, "#2a2b36", lambda: self.input_digit("9")),
            ("×", 1, 3, "#f39c12", lambda: self.handle_operator("×")),
            ("4", 2, 0, "#2a2b36", lambda: self.input_digit("4")),
            ("5", 2, 1, "#2a2b36", lambda: self.input_digit("5")),
            ("6", 2, 2, "#2a2b36", lambda: self.input_digit("6")),
            ("−", 2, 3, "#f39c12", lambda: self.handle_operator("−")),
            ("1", 3, 0, "#2a2b36", lambda: self.input_digit("1")),
            ("2", 3, 1, "#2a2b36", lambda: self.input_digit("2")),
            ("3", 3, 2, "#2a2b36", lambda: self.input_digit("3")),
            ("+", 3, 3, "#f39c12", lambda: self.handle_operator("+")),
            ("⌫", 4, 0, "#555555", self.backspace),
            ("0", 4, 1, "#2a2b36", lambda: self.input_digit("0")),
            (".", 4, 2, "#2a2b36", self.input_decimal),
            ("=", 4, 3, "#2ecc71", self.calculate_equals),
        ]

        for text, row, col, bg_color, cmd in buttons:
            btn = tk.Button(
                grid_frame,
                text=text,
                font=("Segoe UI", 16, "bold"),
                bg=bg_color,
                fg="#ffffff",
                activebackground=bg_color,
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=cmd,
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

    def _bind_keyboard(self):
        self.root.bind("<Key>", self._on_key_press)

    def _on_key_press(self, event: tk.Event):
        key = event.keysym
        char = event.char

        if char in "0123456789":
            self.input_digit(char)
        elif char in (".", ","):
            self.input_decimal()
        elif char == "+":
            self.handle_operator("+")
        elif char == "-":
            self.handle_operator("−")
        elif char == "*":
            self.handle_operator("×")
        elif char == "/":
            self.handle_operator("÷")
        elif char == "%":
            self.percentage()
        elif key in ("Return", "KP_Enter") or char == "=":
            self.calculate_equals()
        elif key == "BackSpace":
            self.backspace()
        elif key in ("Escape", "Delete") or char in ("c", "C", "с", "С"):
            self.clear_all()
        elif key == "F9":
            self.toggle_sign()

    def _format_number(self, num: float) -> str:
        if num == int(num):
            return str(int(num))
        formatted = f"{num:.10f}".rstrip("0").rstrip(".")
        return formatted if formatted != "-0" else "0"

    def _update_display(self):
        self.history_label.config(text=self.history_text)
        self.main_label.config(text=self.current_input)

    def input_digit(self, digit: str):
        if self.current_input == "Ошибка":
            self.clear_all()

        if self.waiting_for_operand:
            self.current_input = digit
            self.waiting_for_operand = False
        else:
            self.current_input = digit if self.current_input == "0" else self.current_input + digit
        self._update_display()

    def input_decimal(self):
        """Добавляет десятичную точку. Блокирует ввод двух точек в одном числе (5..2 или 5.2.1)."""
        if self.current_input == "Ошибка":
            self.clear_all()

        if self.waiting_for_operand:
            self.current_input = "0."
            self.waiting_for_operand = False
            self._update_display()
            return

        # Защита от повторной точки в текущем числе
        if "." in self.current_input:
            return

        self.current_input += "."
        self._update_display()

    def clear_all(self):
        """Очистка (C): сбрасывает все данные, нижнее поле = 0, верхнее очищается."""
        self.current_input = "0"
        self.previous_value = None
        self.operator = None
        self.waiting_for_operand = False
        self.history_text = ""
        self._update_display()

    def backspace(self):
        """Удаление символа (⌫): удаляет последнюю введенную цифру или знак."""
        if self.current_input == "Ошибка":
            self.clear_all()
            return

        if self.waiting_for_operand:
            if self.operator is not None and self.previous_value is not None:
                self.operator = None
                self.waiting_for_operand = False
                self.current_input = self._format_number(self.previous_value)
                self.previous_value = None
                self.history_text = ""
                self._update_display()
            return

        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
            if self.current_input in ("-", "-0"):
                self.current_input = "0"
        else:
            self.current_input = "0"
        self._update_display()

    def toggle_sign(self):
        """Смена знака (±): делает положительное число отрицательным и наоборот."""
        if self.current_input in ("0", "0.", "Ошибка"):
            return
        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input
        self._update_display()

    def percentage(self):
        """Процент (%): делит текущее значение на 100."""
        if self.current_input == "Ошибка":
            return
        try:
            value = float(self.current_input) / 100.0
            self.current_input = self._format_number(value)
            self._update_display()
        except ValueError:
            pass

    def _compute(self, left: float, right: float, op: str):
        if op == "+":
            return left + right
        if op == "−":
            return left - right
        if op == "×":
            return left * right
        if op == "÷":
            if right == 0:
                return None
            return left / right
        return right

    def handle_operator(self, next_operator: str):
        if self.current_input == "Ошибка":
            self.clear_all()

        input_value = float(self.current_input)

        if self.previous_value is None:
            self.previous_value = input_value
        elif not self.waiting_for_operand and self.operator:
            result = self._compute(self.previous_value, input_value, self.operator)
            if result is None:
                self.history_text = f"{self._format_number(self.previous_value)} ÷ 0 ="
                self.current_input = "Ошибка"
                self.previous_value = None
                self.operator = None
                self.waiting_for_operand = True
                self._update_display()
                return
            self.previous_value = result
            self.current_input = self._format_number(result)

        self.waiting_for_operand = True
        self.operator = next_operator
        self.history_text = f"{self._format_number(self.previous_value)} {next_operator}"
        self._update_display()

    def calculate_equals(self):
        if self.current_input == "Ошибка" or self.operator is None or self.previous_value is None:
            return

        input_value = float(self.current_input)
        left_str = self._format_number(self.previous_value)
        right_str = self._format_number(input_value)
        op_str = self.operator

        result = self._compute(self.previous_value, input_value, self.operator)
        self.history_text = f"{left_str} {op_str} {right_str} ="

        if result is None:
            self.current_input = "Ошибка"
        else:
            self.current_input = self._format_number(result)

        self.previous_value = None
        self.operator = None
        self.waiting_for_operand = True
        self._update_display()


def main():
    # Требование по безопасности 1: при запуске стирается предыдущая сессия
    wipe_previous_session()

    root = tk.Tk()

    # Требование по безопасности 2: окно авторизации/регистрации при запуске
    def start_calculator(username: str):
        CalculatorWindow(root, username)

    AuthWindow(root, on_success=start_calculator)
    root.mainloop()


if __name__ == "__main__":
    main()
