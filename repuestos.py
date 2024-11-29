from config import conectar_db
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END, messagebox

# Variables globales
id_repuesto_seleccionado = None  # Almacena el ID del repuesto seleccionado para actualizaciones/eliminaciones

# Crear Repuesto
def crear_repuesto():
    try:
        descripcion = entry_descripcion.get()
        costo = float(entry_costo.get())
        if descripcion and costo >= 0:
            conn = conectar_db()
            cursor = conn.cursor()
            # Inserta el repuesto sin requerir el ID manual
            cursor.execute("INSERT INTO repuestos (descripcion, costo) VALUES (%s, %s)", (descripcion, costo))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Repuesto agregado exitosamente.")
            entry_descripcion.delete(0, END)
            entry_costo.delete(0, END)
            mostrar_repuestos()
        else:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos correctamente.")
    except ValueError:
        messagebox.showerror("Error", "El costo debe ser un valor numérico.")

# Leer Repuestos
def obtener_repuestos():
    conn = conectar_db()
    cursor = conn.cursor()
    # Selecciona todos los repuestos
    cursor.execute("SELECT id_repuesto, descripcion, costo FROM repuestos")
    repuestos = cursor.fetchall()
    conn.close()
    return repuestos

# Mostrar Repuestos en Listbox
def mostrar_repuestos():
    lista_repuestos.delete(0, END)
    for repuesto in obtener_repuestos():
        lista_repuestos.insert(END, f"{repuesto[0]} - {repuesto[1]} - {repuesto[2]}")

# Actualizar Repuesto
def actualizar_repuesto():
    global id_repuesto_seleccionado
    if id_repuesto_seleccionado is None:
        messagebox.showwarning("Advertencia", "Selecciona un repuesto de la lista para actualizar.")
        return
    try:
        descripcion = entry_descripcion.get()
        costo = float(entry_costo.get())
        if descripcion and costo >= 0:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE repuestos SET descripcion=%s, costo=%s WHERE id_repuesto=%s",
                        (descripcion, costo, id_repuesto_seleccionado))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Repuesto actualizado exitosamente.")
            entry_descripcion.delete(0, END)
            entry_costo.delete(0, END)
            id_repuesto_seleccionado = None  # Reinicia la selección
            mostrar_repuestos()
        else:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos correctamente.")
    except ValueError:
        messagebox.showerror("Error", "El costo debe ser un valor numérico.")

# Eliminar Repuesto
def eliminar_repuesto():
    global id_repuesto_seleccionado
    if id_repuesto_seleccionado is None:
        messagebox.showwarning("Advertencia", "Selecciona un repuesto de la lista para eliminar.")
        return
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM repuestos WHERE id_repuesto=%s", (id_repuesto_seleccionado,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Repuesto eliminado exitosamente.")
        entry_descripcion.delete(0, END)
        entry_costo.delete(0, END)
        id_repuesto_seleccionado = None  # Reinicia la selección
        mostrar_repuestos()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Función para manejar la selección en la lista
def seleccionar_repuesto(event):
    global id_repuesto_seleccionado
    try:
        seleccion = lista_repuestos.get(lista_repuestos.curselection())
        id_repuesto, descripcion, costo = seleccion.split(" - ")
        id_repuesto_seleccionado = int(id_repuesto)  # Guarda el ID seleccionado
        entry_descripcion.delete(0, END)
        entry_descripcion.insert(END, descripcion)
        entry_costo.delete(0, END)
        entry_costo.insert(END, costo)
    except Exception as e:
        messagebox.showerror("Error", f"Error al seleccionar el repuesto: {e}")

# Configuración de la ventana principal
root = Tk()
root.title("Gestión de Repuestos")
root.geometry("500x500")

# Widgets para el CRUD de Repuestos
Label(root, text="Descripción").pack()
entry_descripcion = Entry(root)
entry_descripcion.pack()

Label(root, text="Costo").pack()
entry_costo = Entry(root)
entry_costo.pack()

# Botones de acción
Button(root, text="Agregar Repuesto", command=crear_repuesto).pack(pady=5)
Button(root, text="Actualizar Repuesto", command=actualizar_repuesto).pack(pady=5)
Button(root, text="Eliminar Repuesto", command=eliminar_repuesto).pack(pady=5)

# Listbox para mostrar repuestos
lista_repuestos = Listbox(root, width=60)
lista_repuestos.pack(pady=10)

# Scrollbar para Listbox
scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")
lista_repuestos.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lista_repuestos.yview)

# Cargar lista de repuestos y manejar selección
lista_repuestos.bind("<<ListboxSelect>>", seleccionar_repuesto)
mostrar_repuestos()

# Iniciar el loop de Tkinter
root.mainloop()