import csv
import datetime
import json
import re
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image as PlatypusImage
from reportlab.platypus.flowables import KeepTogether
from ttkthemes import ThemedStyle
import pyodbc

styles = getSampleStyleSheet()


class ProductManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Productos")

        # Aplicar un estilo moderno y limpio usando ttkthemes
        self.style = ThemedStyle(self.root)
        self.style.set_theme("adapta")  # Establece el tema equilux

        # Conexión a la base de datos SQL Server
        self.sql_server_connection = pyodbc.connect('Driver={SQL Server};'
                                                     'Server=valeShoko.mssql.somee.com;'
                                                     'Database=valeShoko;'
                                                     'UID=OmarPVP123_SQLLogin_1;'
                                                     'PWD=k2uo5asb6z;')

        self.sql_server_cursor = self.sql_server_connection.cursor()

        self.create_tabs()
        
       # Conexión a la base de datos SQLite
        self.connection = sqlite3.connect("bitacora.db")
        self.cursor = self.connection.cursor()
        self.create_table()
        
        # Obtener todos los eventos de la base de datos
        self.cursor.execute("SELECT * FROM bitacora")
        events = self.cursor.fetchall()
        # Enlazar la función de búsqueda al evento de escribir en el campo de búsqueda
        self.product_listbox.bind("<<ListboxSelect>>", self.show_product_details)
        self.search_entry.bind('<KeyRelease>', self.search_product)

        # Cargar los eventos al abrir la aplicación
        self.update_event_list(events)
        
    def create_table(self):
        # Crear la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bitacora (
                            id INTEGER PRIMARY KEY,
                            date_time TEXT,
                            description TEXT,
                            responsible TEXT,
                            notes TEXT,
                            status TEXT)''')
        self.connection.commit()
        
    def create_tabs(self):
        tab_control = ttk.Notebook(self.root)

        # Fichas Técnicas
        fichas_tab = ttk.Frame(tab_control)
        self.create_fichas_section(fichas_tab)
        tab_control.add(fichas_tab, text="Fichas Técnicas")

        # Bitácora
        bitacora_tab = ttk.Frame(tab_control)
        self.create_bitacora_section(bitacora_tab)
        tab_control.add(bitacora_tab, text="Bitácora")

        # Inventario
        inventario_tab = ttk.Frame(tab_control)
        self.create_inventario_section(inventario_tab)
        tab_control.add(inventario_tab, text="Inventario")

        # Inventario
        notas_tab = ttk.Frame(tab_control)
        self.notas(notas_tab)
        tab_control.add(notas_tab, text="Notas")
        
        tab_control.pack(expand=1, fill="both")

    def notas(self, tab):
        notes_frame = tk.Frame(tab)
        notes_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(notes_frame, text="Notas", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 0))

        # Botones de agregar, editar y eliminar notas
        buttons_frame = tk.Frame(notes_frame)
        buttons_frame.pack(pady=10)

        add_note_btn = tk.Button(buttons_frame, text="Agregar Nota", command=self.add_note, font=("Arial", 12))
        add_note_btn.grid(row=0, column=0, padx=5)

        edit_note_btn = tk.Button(buttons_frame, text="Editar Nota", command=self.edit_note, font=("Arial", 12))
        edit_note_btn.grid(row=0, column=1, padx=5)

        delete_note_btn = tk.Button(buttons_frame, text="Eliminar Nota", command=self.delete_note, font=("Arial", 12))
        delete_note_btn.grid(row=0, column=2, padx=5)

        # Lista de notas
        self.notes_listbox = tk.Listbox(notes_frame, width=50, height=15, font=("Arial", 12))
        self.notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de desplazamiento
        scrollbar = tk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=self.notes_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_listbox.config(yscrollcommand=scrollbar.set)

        # Cargar las notas existentes
        self.load_notes()

        # Configurar la función para abrir el contenido de una nota al hacer doble clic
        self.notes_listbox.bind("<Double-Button-1>", self.open_note_content)

    def load_notes(self):
        # Limpiar la lista de notas
        self.notes_listbox.delete(0, tk.END)

        # Obtener las notas de la base de datos
        self.sql_server_cursor.execute("SELECT * FROM notas")
        notes = self.sql_server_cursor.fetchall()

        # Mostrar las notas en la lista
        for note in notes:
            self.notes_listbox.insert(tk.END, (note[0], note[1]))  # Mostrar el ID y el título de la nota

    def open_note_content(self, event):
        # Obtener el índice de la nota seleccionada
        index = self.notes_listbox.curselection()
        if index:
            selected_note_id = self.notes_listbox.get(index)[0]  # Obtener el ID de la nota
            # Obtener el contenido de la nota desde la base de datos
            self.sql_server_cursor.execute("SELECT content FROM notas WHERE id=?", (selected_note_id,))
            content = self.sql_server_cursor.fetchone()[0]
            
            # Crear una nueva ventana para mostrar el contenido de la nota
            dialog = tk.Toplevel()
            dialog.title("Contenido de la Nota")
            
            # Marco principal para organizar los widgets
            main_frame = tk.Frame(dialog)
            main_frame.pack(padx=10, pady=10)

            # Crear una caja de texto para mostrar el contenido de la nota
            content_text = tk.Text(main_frame, wrap=tk.WORD)
            content_text.insert(tk.END, content)
            content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Barra de desplazamiento para la caja de texto
            scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=content_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Configurar la barra de desplazamiento para que funcione con la caja de texto
            content_text.config(yscrollcommand=scrollbar.set)



    def add_note(self):
        # Abrir una ventana de diálogo para agregar una nueva nota
        dialog = tk.Toplevel()
        dialog.title("Agregar Nota")

        # Campos de entrada para la nueva nota
        tk.Label(dialog, text="Título:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(dialog, font=("Arial", 12))
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Contenido:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        content_entry = tk.Text(dialog, width=50, height=10, font=("Arial", 12))
        content_entry.grid(row=1, column=1, padx=10, pady=5)

        # Función para agregar la nota a la base de datos
        def add_note_to_database():
            title = title_entry.get()
            content = content_entry.get("1.0", tk.END)  # Obtener el contenido desde la primera línea hasta el final
            # Insertar la nota en la base de datos
            self.sql_server_cursor.execute("INSERT INTO notas (title, content) VALUES (?, ?)", (title, content))
            self.sql_server_connection.commit()
            # Cargar las notas actualizadas en la lista
            self.load_notes()
            # Cerrar la ventana de diálogo
            dialog.destroy()

        # Botón para agregar la nota
        add_btn = tk.Button(dialog, text="Agregar", command=add_note_to_database, font=("Arial", 12))
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Enfocar el campo de título al abrir la ventana de diálogo
        title_entry.focus_set()

    def edit_note(self):
        # Verificar si se ha seleccionado una nota
        if not self.notes_listbox.curselection():
            messagebox.showwarning("Editar Nota", "Seleccione una nota para editar.")
            return

        # Obtener el índice de la nota seleccionada
        index = self.notes_listbox.curselection()
        selected_note_id = self.notes_listbox.get(index)[0]  # Obtener el ID de la nota

        # Obtener el título y el contenido de la nota desde la base de datos
        self.sql_server_cursor.execute("SELECT title, content FROM notas WHERE id=?", (selected_note_id,))
        note_data = self.sql_server_cursor.fetchone()

        # Abrir una ventana de diálogo para editar la nota seleccionada
        dialog = tk.Toplevel()
        dialog.title("Editar Nota")

        # Campos de entrada para la nota seleccionada
        tk.Label(dialog, text="Título:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(dialog, font=("Arial", 12))
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        title_entry.insert(tk.END, note_data[0])  # Insertar el título actual de la nota

        tk.Label(dialog, text="Contenido:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        content_entry = tk.Text(dialog, width=50, height=10, font=("Arial", 12))
        content_entry.grid(row=1, column=1, padx=10, pady=5)
        content_entry.insert(tk.END, note_data[1])  # Insertar el contenido actual de la nota

        # Función para guardar los cambios en la base de datos
        def save_changes():
            new_title = title_entry.get()
            new_content = content_entry.get("1.0", tk.END)
            # Actualizar la nota en la base de datos
            self.sql_server_cursor.execute("UPDATE notas SET title=?, content=? WHERE id=?", (new_title, new_content, selected_note_id))
            self.sql_server_connection.commit()
            # Cargar las notas actualizadas en la lista
            self.load_notes()
            # Cerrar la ventana de diálogo
            dialog.destroy()

        # Botón para guardar los cambios
        save_btn = tk.Button(dialog, text="Guardar Cambios", command=save_changes, font=("Arial", 12))
        save_btn.grid(row=2, column=0, columnspan=2, pady=10)


    def delete_note(self):
        # Verificar si se ha seleccionado una nota
        if not self.notes_listbox.curselection():
            messagebox.showwarning("Eliminar Nota", "Seleccione una nota para eliminar.")
            return

        # Confirmar la eliminación de la nota seleccionada
        confirmation = messagebox.askyesno("Eliminar Nota", "¿Está seguro de que desea eliminar esta nota? Esta acción no se puede deshacer.")
        if confirmation:
            # Obtener el índice de la nota seleccionada
            index = self.notes_listbox.curselection()
            selected_note_id = self.notes_listbox.get(index)[0]  # Obtener el ID de la nota
            # Eliminar la nota de la base de datos
            self.sql_server_cursor.execute("DELETE FROM notas WHERE id=?", (selected_note_id,))
            self.sql_server_connection.commit()
            
            # Recorrer los IDs restantes
            remaining_notes = self.notes_listbox.get(0, tk.END)
            for i, (note_id, _) in enumerate(remaining_notes, start=1):
                self.sql_server_cursor.execute("UPDATE notas SET id=? WHERE id=?", (i, note_id))
            self.sql_server_connection.commit()
            
            # Cargar las notas actualizadas en la lista
            self.load_notes()


        
    def create_fichas_section(self, tab):
        # Fichas Técnicas
        label = tk.Label(tab, text="Fichas Técnicas", font=("Arial", 18))
        label.pack(pady=10)

        # Crear el área de construcción de la ficha técnica
        construction_area = tk.Frame(tab, bd=2, relief=tk.GROOVE)
        construction_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Columna izquierda (Imagen y Especificaciones Técnicas)
        left_column = tk.Frame(construction_area)
        left_column.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Imagen
        self.create_image_viewer(left_column)

        # Especificaciones Técnicas
        self.create_specifications_input(left_column)

        # Columna derecha (Software, Extras y Periféricos)
        right_column = tk.Frame(construction_area)
        right_column.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

        # Software
        self.create_software_area(right_column, "Software")

        # Periféricos
        self.create_perifericos_area(right_column, "Periféricos")

        self.titulo(right_column, "Ultimos Toques")
        
        # Botón para generar el PDF
        self.create_pdf_button(right_column, construction_area)
        



    def create_specifications_input(self, parent):
        # Función para crear campos de entrada para especificaciones técnicas
        label = tk.Label(
            parent, text="Especificaciones Técnicas", font=("Arial", 14, "bold")
        )
        label.pack(pady=10)

        self.specifications_data = (
            {}
        )  # Crear un diccionario para almacenar los datos ingresados

        specifications = [
            "Pantalla:",
            "Procesador:",
            "RAM:",
            "Capacidad de Almacenamiento:",
            "Tarjeta Gráfica:",
        ]
        for spec in specifications:
            frame = tk.Frame(parent)
            frame.pack(pady=5, padx=10, fill=tk.X)

            label = tk.Label(frame, text=spec)
            label.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT)

            # Agregar una referencia al campo de entrada al diccionario
            self.specifications_data[spec] = entry

    def create_software_area(self, parent, title):
        # Función para crear campos de entrada para especificaciones software
        label = tk.Label(
            parent, text="Especificaciones De software", font=("Arial", 14, "bold")
        )
        label.pack(pady=10)

        self.software_data = (
            {}
        )  # Crear un diccionario para almacenar los datos ingresados

        specifications = [
            "Antivirus:",
            "Navegador:",
            "Sistema Operativo:",
            "Software De Produccion",
        ]
        for spec in specifications:
            frame = tk.Frame(parent)
            frame.pack(pady=5, padx=10, fill=tk.X)

            label = tk.Label(frame, text=spec)
            label.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT)

            # Agregar una referencia al campo de entrada al diccionario
            self.software_data[spec] = entry

    def create_perifericos_area(self, parent, title):
        # Función para crear campos de entrada para especificaciones software
        label = tk.Label(parent, text="Perifericos", font=("Arial", 14, "bold"))
        label.pack(pady=10)

        self.perifericos_data = (
            {}
        )  # Crear un diccionario para almacenar los datos ingresados

        specifications = ["Teclado:", "Monitor:", "Altavoces", "Mouse:"]
        for spec in specifications:
            frame = tk.Frame(parent)
            frame.pack(pady=5, padx=10, fill=tk.X)

            label = tk.Label(frame, text=spec)
            label.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT)

            # Agregar una referencia al campo de entrada al diccionario
            self.perifericos_data[spec] = entry

    def titulo(self, parent, title):
        # Función para crear campos de entrada para especificaciones software
        label = tk.Label(parent, text="Ultimos Detalles", font=("Arial", 14, "bold"))
        label.pack(pady=10)

        self.titulo_data = (
            {}
        )  # Crear un diccionario para almacenar los datos ingresados

        specifications = ["Nombre Del Equipo", "Fecha De ensamblaje"]
        for spec in specifications:
            frame = tk.Frame(parent)
            frame.pack(pady=5, padx=10, fill=tk.X)

            label = tk.Label(frame, text=spec)
            label.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT)

            # Agregar una referencia al campo de entrada al diccionario
            self.titulo_data[spec] = entry

    def create_image_viewer(self, parent):
        # Función para crear un área de visualización de imagen
        label = tk.Label(parent, text="Imagen del Equipo", font=("Arial", 14, "bold"))
        label.pack(pady=10)

        self.image_frame = tk.Frame(parent, bg="light gray", width=200, height=200)
        self.image_frame.pack(pady=10)

        self.load_image_button = tk.Button(
            parent, text="Cargar Imagen", command=self.load_image
        )
        self.load_image_button.pack(pady=5)

        # Botón para limpiar la imagen
        self.clear_image_button = tk.Button(
            parent, text="Limpiar Imagen", command=self.clear_image
        )
        self.clear_image_button.pack(pady=5)

    def clear_image(self):
        # Verificar si hay una imagen cargada
        if hasattr(self, 'image_path'):
            # Pedir confirmación para eliminar la imagen
            confirm = messagebox.askyesno("Eliminar Imagen", "¿Estás seguro de que deseas eliminar la imagen?")
            if confirm:
                # Eliminar la ruta de la imagen
                delattr(self, 'image_path')

                # Eliminar el widget Label que muestra la imagen
                if hasattr(self, 'image_label'):
                    self.image_label.destroy()

                print("Imagen eliminada.")
        else:
            messagebox.showinfo("Sin imagen", "No hay ninguna imagen cargada.")


    def load_image(self):
        # Verificar si ya hay una imagen cargada
        if hasattr(self, 'image_path'):
            # Si ya hay una imagen cargada, pedir confirmación para reemplazarla
            confirm = messagebox.askyesno("Reemplazar Imagen", "Ya hay una imagen cargada. ¿Deseas reemplazarla?")
            if not confirm:
                return

        # Pedir al usuario que seleccione una nueva imagen
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )

        if file_path:
            # Actualizar image_path con la ruta de la nueva imagen cargada
            self.image_path = file_path

            # Cargar y mostrar la nueva imagen en el widget Label existente
            image = Image.open(file_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            if hasattr(self, 'image_label'):  # Verificar si el widget Label ya existe
                # Actualizar la imagen en el widget Label existente
                self.image_label.configure(image=photo)
                self.image_label.image = photo  # Evitar que la imagen sea recolectada por el recolector de basura
            else:
                # Crear el widget Label si aún no existe
                self.image_label = tk.Label(self.image_frame, image=photo)
                self.image_label.image = photo  # Evitar que la imagen sea recolectada por el recolector de basura
                self.image_label.pack()

            print("Imagen cargada:", file_path)

    def create_pdf_button(self, parent, construction_area):
        # Función para crear un botón para generar el PDF
        pdf_button = tk.Button(
            parent,
            text="Generar PDF",
            command=lambda: self.generate_pdf(construction_area),
        )

        pdf_button.pack(pady=5)


    def generate_pdf(self, construction_area):
        # Obtener los datos ingresados por el usuario
        software = {spec: entry.get() for spec, entry in self.software_data.items()}
        perifericos = {spec: entry.get() for spec, entry in self.perifericos_data.items()}
        specifications = {spec: entry.get() for spec, entry in self.specifications_data.items()}
        titulo = {spec: entry.get() for spec, entry in self.titulo_data.items()}

        # Crear el documento PDF
        pdf_name = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
        )
        if pdf_name:
            doc = SimpleDocTemplate(pdf_name, pagesize=letter)

            # Estilos para el encabezado, pie de página y texto normal
            styles = getSampleStyleSheet()
            header_style = styles["Title"]
            normal_style = styles["BodyText"]

            elements = []

            # Encabezado
            header_text = "Ficha Técnica del Equipo"
            header = Paragraph(header_text, header_style)

            # Formatear los datos del título con un tamaño de letra más pequeño
            datos_titulo = "<br/>".join(
                [f"<font size='10'>{key}: {value}</font>" for key, value in titulo.items()]
            )
            datos_titulo = Paragraph(datos_titulo, normal_style)

            # Mantener el encabezado y los datos del título juntos
            encabezado_y_datos = KeepTogether([header, Spacer(1, 10), datos_titulo])
            elements.append(encabezado_y_datos)

            # Añadir la imagen
            if hasattr(self, 'image_path'):
                platypus_image = PlatypusImage(self.image_path, width=200, height=200)
                elements.append(platypus_image)

            elements.append(Spacer(1, 10))

            # Especificaciones Técnicas
            elements.append(Paragraph("<b>Especificaciones Técnicas</b>", normal_style))
            elements.append(Spacer(1, 10))  # Agregar un pequeño espacio
            data = [[spec, value] for spec, value in specifications.items()]
            table = Table(data, colWidths=[150, 150])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)

            # Espacio entre las tablas
            elements.append(Spacer(1, 20))

            # Especificaciones de Software
            elements.append(Paragraph("<b>Especificaciones de Software</b>", normal_style))
            elements.append(Spacer(1, 10))  # Agregar un pequeño espacio
            data = [[spec, value] for spec, value in software.items()]
            table = Table(data, colWidths=[150, 150])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)

            # Espacio entre las tablas
            elements.append(Spacer(1, 20))

            # Periféricos
            elements.append(Paragraph("<b>Periféricos</b>", normal_style))
            elements.append(Spacer(1, 10))  # Agregar un pequeño espacio
            data = [[spec, value] for spec, value in perifericos.items()]
            table = Table(data, colWidths=[150, 150])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)

            # Generar el PDF
            doc.build(elements)

            print("PDF guardado exitosamente.")


    def create_bitacora_section(self, tab):
        # Bitácora
        label = tk.Label(
            tab, text="Bitácora", font=("Arial", 24, "bold"), fg="#333"
        )
        label.pack(pady=10)

        # Marco para la lista de eventos con bordes
        event_frame = tk.Frame(tab, bd=2, relief=tk.GROOVE)
        event_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Lista de eventos con scrollbar
        self.event_list = tk.Listbox(
            event_frame, width=70, height=15, bd=0, highlightthickness=0, font=("Arial", 12)
        )
        self.event_list.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(event_frame, orient="vertical", command=self.event_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.event_list.config(yscrollcommand=scrollbar.set)
        self.event_list.bind("<Double-1>", self.show_event_details)

        # Menú desplegable para seleccionar el criterio de ordenamiento
        sort_label = tk.Label(tab, text="Ordenar por:")
        sort_label.pack()
        self.sort_criteria = ttk.Combobox(tab, values=["Fecha", "Descripción", "Estado"])
        self.sort_criteria.pack()
        self.sort_criteria.current(0)  # Seleccionar "Fecha" por defecto
        self.sort_criteria.bind("<<ComboboxSelected>>", self.sort_events_ui)  # Vincular evento

        # Botones
        button_frame = tk.Frame(tab)
        button_frame.pack(pady=10)

        # Estilo de los botones
        button_style = ttk.Style()
        button_style.configure("TButton", font=("Arial", 12))

        btn_add_event = ttk.Button(
            button_frame, text="Agregar Evento", style="Accent.TButton", command=self.add_event
        )
        btn_add_event.pack(side="left", padx=10)

        btn_modify_event = ttk.Button(
            button_frame, text="Modificar Evento", style="Accent.TButton", command=self.modify_event
        )
        btn_modify_event.pack(side="left", padx=10)

        btn_delete_event = ttk.Button(
            button_frame, text="Eliminar Evento", style="Accent.TButton", command=self.delete_event
        )
        btn_delete_event.pack(side="left", padx=10)

        btn_export_json = ttk.Button(
            button_frame, text="Exportar a JSON", style="Accent.TButton", command=self.export_to_json
        )
        btn_export_json.pack(side="left", padx=10)

        btn_import_json = ttk.Button(
            button_frame, text="Importar a JSON", style="Accent.TButton", command=self.import_from_json
        )
        btn_import_json.pack(side="left", padx=10)

    def add_event(self):
        # Crear una ventana emergente para agregar un nuevo evento
        event_window = tk.Toplevel(self.root)
        event_window.title("Agregar Evento")

        # Etiquetas y campos de entrada para agregar detalles del evento
        lbl_description = tk.Label(event_window, text="Descripción:")
        lbl_description.pack(pady=5)
        self.description_entry = ttk.Entry(event_window)
        self.description_entry.pack()

        lbl_responsible = tk.Label(event_window, text="Responsable:")
        lbl_responsible.pack(pady=5)
        self.responsible_entry = ttk.Entry(event_window)
        self.responsible_entry.pack()

        lbl_notes = tk.Label(event_window, text="Observaciones:")
        lbl_notes.pack(pady=5)
        self.notes_entry = tk.Text(event_window, width=40, height=6)
        self.notes_entry.pack()

        lbl_status = tk.Label(event_window, text="Estado:")
        lbl_status.pack(pady=5)
        self.status_entry = ttk.Combobox(event_window, values=["En Progreso", "Completado", "Pendiente"])
        self.status_entry.pack()

        btn_save_event = ttk.Button(event_window, text="Guardar Evento", command=self.save_event)
        btn_save_event.pack(pady=10)

    def modify_event(self):
        # Obtener el evento seleccionado en la lista
        selected_event_index = self.event_list.curselection()
        if selected_event_index:
            # Sumar 1 al índice obtenido para obtener el ID correcto del evento
            event_id = selected_event_index[0] + 1

            # Obtener los detalles del evento de la base de datos
            self.cursor.execute("SELECT * FROM bitacora WHERE id=?", (event_id,))
            event_data = self.cursor.fetchone()

            if event_data:
                # Crear una ventana emergente para modificar el evento
                event_window = tk.Toplevel(self.root)
                event_window.title("Modificar Evento")

                # Etiquetas y campos de entrada para modificar detalles del evento
                lbl_description = tk.Label(event_window, text="Descripción:")
                lbl_description.pack(pady=5)
                self.description_entry = ttk.Entry(event_window)
                self.description_entry.insert(tk.END, event_data[2])
                self.description_entry.pack()

                lbl_responsible = tk.Label(event_window, text="Responsable:")
                lbl_responsible.pack(pady=5)
                self.responsible_entry = ttk.Entry(event_window)
                self.responsible_entry.insert(tk.END, event_data[3])
                self.responsible_entry.pack()

                lbl_notes = tk.Label(event_window, text="Observaciones:")
                lbl_notes.pack(pady=5)
                self.notes_entry = tk.Text(event_window, width=40, height=6)
                self.notes_entry.insert(tk.END, event_data[4])
                self.notes_entry.pack()

                lbl_status = tk.Label(event_window, text="Estado:")
                lbl_status.pack(pady=5)
                self.status_entry = ttk.Combobox(event_window, values=["En Progreso", "Completado", "Pendiente"])
                self.status_entry.set(event_data[5])
                self.status_entry.pack()

                btn_save_event = ttk.Button(event_window, text="Guardar Cambios", command=lambda: self.save_modified_event(event_id))
                btn_save_event.pack(pady=10)
            else:
                messagebox.showerror("Error", "El evento seleccionado no existe en la base de datos.")
        else:
            messagebox.showerror("Error", "Por favor, seleccione un evento para modificar.")


    def delete_event(self):
        # Obtener el evento seleccionado en la lista
        selected_event_index = self.event_list.curselection()
        if selected_event_index:
            event_index = selected_event_index[0]  # Obtener el primer índice seleccionado
            event_details = self.event_list.get(event_index)
            event_id_match = re.search(r'ID: (\d+)', event_details)
            if event_id_match:
                event_id = int(event_id_match.group(1))

                # Confirmar la eliminación del evento
                confirm_delete = messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este evento?")
                if confirm_delete:
                    # Eliminar el evento de la base de datos
                    self.cursor.execute("DELETE FROM bitacora WHERE id=?", (event_id,))
                    self.connection.commit()

                    # Actualizar la lista de eventos
                    self.event_list.delete(event_index)  # Eliminar el evento de la lista
                    self.reorder_event_ids(event_index)  # Reorganizar los IDs de los eventos restantes
                    messagebox.showinfo("Éxito", "Evento eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo encontrar el ID del evento.")
        else:
            messagebox.showerror("Error", "Por favor, seleccione un evento para eliminar.")

    def reorder_event_ids(self, deleted_index):
        # Obtener todos los eventos de la base de datos
        self.cursor.execute("SELECT id FROM bitacora ORDER BY id")
        event_ids = [event[0] for event in self.cursor.fetchall()]

        # Reorganizar los IDs de los eventos restantes
        for i, event_id in enumerate(event_ids):
            if event_id > deleted_index:
                new_event_id = event_id - 1  # Decrementar el ID en 1
                self.cursor.execute("UPDATE bitacora SET id=? WHERE id=?", (new_event_id, event_id))
                self.connection.commit()

        # Actualizar la lista de eventos después de la reorganización
        self.update_event_list()


    def sort_events_ui(self, event=None):
        # Obtener el criterio de ordenamiento seleccionado por el usuario
        sort_criteria = self.sort_criteria.get()

        # Obtener todos los eventos de la base de datos
        self.cursor.execute("SELECT * FROM bitacora")
        events = self.cursor.fetchall()

        # Ordenar eventos según el criterio seleccionado
        if sort_criteria == "Fecha":
            sorted_events = sorted(events, key=lambda x: x[1], reverse=True)  # Ordenar por fecha
        elif sort_criteria == "Descripción":
            sorted_events = sorted(events, key=lambda x: x[2])  # Ordenar por descripción
        elif sort_criteria == "Estado":
            sorted_events = sorted(events, key=lambda x: x[5])  # Ordenar por estado

        # Actualizar la lista de eventos con los eventos ordenados
        self.update_event_list(sorted_events)
        
    def save_event(self):
        # Obtener los detalles del evento ingresados por el usuario
        description = self.description_entry.get()
        responsible = self.responsible_entry.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()
        status = self.status_entry.get()
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Verificar que la descripción y el responsable no estén vacíos
        if description and responsible:
            # Insertar el evento en la base de datos
            self.cursor.execute('''INSERT INTO bitacora (date_time, description, responsible, notes, status)
                                VALUES (?, ?, ?, ?, ?)''', (date_time, description, responsible, notes, status))
            self.connection.commit()

            # Actualizar la lista de eventos
            self.update_event_list()

            # Cerrar la ventana emergente
            self.description_entry.delete(0, tk.END)
            self.responsible_entry.delete(0, tk.END)
            self.notes_entry.delete("1.0", tk.END)
            self.status_entry.set("")
            messagebox.showinfo("Éxito", "Evento guardado correctamente.")
        else:
            messagebox.showerror("Error", "Por favor, complete la descripción y el responsable.")

    def save_modified_event(self, event_id):
        # Obtener los detalles del evento modificados por el usuario
        description = self.description_entry.get()
        responsible = self.responsible_entry.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()
        status = self.status_entry.get()

        # Verificar que la descripción y el responsable no estén vacíos
        if description and responsible:
            # Actualizar el evento en la base de datos
            self.cursor.execute('''UPDATE bitacora SET description=?, responsible=?, notes=?, status=?
                                WHERE id=?''', (description, responsible, notes, status, event_id))
            self.connection.commit()

            # Actualizar la lista de eventos
            self.update_event_list()

            # Cerrar la ventana emergente
            messagebox.showinfo("Éxito", "Evento modificado correctamente.")
        else:
            messagebox.showerror("Error", "Por favor, complete la descripción y el responsable.")

    def update_event_list(self, sorted_events=None):
        # Limpiar la lista de eventos
        self.event_list.delete(0, tk.END)

        # Obtener todos los eventos de la base de datos si no se proporciona una lista ordenada
        if sorted_events is None:
            self.cursor.execute("SELECT * FROM bitacora ORDER BY date_time DESC")
            events = self.cursor.fetchall()
        else:
            events = sorted_events

        # Agregar cada evento a la lista de eventos
        for event in events:
            event_id = event[0]
            date_time = event[1]
            description = event[2]
            event_details = f"ID: {event_id} | Fecha y Hora: {date_time} | Descripción: {description}"
            self.event_list.insert(tk.END, event_details)

    def show_event_details(self, event=None):
        # Obtener el índice del evento seleccionado en la lista
        selected_event_index = self.event_list.curselection()
        if selected_event_index:
            # Obtener el ID del evento seleccionado
            event_id = selected_event_index[0] + 1  # Sumar 1 para obtener el ID correcto (índice + 1)

            # Buscar el evento en la base de datos y obtener sus detalles
            event_details = self.get_event_details(event_id)

            if event_details:
                # Crear una ventana emergente para mostrar los detalles del evento
                event_window = tk.Toplevel(self.root)
                event_window.title("Detalles del Evento")

                # Crear una "card" para mostrar los detalles del evento
                card_frame = tk.Frame(event_window, bg="white", padx=10, pady=10, bd=2, relief=tk.RIDGE)
                card_frame.pack(fill=tk.BOTH, expand=True)

                # Mostrar los detalles del evento en la "card"
                lbl_date_time = tk.Label(card_frame, text=f"Fecha y Hora: {event_details['date_time']}", font=("Arial", 12), bg="white")
                lbl_date_time.pack(anchor="w", padx=5, pady=5)

                lbl_description = tk.Label(card_frame, text=f"Descripción: {event_details['description']}", font=("Arial", 12), bg="white")
                lbl_description.pack(anchor="w", padx=5, pady=5)

                lbl_responsible = tk.Label(card_frame, text=f"Responsable: {event_details['responsible']}", font=("Arial", 12), bg="white")
                lbl_responsible.pack(anchor="w", padx=5, pady=5)

                lbl_notes = tk.Label(card_frame, text=f"Observaciones: {event_details['notes']}", font=("Arial", 12), bg="white")
                lbl_notes.pack(anchor="w", padx=5, pady=5)

                lbl_status = tk.Label(card_frame, text=f"Estado: {event_details['status']}", font=("Arial", 12), bg="white")
                lbl_status.pack(anchor="w", padx=5, pady=5)
            else:
                messagebox.showerror("Error", "El evento seleccionado no existe en la base de datos.")
        else:
            messagebox.showerror("Error", "Por favor, seleccione un evento para ver los detalles.")

    def get_event_details(self, event_id):
        # Buscar el evento en la base de datos y obtener sus detalles
        event_details = {
            "date_time": "Desconocido",
            "description": "Desconocido",
            "responsible": "Desconocido",
            "notes": "Desconocido",
            "status": "Desconocido"
        }
        self.cursor.execute("SELECT * FROM bitacora WHERE id=?", (event_id,))
        event_data = self.cursor.fetchone()
        if event_data:
            event_details = {
                "date_time": event_data[1],
                "description": event_data[2],
                "responsible": event_data[3],
                "notes": event_data[4],
                "status": event_data[5]
            }
        return event_details

    def import_from_json(self):
        # Abrir un archivo JSON para importar eventos
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                # Leer los eventos desde el archivo JSON
                with open(file_path, "r") as json_file:
                    events_data = json.load(json_file)

                # Verificar si los eventos ya existen en la base de datos
                existing_events = set()
                self.cursor.execute("SELECT description, responsible, status FROM bitacora")
                for row in self.cursor.fetchall():
                    existing_events.add((row[0], row[1], row[2]))

                # Contadores para el seguimiento de eventos importados y eventos existentes
                imported_count = 0
                existing_count = 0

                # Insertar los eventos en la base de datos si no existen
                for event_data in events_data:
                    description = event_data["description"]
                    responsible = event_data["responsible"]
                    status = event_data["status"]
                    if (description, responsible, status) not in existing_events:
                        date_time = event_data["date_time"]
                        notes = event_data["notes"]
                        self.cursor.execute('''INSERT INTO bitacora (date_time, description, responsible, notes, status)
                                            VALUES (?, ?, ?, ?, ?)''', (date_time, description, responsible, notes, status))
                        imported_count += 1
                    else:
                        existing_count += 1
                self.connection.commit()

                # Actualizar la lista de eventos
                self.update_event_list()

                # Mostrar el mensaje con los recuentos
                messagebox.showinfo("Éxito", f"{imported_count} eventos importados correctamente. {existing_count} eventos ya existían y no fueron importados.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo importar eventos desde JSON: {str(e)}")
                print({str(e)})
                
    def export_to_json(self):
        # Obtener todos los eventos de la base de datos
        self.cursor.execute("SELECT * FROM bitacora ORDER BY date_time DESC")
        events = self.cursor.fetchall()

        # Convertir los eventos a un formato compatible con JSON
        events_json = []
        for event in events:
            event_dict = {
                "id": event[0],
                "date_time": event[1],
                "description": event[2],
                "responsible": event[3],
                "notes": event[4],
                "status": event[5]
            }
            events_json.append(event_dict)

        # Guardar los eventos en un archivo JSON
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w") as json_file:
                json.dump(events_json, json_file, indent=4)
            messagebox.showinfo("Éxito", "Bitácora exportada a JSON correctamente.")

    def __del__(self):
        # Cerrar la conexión a la base de datos al destruir la instancia
        self.connection.close()
        

    def create_inventario_section(self, tab):
        # Crear el contenedor principal
        inventory_frame = tk.Frame(tab)
        inventory_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(inventory_frame, text="Inventario", font=("Arial", 16, "bold"))
        title_label.pack()

        # Menú desplegable para exportar e importar
        export_import_frame = tk.Frame(inventory_frame)
        export_import_frame.pack(pady=(10, 0))

        export_import_menu = tk.Menubutton(export_import_frame, text="Menu Desplegable", font=("Arial", 12))
        export_import_menu.grid(row=0, column=0, padx=5)

        export_import_dropdown = tk.Menu(export_import_menu, tearoff=0)
        export_import_menu.config(menu=export_import_dropdown)

        export_import_dropdown.add_command(label="Exportar JSON", command=self.export_inventory_data_to_json)
        export_import_dropdown.add_command(label="Exportar CSV", command=self.export_inventory_data_to_csv)
        export_import_dropdown.add_separator()  
        export_import_dropdown.add_command(label="Importar JSON", command=self.import_inventory_data_from_json)
        export_import_dropdown.add_command(label="Importar CSV", command=self.import_inventory_data_from_csv)

        # Barra de búsqueda
        search_frame = tk.Frame(inventory_frame)
        search_frame.pack(pady=10)

        search_label = tk.Label(search_frame, text="Buscar Producto:", font=("Arial", 12))
        search_label.grid(row=0, column=0)

        self.search_entry = tk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.grid(row=0, column=1, padx=5)

        # Lista de productos
        product_list_frame = tk.Frame(inventory_frame)
        product_list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(product_list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.product_listbox = tk.Listbox(product_list_frame, width=50, height=15, font=("Arial", 12), yscrollcommand=scrollbar.set)
        self.product_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.product_listbox.yview)

        self.product_listbox.bind("<<ListboxSelect>>", self.show_product_details)

        # Detalles del producto
        detail_frame = tk.Frame(inventory_frame)
        detail_frame.pack(fill=tk.BOTH, expand=True)

        self.detail_label = tk.Label(detail_frame, text="Detalles del Producto:", font=("Arial", 14))
        self.detail_label.pack(pady=(10, 5), anchor=tk.W)

        self.detail_text = tk.Text(detail_frame, width=50, height=10, font=("Arial", 12), state="disabled")
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # Frame para los botones de acción
        action_btn_frame = tk.Frame(inventory_frame)
        action_btn_frame.pack(pady=10)

        # Botones de acción
        add_btn = tk.Button(action_btn_frame, text="Agregar Producto", command=self.add_product, font=("Arial", 12))
        add_btn.grid(row=0, column=0, padx=5)

        delete_btn = tk.Button(action_btn_frame, text="Eliminar Producto", command=self.delete_product, font=("Arial", 12))
        delete_btn.grid(row=0, column=1, padx=5)

        update_btn = tk.Button(action_btn_frame, text="Editar Producto", command=self.update_product, font=("Arial", 12))
        update_btn.grid(row=0, column=2, padx=5)


        # Conexión a la base de datos SQLite
        self.conn = sqlite3.connect('inventory.db')
        self.c = self.conn.cursor()

        # Crear tabla de productos si no existe
        self.c.execute('''CREATE TABLE IF NOT EXISTS productos (
                            id INTEGER PRIMARY KEY,
                            nombre TEXT NOT NULL,
                            cantidad INTEGER NOT NULL,
                            precio REAL NOT NULL
                            )''')
        self.conn.commit()

        # Mostrar productos en la lista al cargar la aplicación
        self.show_products()

    def show_product_details(self, event):
        # Obtener el índice del producto seleccionado en la lista
        selected_product_index = self.product_listbox.curselection()
        if selected_product_index:
            selected_product_name = self.product_listbox.get(selected_product_index[0])  # Obtener el nombre del producto seleccionado
            try:
                # Consultar la base de datos para obtener los detalles del producto seleccionado por su nombre
                self.c.execute("SELECT * FROM productos WHERE nombre=?", (selected_product_name,))
                product_details = self.c.fetchone()
                if product_details is not None:
                    # Mostrar los detalles del producto en la sección designada
                    details_text = f"Nombre: {product_details[1]}\n"
                    details_text += f"Cantidad: {product_details[2]}\n"
                    details_text += f"Precio: {product_details[3]}\n"
                    # Agregar más detalles aquí según sea necesario (descripción, proveedor, fecha de caducidad, etc.)
                    self.detail_text.config(state=tk.NORMAL)  # Habilitar la edición del texto
                    self.detail_text.delete(1.0, tk.END)  # Limpiar el texto anterior
                    self.detail_text.insert(tk.END, details_text)
                    self.detail_text.config(state=tk.DISABLED)  # Deshabilitar la edición del texto
                else:
                    self.detail_text.config(state=tk.NORMAL)  # Habilitar la edición del texto
                    self.detail_text.delete(1.0, tk.END)  # Limpiar el texto si no hay ningún producto seleccionado
                    self.detail_text.config(state=tk.DISABLED)  # Deshabilitar la edición del texto
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron obtener los detalles del producto: {e}")

    def show_products(self):
        # Limpiar la lista de productos
        self.product_listbox.delete(0, tk.END)

        # Consultar la base de datos para obtener todos los productos
        self.c.execute("SELECT * FROM productos")
        products = self.c.fetchall()

        # Mostrar los productos en la lista
        for product in products:
            self.product_listbox.insert(tk.END, product[1])  # Mostrar el nombre del producto en la lista

    def check_low_stock(self):
        # Establecer el umbral para el stock bajo
        low_stock_threshold = 10
        # Consultar la base de datos para obtener productos con stock bajo
        self.c.execute("SELECT * FROM productos WHERE cantidad < ?", (low_stock_threshold,))
        low_stock_products = self.c.fetchall()
        if low_stock_products:
            # Mostrar notificación de stock bajo
            low_stock_message = "Productos con stock bajo:\n"
            for product in low_stock_products:
                low_stock_message += f"{product[1]} - Cantidad: {product[2]}\n"
            # Puedes mostrar esta notificación como prefieras (mensaje emergente, alerta en la interfaz, etc.)
            print(low_stock_message)  # Por ahora, mostramos un mensaje en la consola

    def show_inventory_history(self):
        # Consultar la base de datos para obtener el historial de movimientos
        self.c.execute("SELECT * FROM historial_movimientos")
        inventory_history = self.c.fetchall()
        # Mostrar el historial de movimientos en la interfaz de usuario
        # Puedes mostrarlo en una nueva ventana, en una sección dedicada, etc.
        for entry in inventory_history:
            print(entry)  # Por ahora, mostramos el historial en la consola

    def export_inventory_data_to_json(self):
        # Consultar la base de datos para obtener todos los productos
        self.c.execute("SELECT * FROM productos")
        inventory_data = self.c.fetchall()
        # Crear una lista de diccionarios para representar los datos del inventario
        inventory_list = []
        for product in inventory_data:
            product_dict = {
                "id": product[0],
                "nombre": product[1],
                "cantidad": product[2],
                "precio": product[3]
            }
            inventory_list.append(product_dict)
        # Exportar los datos del inventario a un archivo JSON
        with open('inventory.json', 'w') as json_file:
            json.dump(inventory_list, json_file, indent=4)

    def export_inventory_data_to_csv(self):
        # Consultar la base de datos para obtener todos los productos
        self.c.execute("SELECT * FROM productos")
        inventory_data = self.c.fetchall()
        # Exportar los datos del inventario a un archivo CSV
        with open('inventory.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['ID', 'Nombre', 'Cantidad', 'Precio'])
            csv_writer.writerows(inventory_data)

    def import_inventory_data_from_json(self):
        # Abrir un cuadro de diálogo para que el usuario seleccione el archivo JSON
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:  # Verificar si se seleccionó un archivo
            # Leer los datos del archivo JSON
            with open(file_path, 'r') as json_file:
                inventory_list = json.load(json_file)
            # Insertar los datos en la base de datos
            for product in inventory_list:
                # Verificar si el producto ya existe en la base de datos
                self.c.execute("SELECT * FROM productos WHERE id=?", (product['id'],))
                existing_product = self.c.fetchone()
                if not existing_product:  # Si el producto no existe, insertarlo
                    self.c.execute("INSERT INTO productos (id, nombre, cantidad, precio) VALUES (?, ?, ?, ?)",
                                (product['id'], product['nombre'], product['cantidad'], product['precio']))
            self.conn.commit()

    def import_inventory_data_from_csv(self):
        # Abrir un cuadro de diálogo para que el usuario seleccione el archivo CSV
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:  # Verificar si se seleccionó un archivo
            # Leer los datos del archivo CSV
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Saltar la fila de encabezado si existe
                # Insertar los datos en la base de datos
                for row in csv_reader:
                    # Verificar si el producto ya existe en la base de datos
                    self.c.execute("SELECT * FROM productos WHERE id=?", (row[0],))
                    existing_product = self.c.fetchone()
                    if not existing_product:  # Si el producto no existe, insertarlo
                        self.c.execute("INSERT INTO productos (id, nombre, cantidad, precio) VALUES (?, ?, ?, ?)",
                                    (row[0], row[1], row[2], row[3]))
            self.conn.commit()

    def add_product(self):
        # Abrir una ventana de diálogo para que el usuario ingrese los detalles del nuevo producto
        dialog = tk.Toplevel()
        dialog.title("Agregar Producto")

        # Campos de entrada para el nuevo producto
        tk.Label(dialog, text="Nombre del Producto:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        name_entry = tk.Entry(dialog, font=("Arial", 12))
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Cantidad:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        quantity_entry = tk.Entry(dialog, font=("Arial", 12))
        quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Precio:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        price_entry = tk.Entry(dialog, font=("Arial", 12))
        price_entry.grid(row=2, column=1, padx=10, pady=5)

        # Función para agregar el producto a la base de datos y actualizar la interfaz de usuario
        def add_and_close():
            name = name_entry.get()
            quantity = int(quantity_entry.get())
            price = float(price_entry.get())
            # Insertar el nuevo producto en la base de datos
            self.c.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)", (name, quantity, price))
            self.conn.commit()
            # Actualizar la lista de productos en la interfaz de usuario
            self.show_products()
            # Cerrar la ventana de diálogo
            dialog.destroy()

        # Botón para agregar el producto
        tk.Button(dialog, text="Agregar", command=add_and_close, font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_product(self):
        # Obtener el producto seleccionado de la lista
        selected_product_index = self.product_listbox.curselection()
        if selected_product_index:
            if messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de que quieres eliminar este producto?"):
                selected_product_id = selected_product_index[0]  # Índice en la lista, no se necesita get() aquí
                try:
                    # Eliminar el producto de la base de datos
                    self.c.execute("DELETE FROM productos WHERE id=?", (selected_product_id + 1,))  # Ajustar el índice
                    # Actualizar los IDs de los productos siguientes
                    self.c.execute("UPDATE productos SET id = id - 1 WHERE id > ?", (selected_product_id + 1,))
                    self.conn.commit()
                    # Actualizar la lista de productos en la interfaz de usuario
                    self.show_products()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")


    def update_product(self):
        # Obtener el producto seleccionado de la lista
        selected_product_index = self.product_listbox.curselection()
        if selected_product_index:
            selected_product_id = selected_product_index[0]  # Índice en la lista, no se necesita get() aquí

            # Obtener los detalles actuales del producto seleccionado
            self.c.execute("SELECT * FROM productos WHERE id=?", (selected_product_id + 1,))  # Ajustar el índice
            product_details = self.c.fetchone()

            # Función para guardar los cambios y cerrar la ventana de diálogo
            def update_and_close():
                name = name_entry.get()
                quantity = quantity_entry.get()
                price = price_entry.get()

                if name and quantity and price:
                    try:
                        quantity = int(quantity)
                        price = float(price)
                        # Actualizar los detalles del producto en la base de datos
                        self.c.execute("UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id=?", (name, quantity, price, selected_product_id + 1))  # Ajustar el índice
                        self.conn.commit()
                        # Actualizar la lista de productos en la interfaz de usuario
                        self.show_products()
                        # Cerrar la ventana de diálogo
                        dialog.destroy()
                    except ValueError:
                        messagebox.showerror("Error", "Cantidad y precio deben ser números enteros o flotantes.")
                else:
                    messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")

            # Crear una ventana de diálogo para editar los detalles del producto seleccionado
            dialog = tk.Toplevel()
            dialog.title("Editar Producto")

            # Campos de entrada para editar el producto
            tk.Label(dialog, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
            name_entry = tk.Entry(dialog, font=("Arial", 12))
            name_entry.insert(0, product_details[1])
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(dialog, text="Cantidad:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
            quantity_entry = tk.Entry(dialog, font=("Arial", 12))
            quantity_entry.insert(0, product_details[2])
            quantity_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(dialog, text="Precio:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
            price_entry = tk.Entry(dialog, font=("Arial", 12))
            price_entry.insert(0, product_details[3])
            price_entry.grid(row=2, column=1, padx=10, pady=5)

            # Botón para guardar los cambios
            tk.Button(dialog, text="Guardar Cambios", command=update_and_close, font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10)


    def search_product(self, event=None):
        # Obtener el texto de búsqueda
        search_text = self.search_entry.get()

        # Limpiar la lista de productos
        self.product_listbox.delete(0, tk.END)

        # Consultar la base de datos para obtener productos que coincidan con el texto de búsqueda
        if search_text:
            try:
                self.c.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + search_text + '%',))
                matching_products = self.c.fetchall()

                # Mostrar los productos que coinciden con la búsqueda en la lista
                for product in matching_products:
                    self.product_listbox.insert(tk.END, product[1])  # Mostrar el nombre del producto en la lista
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {e}")
        else:
            # Si no hay texto de búsqueda, mostrar todos los productos
            self.show_products()



        
def main():
    root = tk.Tk()
    app = ProductManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
