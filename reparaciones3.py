from config import conectar_db
from tkinter import Tk, Label, Entry, Button, Listbox, END, messagebox, Frame
from tkinter.ttk import Treeview, Scrollbar
from tkcalendar import Calendar
from datetime import datetime

# Variables globales
id_cliente_seleccionado = None
id_celular_seleccionado = None

# Funciones

# Cargar clientes en el Listbox
def cargar_clientes():
    lista_clientes.delete(0, END)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nombre FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    for cliente in clientes:
        lista_clientes.insert(END, f"{cliente[0]} - {cliente[1]}")

# Cargar celulares del cliente seleccionado
def cargar_celulares(event):
    global id_cliente_seleccionado, id_celular_seleccionado
    seleccion = lista_clientes.curselection()

    if not seleccion:
        id_cliente_seleccionado = None
        lista_celulares.delete(0, END)
        return

    seleccion_texto = lista_clientes.get(seleccion)
    id_cliente_seleccionado = seleccion_texto.split(" - ")[0]  # Extraer el ID del cliente
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_celular, marca, modelo FROM celulares WHERE id_cliente=%s", (id_cliente_seleccionado,))
    celulares = cursor.fetchall()
    conn.close()

    # Limpiar y rellenar lista de celulares
    lista_celulares.delete(0, END)
    for celular in celulares:
        lista_celulares.insert(END, f"{celular[0]} - {celular[1]} - {celular[2]}")

    # Mantener selección previa si existe
    if id_celular_seleccionado:
        for index in range(lista_celulares.size()):
            if id_celular_seleccionado in lista_celulares.get(index):
                lista_celulares.select_set(index)
                break

# Registrar reparación
def crear_reparacion():
    global id_celular_seleccionado
    seleccion = lista_celulares.curselection()

    if not seleccion:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un celular de la lista.")
        return

    seleccion_celular = lista_celulares.get(seleccion)
    id_celular_seleccionado = seleccion_celular.split(" - ")[0]

    # Obtener los datos ingresados
    fecha_ingreso = entry_fecha_ingreso.get()
    fecha_estimada_entrega = entry_fecha_estimada_entrega.get()

    if not fecha_ingreso or not fecha_estimada_entrega:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos de fecha.")
        return

    # Insertar la reparación en la base de datos
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reparaciones (id_celular, fecha_ingreso, fecha_estimada_entrega, estado) VALUES (%s, %s, %s, %s)",
            (id_celular_seleccionado, fecha_ingreso, fecha_estimada_entrega, "En proceso")
        )
        conn.commit()
        messagebox.showinfo("Éxito", "Reparación registrada exitosamente.")
        limpiar_campos()
        mostrar_reparaciones()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al registrar la reparación: {e}")
    finally:
        conn.close()

