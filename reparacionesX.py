from config import conectar_db
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END, messagebox, Frame
from tkcalendar import Calendar
from datetime import datetime

# Variables globales para almacenar IDs seleccionados
id_cliente_seleccionado = None
id_celular_seleccionado = None

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
    try:
        # Guardar la selección actual del celular para mantenerla si es posible
        selected_celular = lista_celulares.curselection() if lista_celulares.curselection() else None
        lista_celulares.delete(0, END)
        
        seleccion = lista_clientes.curselection()
        if seleccion:
            seleccion_texto = lista_clientes.get(seleccion)
            id_cliente_seleccionado = seleccion_texto.split(" - ")[0]
        else:
            id_cliente_seleccionado = None
            id_celular_seleccionado = None
            return

        if id_cliente_seleccionado:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id_celular, marca, modelo FROM celulares WHERE id_cliente=%s", (id_cliente_seleccionado,))
            celulares = cursor.fetchall()
            conn.close()
            for celular in celulares:
                lista_celulares.insert(END, f"{celular[0]} - {celular[1]} - {celular[2]}")
            
            # Restaurar la selección del celular si es posible
            if selected_celular and selected_celular[0] < lista_celulares.size():
                lista_celulares.selection_set(selected_celular[0])
                id_celular_seleccionado = lista_celulares.get(selected_celular[0]).split(" - ")[0]
            else:
                id_celular_seleccionado = None
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al cargar celulares: {e}")

# Crear una nueva reparación
def crear_reparacion():
    global id_celular_seleccionado
    try:
        # Usar la selección guardada en lugar de obtenerla nuevamente
        if id_celular_seleccionado is None:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un celular de la lista.")
            return
        
        id_celular = id_celular_seleccionado

        # Obtener los datos de la reparación
        fecha_ingreso = entry_fecha_ingreso.get()
        fecha_estimada_entrega = entry_fecha_estimada_entrega.get()
        estado = entry_estado.get()

        # Insertar en la base de datos
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reparaciones (id_celular, fecha_ingreso, fecha_estimada_entrega, estado) VALUES (%s, %s, %s, %s)",
            (id_celular, fecha_ingreso, fecha_estimada_entrega, estado),
        )
        conn.commit()
        conn.close()

        # Notificar éxito y limpiar campos
        messagebox.showinfo("Éxito", "Reparación creada exitosamente.")
        limpiar_campos()
        mostrar_reparaciones()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Mostrar reparaciones (sin cambios)
def mostrar_reparaciones():
    lista_reparaciones.delete(0, END)
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
        lista_reparaciones.insert(END, f"{reparacion[0]} - Cliente: {reparacion[1]} - Celular: {reparacion[2]} {reparacion[3]} - "
                                       f"Ingreso: {reparacion[4]} - Est. Entrega: {reparacion[5]} - Estado: {reparacion[6]}")

# Limpiar campos
def limpiar_campos():
    global id_cliente_seleccionado, id_celular_seleccionado
    entry_fecha_ingreso.delete(0, END)
    entry_fecha_estimada_entrega.delete(0, END)
    entry_estado.delete(0, END)
    # No limpiar la selección de clientes y celulares aquí, solo al confirmar el registro
    id_cliente_seleccionado = None
    id_celular_seleccionado = None

# Seleccionar fecha estimada de entrega con un calendario (sin cambios)
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

# Configuración de la ventana principal (sin cambios)
root = Tk()
root.title("Gestión de Reparaciones")
root.geometry("800x700")

# Frame para selección de cliente y celular (sin cambios)
frame_seleccion = Frame(root)
frame_seleccion.pack(pady=10)

def update_selected_celular(event=None):
    global id_celular_seleccionado
    try:
        seleccion = lista_celulares.curselection()
        if seleccion:
            id_celular_seleccionado = lista_celulares.get(seleccion[0]).split(" - ")[0]
        else:
            id_celular_seleccionado = None
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al seleccionar celular: {e}")

# Listbox para seleccionar cliente (corregido)
Label(frame_seleccion, text="Selecciona un Celular:").grid(row=0, column=1)
lista_celulares = Listbox(frame_seleccion, width=30)
lista_celulares.grid(row=1, column=1, padx=10)
lista_celulares.bind("<<ListboxSelect>>", update_selected_celular)

# Widgets para los datos de la reparación (sin cambios)
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

Label(root, text="Reparaciones Registradas:").pack()
lista_reparaciones = Listbox(root, width=80)
lista_reparaciones.pack(pady=10)

scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")
lista_reparaciones.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lista_reparaciones.yview)

cargar_clientes()
mostrar_reparaciones()

root.mainloop()