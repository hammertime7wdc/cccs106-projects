import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    page.window.center()
    page.window.frameless = True
    page.title = "User Log in"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT

    log_in_title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER
    )

    username_input = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        prefix_icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        disabled=False,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    async def login_click(e):
        success_dialog = ft.AlertDialog(
            title=ft.Text("Login Successful"),
            content=ft.Text(
                f"Welcome, {username_input.value}!",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(success_dialog))
            ],
            icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        )
        
        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed"),
            content=ft.Text(
                "Invalid username or password",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(failure_dialog))
            ],
            icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED)
        )
        
        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error"),
            content=ft.Text(
                "Please enter username and password",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(invalid_input_dialog))
            ],
            icon=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE)
        )
        
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text(
                "An error occurred while connecting to the database",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(database_error_dialog))
            ],
            icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED)
        )
        
        def close_dialog(dialog):
            dialog.open = False
            page.update()
        
        if not username_input.value or not password.value:
            page.overlay.append(invalid_input_dialog)
            invalid_input_dialog.open = True
            page.update()
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username_input.value, password.value)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                page.overlay.append(success_dialog)
                success_dialog.open = True
            else:
                page.overlay.append(failure_dialog)
                failure_dialog.open = True
            
            page.update()
            
        except mysql.connector.Error as e:
            page.overlay.append(database_error_dialog)
            database_error_dialog.open = True
            page.update()
            print(f"Database error: {e}")

    login_button = ft.ElevatedButton(
        text="Login",
        on_click=login_click,
        width=100,
        icon=ft.Icons.LOGIN
    )
    
    page.add(
        ft.Column([
            log_in_title,
            ft.Container(height=30),
            username_input,
            ft.Container(height=10),
            password,
            ft.Container(height=30),
            ft.Row([
                ft.Container(expand=True),
                login_button
            ])
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)