# Mostrar reparaciones en la grilla
def mostrar_reparaciones():
    for item in tree_reparaciones.get_children():
        tree_reparaciones.delete(item)

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT reparaciones.id_reparacion, clientes.nombre, celulares.marca, celulares.modelo, 
               reparaciones.fecha_ingreso, reparaciones.fecha_estimada_entrega, reparaciones.estado 
        FROM reparaciones 
        JOIN celulares ON reparaciones.id_celular = celulares.id_celular
        JOIN clientes ON celulares.id_cliente = clientes.id_cliente
    """)
    reparaciones = cursor.fetchall()
    conn.close()

    for reparacion in reparaciones:
        tree_reparaciones.insert("", END, values=reparacion)

# Limpiar campos
def limpiar_campos():
    global id_cliente_seleccionado, id_celular_seleccionado
    entry_fecha_ingreso.delete(0, END)
    entry_fecha_estimada_entrega.delete(0, END)
    lista_clientes.selection_clear(0, END)
    lista_celulares.delete(0, END)
    id_cliente_seleccionado = None
    id_celular_seleccionado = None

# Abrir calendario para seleccionar fecha
def abrir_calendario(campo):
    def seleccionar_fecha():
        campo.delete(0, END)
        campo.insert(0, cal.selection_get().strftime("%Y-%m-%d"))
        top_cal.destroy()

    top_cal = Tk()
    top_cal.title("Seleccionar Fecha")
    cal = Calendar(top_cal, date_pattern="yyyy-mm-dd", selectmode="day")
    cal.pack(pady=10)
    Button(top_cal, text="Seleccionar", command=seleccionar_fecha).pack(pady=10)

# Configuración de la ventana principal
root = Tk()
root.title("Gestión de Reparaciones")
root.geometry("900x600")

# Frame para la sección de reparaciones
frame_reparaciones = Frame(root)
frame_reparaciones.pack(pady=10, fill="both", expand=True)

# Crear Treeview para mostrar reparaciones
tree_reparaciones = Treeview(
    frame_reparaciones,
    columns=("ID", "Cliente", "Marca", "Modelo", "Fecha Ingreso", "Fecha Estimada", "Estado"),
    show="headings",
    height=10
)
tree_reparaciones.pack(side="left", fill="both", expand=True)

# Configurar encabezados de columnas
tree_reparaciones.heading("ID", text="ID Reparación")
tree_reparaciones.heading("Cliente", text="Cliente")
tree_reparaciones.heading("Marca", text="Marca")
tree_reparaciones.heading("Modelo", text="Modelo")
tree_reparaciones.heading("Fecha Ingreso", text="Fecha Ingreso")
tree_reparaciones.heading("Fecha Estimada", text="Fecha Estimada")
tree_reparaciones.heading("Estado", text="Estado")

# Configurar tamaño de las columnas
tree_reparaciones.column("ID", width=100, anchor="center")
tree_reparaciones.column("Cliente", width=150, anchor="center")
tree_reparaciones.column("Marca", width=100, anchor="center")
tree_reparaciones.column("Modelo", width=100, anchor="center")
tree_reparaciones.column("Fecha Ingreso", width=120, anchor="center")
tree_reparaciones.column("Fecha Estimada", width=120, anchor="center")
tree_reparaciones.column("Estado", width=100, anchor="center")

# Añadir barra de desplazamiento para el Treeview
scroll_reparaciones = Scrollbar(frame_reparaciones, orient="vertical", command=tree_reparaciones.yview)
scroll_reparaciones.pack(side="right", fill="y")
tree_reparaciones.config(yscrollcommand=scroll_reparaciones.set)

# Frame para selección de cliente y celular
frame_seleccion = Frame(root)
frame_seleccion.pack(pady=10)

Label(frame_seleccion, text="Selecciona un Cliente:").grid(row=0, column=0, padx=5)
lista_clientes = Listbox(frame_seleccion, width=30)
lista_clientes.grid(row=1, column=0, padx=5)
lista_clientes.bind("<<ListboxSelect>>", cargar_celulares)

Label(frame_seleccion, text="Selecciona un Celular:").grid(row=0, column=1, padx=5)
lista_celulares = Listbox(frame_seleccion, width=30)
lista_celulares.grid(row=1, column=1, padx=5)

# Otros widgets y configuraciones para fechas
frame_fechas = Frame(root)
frame_fechas.pack(pady=10)

Label(frame_fechas, text="Fecha de Ingreso:").grid(row=0, column=0, padx=5)
entry_fecha_ingreso = Entry(frame_fechas)
entry_fecha_ingreso.grid(row=0, column=1, padx=5)
Button(frame_fechas, text="Seleccionar Fecha", command=lambda: abrir_calendario(entry_fecha_ingreso)).grid(row=0, column=2, padx=5)

Label(frame_fechas, text="Fecha Estimada de Entrega:").grid(row=1, column=0, padx=5)
entry_fecha_estimada_entrega = Entry(frame_fechas)
entry_fecha_estimada_entrega.grid(row=1, column=1, padx=5)
Button(frame_fechas, text="Seleccionar Fecha", command=lambda: abrir_calendario(entry_fecha_estimada_entrega)).grid(row=1, column=2, padx=5)

# Botón para registrar reparación
Button(root, text="Registrar Reparación", command=crear_reparacion).pack(pady=10)

# Cargar datos iniciales
cargar_clientes()
mostrar_reparaciones()

root.mainloop()
