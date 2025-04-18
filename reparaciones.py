from config import conectar_db
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END, messagebox, Frame
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime

# Variables globales
id_cliente_seleccionado = None
id_celular_seleccionado = None

# Función para cargar clientes en el Listbox
def cargar_clientes():
    lista_clientes.delete(0, END)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nombre FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    for cliente in clientes:
        lista_clientes.insert(END, f"{cliente[0]} - {cliente[1]}")

# Función para cargar celulares del cliente seleccionado
def cargar_celulares(event):
    global id_cliente_seleccionado, id_celular_seleccionado

    seleccion_cliente = lista_clientes.curselection()
    seleccion_texto = lista_clientes.get(seleccion_cliente)
    id_cliente_seleccionado = seleccion_texto.split(" - ")[0]  # Extraer el ID del cliente
    
    if not id_cliente_seleccionado:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un cliente.")
        return
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_celular, marca, modelo FROM celulares WHERE id_cliente=%s", (id_cliente_seleccionado,))
    celulares = cursor.fetchall()
    conn.close()

    lista_celulares.delete(0, END)
    for celular in celulares:
        lista_celulares.insert(END, f"{celular[0]} - {celular[1]} - {celular[2]}")

# Función para crear una nueva reparación
def crear_reparacion():
    global id_celular_seleccionado

    seleccion_celular = lista_celulares.curselection()
    if not seleccion_celular:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un celular.")
        return

    seleccion_texto = lista_celulares.get(seleccion_celular)
    id_celular_seleccionado = seleccion_texto.split(" - ")[0]  # Extraer el ID del celular

    # Obtener datos de la reparación
    fecha_ingreso = entry_fecha_ingreso.get()
    fecha_estimada_entrega = entry_fecha_estimada_entrega.get()
    estado = entry_estado.get()

    if not fecha_ingreso or not fecha_estimada_entrega or not estado:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
        return

    # Insertar la reparación en la base de datos
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reparaciones (id_celular, fecha_ingreso, fecha_estimada_entrega, estado) VALUES (%s, %s, %s, %s)",
            (id_celular_seleccionado, fecha_ingreso, fecha_estimada_entrega, estado),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Reparación registrada exitosamente.")
        limpiar_campos()
        mostrar_reparaciones()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar la reparación: {e}")

# Función para mostrar reparaciones en el Treeview
def mostrar_reparaciones():
    tree_reparaciones.delete(*tree_reparaciones.get_children())
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
        tree_reparaciones.insert("", END, values=(
            reparacion[0], reparacion[1], reparacion[2], reparacion[3], reparacion[4], reparacion[5], reparacion[6]
        ))

# Función para limpiar los campos y mantener las selecciones
def limpiar_campos():
    entry_fecha_ingreso.delete(0, END)
    entry_fecha_ingreso.insert(0, datetime.now().strftime("%Y-%m-%d"))
    entry_fecha_estimada_entrega.delete(0, END)
    entry_estado.delete(0, END)
    entry_estado.insert(0, "En proceso")

# Función para abrir el calendario
def abrir_calendario():
    def seleccionar_fecha():
        entry_fecha_estimada_entrega.delete(0, END)
        entry_fecha_estimada_entrega.insert(0, cal.selection_get().strftime("%Y-%m-%d"))
        top_cal.destroy()

    top_cal = Tk()
    top_cal.title("Seleccionar Fecha")
    cal = Calendar(top_cal, date_pattern="yyyy-mm-dd", selectmode="day")
    cal.pack(pady=10)
    Button(top_cal, text="Seleccionar", command=seleccionar_fecha).pack(pady=10)

# Configuración de la ventana principal
root = Tk()
root.title("Gestión de Reparaciones")
root.geometry("900x700")

# Sección de selección de clientes y celulares
frame_seleccion = Frame(root)
frame_seleccion.pack(pady=10)

Label(frame_seleccion, text="Selecciona un Cliente:").grid(row=0, column=0)
lista_clientes = Listbox(frame_seleccion, width=30)
lista_clientes.grid(row=1, column=0, padx=10)
lista_clientes.bind("<<ListboxSelect>>", cargar_celulares)

Label(frame_seleccion, text="Selecciona un Celular:").grid(row=0, column=1)
lista_celulares = Listbox(frame_seleccion, width=30)
lista_celulares.grid(row=1, column=1, padx=10)

# Sección para los datos de la reparación
Label(root, text="Fecha Ingreso (YYYY-MM-DD):").pack()
entry_fecha_ingreso = Entry(root)
entry_fecha_ingreso.insert(0, datetime.now().strftime("%Y-%m-%d"))
entry_fecha_ingreso.pack()

Label(root, text="Fecha Estimada de Entrega (YYYY-MM-DD):").pack()
entry_fecha_estimada_entrega = Entry(root)
entry_fecha_estimada_entrega.pack()

Button(root, text="📅", command=abrir_calendario).pack()

Label(root, text="Estado:").pack()
entry_estado = Entry(root)
entry_estado.insert(0, "En proceso")
entry_estado.pack()

Button(root, text="Agregar Reparación", command=crear_reparacion).pack(pady=10)

# Configurar el Treeview para mostrar reparaciones
columns = ("ID", "Cliente", "Marca", "Modelo", "Fecha Ingreso", "Fecha Estimada", "Estado")
tree_reparaciones = ttk.Treeview(root, columns=columns, show="headings", height=15)

for col in columns:
    tree_reparaciones.heading(col, text=col)
    tree_reparaciones.column(col, width=120, anchor="center")

tree_reparaciones.pack(pady=10, fill="x")

# Cargar datos iniciales
cargar_clientes()
mostrar_reparaciones()

root.mainloop()
