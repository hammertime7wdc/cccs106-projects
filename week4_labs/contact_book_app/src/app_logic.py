# app_logic.py
import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def display_contacts(page, contacts_list_view, db_conn, search_term=None):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)
    
    if not contacts:
        contacts_list_view.controls.append(
            ft.Container(
                content=ft.Text("No contacts found", style=ft.TextThemeStyle.BODY_MEDIUM),
                alignment=ft.alignment.center,
                padding=20
            )
        )
    else:
        for contact in contacts:
            contact_id, name, phone, email = contact
            
            # Create a modern card layout
            card_content = ft.Column([
                ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Icon(ft.Icons.PHONE, size=16),
                    ft.Text(phone or "No phone", size=14)
                ], spacing=5) if phone else ft.Container(),
                ft.Row([
                    ft.Icon(ft.Icons.EMAIL, size=16),
                    ft.Text(email or "No email", size=14)
                ], spacing=5) if email else ft.Container(),
            ], spacing=5)
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Container(card_content, expand=True),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    text="Edit",
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                                ),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda _, cid=contact_id: show_delete_confirmation(page, cid, name, db_conn, contacts_list_view)
                                ),
                            ],
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                ),
                elevation=2
            )
            contacts_list_view.controls.append(card)
    
    page.update()

def search_contacts(page, search_term, contacts_list_view, db_conn):
    """Filters contacts based on search term."""
    display_contacts(page, contacts_list_view, db_conn, search_term)

def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact with input validation."""
    name_input, phone_input, email_input = inputs
    
    # Clear previous error messages
    name_input.error_text = None
    phone_input.error_text = None
    email_input.error_text = None
    
    # Validation
    is_valid = True
    
    if not name_input.value or not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        is_valid = False
    
    if not is_valid:
        page.update()
        return
    
    # Add contact to database
    add_contact_db(db_conn, name_input.value.strip(), phone_input.value.strip(), email_input.value.strip())
    
    # Clear input fields
    for field in inputs:
        field.value = ""
    
    # Refresh the contact list
    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def show_delete_confirmation(page, contact_id, contact_name, db_conn, contacts_list_view):
    """Shows confirmation dialog before deleting a contact."""
    def confirm_delete(e):
        delete_contact_db(db_conn, contact_id)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)
    
    def cancel_delete(e):
        dialog.open = False
        page.update()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text(f"Are you sure you want to delete '{contact_name}'? This action cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=cancel_delete),
            ft.TextButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
        ],
    )
    
    page.open(dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    
    edit_name = ft.TextField(label="Name", value=name, width=300)
    edit_phone = ft.TextField(label="Phone", value=phone or "", width=300)
    edit_email = ft.TextField(label="Email", value=email or "", width=300)
    
    def save_and_close(e):
        # Validation
        if not edit_name.value or not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty"
            page.update()
            return
        
        edit_name.error_text = None
        update_contact_db(db_conn, contact_id, edit_name.value.strip(), edit_phone.value.strip(), edit_email.value.strip())
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)
    
    def cancel_edit(e):
        dialog.open = False
        page.update()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email], height=200, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Cancel", on_click=cancel_edit),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    
    page.open(dialog)