import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_query
import pandas as pd
import matplotlib.pyplot as plt

class EncuestasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Encuestas - Tkinter & MySQL")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f7f7f7")

        # Título
        title_label = tk.Label(self.root, text="Gestión de Encuestas", font=("Arial", 20, "bold"), bg="#f7f7f7", fg="#333")
        title_label.pack(pady=10)

        # Frame de Filtros
        filter_frame = tk.Frame(self.root, bg="#f7f7f7")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filtrar por:", bg="#f7f7f7", font=("Arial", 12)).grid(row=0, column=0, padx=10)
        self.filter_column = ttk.Combobox(filter_frame, values=[
            "Edad", "Sexo", "BebidasSemana", "CervezasSemana", 
            "BebidasFinSemana", "VinosSemana", "PerdidasControl"
        ])
        self.filter_column.grid(row=0, column=1, padx=10)
        self.filter_column.set("Seleccione columna")

        tk.Label(filter_frame, text="Condición:", bg="#f7f7f7", font=("Arial", 12)).grid(row=0, column=2, padx=10)
        self.filter_condition = ttk.Combobox(filter_frame, values=["=", ">", "<", ">=", "<="])
        self.filter_condition.grid(row=0, column=3, padx=10)
        self.filter_condition.set("Seleccione condición")

        tk.Label(filter_frame, text="Valor:", bg="#f7f7f7", font=("Arial", 12)).grid(row=0, column=4, padx=10)
        self.filter_value = tk.Entry(filter_frame)
        self.filter_value.grid(row=0, column=5, padx=10)

        tk.Button(filter_frame, text="Aplicar Filtro", command=self.apply_filter, bg="#4CAF50", fg="white").grid(row=0, column=6, padx=10)

        # Botones CRUD y Gráficos
        button_frame = tk.Frame(self.root, bg="#f7f7f7")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Insertar", command=self.insert_record, bg="#4CAF50", fg="white", width=15).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Actualizar", command=self.update_record, bg="#FFC107", fg="black", width=15).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Eliminar", command=self.delete_record, bg="#F44336", fg="white", width=15).grid(row=0, column=2, padx=10)
        tk.Button(button_frame, text="Exportar a Excel", command=self.export_to_excel, bg="#2196F3", fg="white", width=15).grid(row=0, column=3, padx=10)
        tk.Button(button_frame, text="Generar Gráfico", command=self.generate_graph, bg="#9C27B0", fg="white", width=15).grid(row=0, column=4, padx=10)

        # Tabla para mostrar datos
        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "idEncuesta", "edad", "Sexo", "BebidasSemana", "CervezasSemana", 
                "BebidasFinSemana", "BebidasDestiladasSemana", "VinosSemana", 
                "PerdidasControl", "DiversionDependenciaAlcohol", "ProblemasDigestivos", 
                "TensionAlta", "DolorCabeza"
            ),
            show="headings",
            height=15
        )
        self.tree.pack(fill="both", expand=True, pady=10)

        # Configuración de columnas
        columns = [
            ("idEncuesta", "ID Encuesta"),
            ("edad", "Edad"),
            ("Sexo", "Sexo"),
            ("BebidasSemana", "Bebidas/semana"),
            ("CervezasSemana", "Cervezas/semana"),
            ("BebidasFinSemana", "Bebidas Fin Semana"),
            ("BebidasDestiladasSemana", "Bebidas Destiladas"),
            ("VinosSemana", "Vinos/semana"),
            ("PerdidasControl", "Pérdidas Control"),
            ("DiversionDependenciaAlcohol", "Diversión Alcohol"),
            ("ProblemasDigestivos", "Problemas Digestivos"),
            ("TensionAlta", "Tensión Alta"),
            ("DolorCabeza", "Dolor Cabeza")
        ]
        for col_id, col_name in columns:
            self.tree.heading(col_id, text=col_name)
            self.tree.column(col_id, width=120, anchor="center")

        # Cargar datos iniciales
        self.populate_data()

    def populate_data(self):
        """Carga datos desde la base de datos y los muestra en la tabla."""
        self.tree.delete(*self.tree.get_children())  # Limpiar filas actuales
        query = "SELECT * FROM ENCUESTA"
        data = execute_query(query, fetch=True)
        for row in data:
            self.tree.insert("", "end", values=tuple(row.values()))

    def apply_filter(self):
        """Aplica un filtro basado en los campos seleccionados."""
        column = self.filter_column.get()
        condition = self.filter_condition.get()
        value = self.filter_value.get()

        if column == "Seleccione columna" or condition == "Seleccione condición" or not value:
            messagebox.showerror("Error", "Debes seleccionar una columna, condición y un valor para filtrar.")
            return

        # Construir consulta de filtro
        column_map = {
            "Edad": "edad",
            "Sexo": "Sexo",
            "BebidasSemana": "BebidasSemana",
            "CervezasSemana": "CervezasSemana",
            "BebidasFinSemana": "BebidasFinSemana",
            "VinosSemana": "VinosSemana",
            "PerdidasControl": "PerdidasControl"
        }
        sql_column = column_map.get(column, column)
        query = f"SELECT * FROM ENCUESTA WHERE {sql_column} {condition} %s"

        try:
            data = execute_query(query, (value,), fetch=True)
            self.tree.delete(*self.tree.get_children())  # Limpiar tabla
            for row in data:
                self.tree.insert("", "end", values=tuple(row.values()))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar el filtro: {e}")

    def export_to_excel(self):
        """Exporta los datos a un archivo Excel."""
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]

        if not rows:
            messagebox.showerror("Error", "No hay datos para exportar.")
            return

        # Convertir los datos a un DataFrame
        columns = [
            "ID Encuesta", "Edad", "Sexo", "Bebidas/semana", "Cervezas/semana",
            "Bebidas Fin Semana", "Bebidas Destiladas", "Vinos/semana",
            "Pérdidas Control", "Diversión Alcohol", "Problemas Digestivos",
            "Tensión Alta", "Dolor Cabeza"
        ]
        df = pd.DataFrame(rows, columns=columns)

        # Guardar en un archivo Excel
        try:
            df.to_excel("encuestas_exportadas.xlsx", index=False)
            messagebox.showinfo("Éxito", "Datos exportados a 'encuestas_exportadas.xlsx'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    def generate_graph(self):
        """Genera un gráfico basado en los datos actuales de la tabla."""
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]

        if not rows:
            messagebox.showerror("Error", "No hay datos para generar el gráfico.")
            return

        # Ventana para seleccionar tipo de gráfico
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Seleccionar Tipo de Gráfico")
        graph_window.geometry("300x200")

        def show_bar_chart():
            labels = [row[1] for row in rows]  # Ejemplo: Edad
            values = [row[3] for row in rows]  # Ejemplo: Bebidas/semana
            plt.bar(labels, values, color='skyblue')
            plt.title("Consumo de Bebidas por Edad")
            plt.xlabel("Edad")
            plt.ylabel("Bebidas/semana")
            plt.show()

        def show_pie_chart():
            labels = [row[2] for row in rows]  # Ejemplo: Sexo
            sizes = [row[3] for row in rows]  # Ejemplo: Bebidas/semana
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.title("Proporción de Bebidas por Sexo")
            plt.show()

        tk.Button(graph_window, text="Gráfico de Barras", command=show_bar_chart, width=20).pack(pady=10)
        tk.Button(graph_window, text="Gráfico Circular", command=show_pie_chart, width=20).pack(pady=10)

    def insert_record(self):
        """Inserta un nuevo registro."""
        insert_window = tk.Toplevel(self.root)
        insert_window.title("Insertar Registro")
        insert_window.geometry("600x600")

        # Configuración de campos
        fields = [
            "ID Encuesta", "Edad", "Sexo", "Bebidas/semana", "Cervezas/semana", 
            "Bebidas Fin Semana", "Bebidas Destiladas", "Vinos/semana", 
            "Pérdidas Control", "Diversión Alcohol", "Problemas Digestivos", 
            "Tensión Alta", "Dolor Cabeza"
        ]
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(insert_window, text=field).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(insert_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save_new_record():
            try:
                values = tuple(entry.get() for entry in entries.values())
                query = """
                    INSERT INTO ENCUESTA VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(query, values)
                messagebox.showinfo("Éxito", "Registro insertado correctamente.")
                insert_window.destroy()
                self.populate_data()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo insertar el registro: {e}")

        tk.Button(insert_window, text="Guardar", command=save_new_record, bg="#4CAF50", fg="white").grid(row=len(fields), columnspan=2, pady=10)

    def update_record(self):
        """Actualiza un registro seleccionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Actualizar", "Selecciona un registro para actualizar.")
            return

        current_values = self.tree.item(selected_item, "values")
        update_window = tk.Toplevel(self.root)
        update_window.title("Actualizar Registro")
        update_window.geometry("600x600")

        fields = [
            "ID Encuesta", "Edad", "Sexo", "Bebidas/semana", "Cervezas/semana", 
            "Bebidas Fin Semana", "Bebidas Destiladas", "Vinos/semana", 
            "Pérdidas Control", "Diversión Alcohol", "Problemas Digestivos", 
            "Tensión Alta", "Dolor Cabeza"
        ]
        entries = {}
        for i, (field, value) in enumerate(zip(fields, current_values)):
            tk.Label(update_window, text=field).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(update_window)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

    def delete_record(self):
        """Elimina un registro seleccionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Eliminar", "Selecciona un registro para eliminar.")
            return

        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este registro?")
        if not confirm:
            return

        record_id = self.tree.item(selected_item, "values")[0]
        try:
            query = "DELETE FROM ENCUESTA WHERE idEncuesta = %s"
            execute_query(query, (record_id,))
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
            self.populate_data()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")

# Ejecuta la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = EncuestasApp(root)
    root.mainloop()
