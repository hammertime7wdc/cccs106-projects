# main.py
import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact, search_contacts

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 450
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize database
    db_conn = init_db()
    
    # Input fields
    name_input = ft.TextField(label="Name", width=380)
    phone_input = ft.TextField(label="Phone", width=380)
    email_input = ft.TextField(label="Email", width=380)
    inputs = (name_input, phone_input, email_input)
    
    # Search field
    search_input = ft.TextField(
        label="Search contacts...",
        width=380,
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: search_contacts(page, search_input.value, contacts_list_view, db_conn)
    )
    
    # Contacts list
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)
    
    # Theme toggle
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()
    
    theme_switch = ft.Switch(
        label="Dark Mode",
        on_change=toggle_theme
    )
    
    # Add button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        icon=ft.Icons.ADD,
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )
    
    # Layout
    page.add(
        ft.Column([
            ft.Row([
                ft.Text("Contact Book", size=24, weight=ft.FontWeight.BOLD),
                theme_switch
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Text("Enter Contact Details:", size=18, weight=ft.FontWeight.BOLD),
            name_input,
            phone_input,
            email_input,
            add_button,
            ft.Divider(),
            ft.Text("Contacts:", size=18, weight=ft.FontWeight.BOLD),
            search_input,
            contacts_list_view,
        ])
    )
    
    # Load initial contacts
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)
