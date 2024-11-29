from config import conectar_db
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END, messagebox

# Crear Cliente
def crear_cliente():
    nombre = entry_nombre.get()
    contacto = entry_contacto.get()
    if nombre and contacto:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, contacto) VALUES (%s, %s)", (nombre, contacto))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Cliente creado exitosamente.")
        entry_nombre.delete(0, END)
        entry_contacto.delete(0, END)
        mostrar_clientes()
    else:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")

# Leer Clientes
def obtener_clientes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

# Mostrar Clientes en Listbox
def mostrar_clientes():
    lista_clientes.delete(0, END)
    for cliente in obtener_clientes():
        lista_clientes.insert(END, f"{cliente[0]} - {cliente[1]} - {cliente[2]}")

# Actualizar Cliente
def actualizar_cliente():
    try:
        id_cliente = entry_id.get()  # Obtener id_cliente desde el campo entry_id (que ahora está enabled temporalmente)
        nombre = entry_nombre.get()
        contacto = entry_contacto.get()
        if id_cliente and nombre and contacto:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE clientes SET nombre=%s, contacto=%s WHERE id_cliente=%s", (nombre, contacto, id_cliente))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cliente actualizado exitosamente.")
            entry_id.delete(0, END)
            entry_nombre.delete(0, END)
            entry_contacto.delete(0, END)
            mostrar_clientes()
        else:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
    except ValueError:
        messagebox.showerror("Error", "Por favor, selecciona un cliente válido.")

# Eliminar Cliente
def eliminar_cliente():
    try:
        id_cliente = entry_id.get()  # Obtener id_cliente desde el campo entry_id
        if id_cliente:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id_cliente=%s", (id_cliente,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cliente eliminado exitosamente.")
            entry_id.delete(0, END)
            entry_nombre.delete(0, END)
            entry_contacto.delete(0, END)
            mostrar_clientes()
        else:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un cliente.")
    except ValueError:
        messagebox.showerror("Error", "Por favor, selecciona un cliente válido.")

# Función para manejar la selección en la lista
def seleccionar_cliente(event):
    seleccion = lista_clientes.get(lista_clientes.curselection())
    id_cliente, nombre, contacto = seleccion.split(" - ")
    entry_id.config(state="normal")  # Habilitar temporalmente el campo entry_id
    entry_id.delete(0, END)
    entry_id.insert(END, id_cliente)
    entry_id.config(state="readonly")  # Volver a desactivar el campo entry_id para evitar ediciones accidentales
    entry_nombre.delete(0, END)
    entry_nombre.insert(END, nombre)
    entry_contacto.delete(0, END)
    entry_contacto.insert(END, contacto)

# Configuración de la ventana principal
root = Tk()
root.title("Gestión de Clientes")
root.geometry("400x400")

# Widgets para el CRUD de Clientes (campo de entrada para ID Cliente en estado readonly)
entry_id = Entry(root, state="readonly")  # Almacena el ID del cliente seleccionado
entry_id.pack_forget()  # Ocultar entry_id, ya que solo se usa internamente para seleccionar el ID

Label(root, text="Nombre").pack()
entry_nombre = Entry(root)
entry_nombre.pack()

Label(root, text="Contacto").pack()
entry_contacto = Entry(root)
entry_contacto.pack()

# Botones de acción
Button(root, text="Crear Cliente", command=crear_cliente).pack(pady=5)
Button(root, text="Actualizar Cliente", command=actualizar_cliente).pack(pady=5)
Button(root, text="Eliminar Cliente", command=eliminar_cliente).pack(pady=5)

# Listbox para mostrar clientes
lista_clientes = Listbox(root, width=50)
lista_clientes.pack(pady=10)

# Scrollbar para Listbox
scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")
lista_clientes.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lista_clientes.yview)

# Cargar lista de clientes y manejar selección
lista_clientes.bind("<<ListboxSelect>>", seleccionar_cliente)
mostrar_clientes()

# Iniciar el loop de Tkinter
root.mainloop()
