from config import conectar_db
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END, messagebox, Frame


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
    lista_celulares.delete(0, END)
    seleccion = lista_clientes.get(lista_clientes.curselection())
    id_cliente = seleccion.split(" - ")[0]
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_celular, marca, modelo FROM celulares WHERE id_cliente=%s", (id_cliente,))
    celulares = cursor.fetchall()
    conn.close()
    for celular in celulares:
        lista_celulares.insert(END, f"{celular[0]} - {celular[1]} {celular[2]}")


# Crear una nueva reparación
def crear_reparacion():
    try:
        seleccion_celular = lista_celulares.get(lista_celulares.curselection())
        id_celular = seleccion_celular.split(" - ")[0]
        fecha_ingreso = entry_fecha_ingreso.get()
        fecha_estimada_entrega = entry_fecha_estimada_entrega.get()
        estado = entry_estado.get()

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reparaciones (id_celular, fecha_ingreso, fecha_estimada_entrega, estado) VALUES (%s, %s, %s, %s)",
            (id_celular, fecha_ingreso, fecha_estimada_entrega, estado),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Reparación creada exitosamente.")
        limpiar_campos()
        mostrar_reparaciones()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")


# Mostrar reparaciones
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
    entry_fecha_ingreso.delete(0, END)
    entry_fecha_estimada_entrega.delete(0, END)
    entry_estado.delete(0, END)
    lista_clientes.selection_clear(0, END)
    lista_celulares.delete(0, END)


# Configuración de la ventana principal
root = Tk()
root.title("Gestión de Reparaciones")
root.geometry("700x700")

# Frame para selección de cliente y celular
frame_seleccion = Frame(root)
frame_seleccion.pack(pady=10)

# Listbox para seleccionar cliente
Label(frame_seleccion, text="Selecciona un Cliente:").grid(row=0, column=0)
lista_clientes = Listbox(frame_seleccion, width=30)
lista_clientes.grid(row=1, column=0, padx=10)
lista_clientes.bind("<<ListboxSelect>>", cargar_celulares)

# Listbox para seleccionar celular del cliente
Label(frame_seleccion, text="Selecciona un Celular:").grid(row=0, column=1)
lista_celulares = Listbox(frame_seleccion, width=30)
lista_celulares.grid(row=1, column=1, padx=10)

# Widgets para los datos de la reparación
Label(root, text="Fecha Ingreso (YYYY-MM-DD):").pack()
entry_fecha_ingreso = Entry(root)
entry_fecha_ingreso.pack()

Label(root, text="Fecha Estimada de Entrega (YYYY-MM-DD):").pack()
entry_fecha_estimada_entrega = Entry(root)
entry_fecha_estimada_entrega.pack()

Label(root, text="Estado:").pack()
entry_estado = Entry(root)
entry_estado.insert(0, "En proceso")  # Valor predeterminado
entry_estado.pack()

# Botón para agregar reparación
Button(root, text="Agregar Reparación", command=crear_reparacion).pack(pady=10)

# Listbox para mostrar reparaciones
Label(root, text="Reparaciones Registradas:").pack()
lista_reparaciones = Listbox(root, width=80)
lista_reparaciones.pack(pady=10)

# Scrollbar para el Listbox
scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")
lista_reparaciones.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lista_reparaciones.yview)

# Cargar datos iniciales
cargar_clientes()
mostrar_reparaciones()

# Iniciar loop de Tkinter
root.mainloop()
