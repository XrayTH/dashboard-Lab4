import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from sklearn.cluster import KMeans  # Importamos KMeans
from controlador import obtener_todos_beneficiarios

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Distribución de Beneficiarios por Año")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f2f2f2')

        # Crear un Frame para los botones
        self.button_frame = ttk.Frame(self.root, padding=10)
        self.button_frame.grid(row=0, column=0, sticky="ew")

        # Crear un diccionario para los botones y sus comandos
        button_commands = {
            "Número total de beneficiarios": self.total_beneficiarios,
            "Distribución por departamento": self.distribucion_por_departamento,
            "Tipos de incentivos recibidos": self.tipos_incentivos_recibidos,
            "Variación de beneficiarios en el tiempo": self.variacion_beneficiarios_tiempo,
            "Relación entre tipo de incentivo y nivel educativo": self.relacion_incentivo_educacion,
            "Clustering de Beneficiarios": self.clustering_beneficiarios  # Nuevo botón
        }

        # Crear botones utilizando el diccionario
        for i, (text, command) in enumerate(button_commands.items()):
            button = ttk.Button(self.button_frame, text=text, command=command)
            button.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            button.config(width=30, style="TButton")

        # Estilo de botones
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Arial', 10))
        style.map("TButton", background=[('active', '#4CAF50')])  # Color al hacer hover

        # Crear un Frame para los gráficos
        self.canvas_graficos = tk.Frame(self.root, bg='#f2f2f2')
        self.canvas_graficos.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Asegurar que el Frame de gráficos se expanda
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Cargar datos con control de errores
        try:
            self.data = self.cargar_datos()
        except Exception as e:
            self.mostrar_mensaje(f"Error al cargar datos: {e}")
            self.data = pd.DataFrame()  # Cargar un DataFrame vacío si hay error

    def cargar_datos(self):
        try:
            beneficiarios = obtener_todos_beneficiarios()
            columnas = [
                'id', 'CodigoDepartamentoAtencion', 'EstadoBeneficiario',
                'FechaInscripcionBeneficiario', 'Genero', 'NivelEscolaridad',
                'NombreDepartamentoAtencion', 'TipoAsignacionBeneficio', 
                'TipoBeneficio', 'RangoBeneficioConsolidadoAsignado', 
                'RangoEdad', 'Titular', 'CantidadDeBeneficiarios'
            ]
            df = pd.DataFrame(beneficiarios, columns=columnas)
            df['FechaInscripcionBeneficiario'] = pd.to_datetime(df['FechaInscripcionBeneficiario'])
            return df
        except Exception as e:
            self.mostrar_mensaje(f"Error al convertir datos: {e}")
            return pd.DataFrame() 

    def mostrar_mensaje(self, mensaje):
        ventana = tk.Toplevel(self.root)
        ventana.title("Resultado")
        tk.Label(ventana, text=mensaje, bg='#f2f2f2', font=('Arial', 12)).pack(pady=20)

    def mostrar_grafico(self, fig):
        for widget in self.canvas_graficos.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def total_beneficiarios(self):
        try:
            # Agrupar los datos por año y contar la cantidad de beneficiarios
            self.data['Año'] = self.data['FechaInscripcionBeneficiario'].dt.year
            total_por_año = self.data.groupby('Año')['CantidadDeBeneficiarios'].sum().reset_index()

            # Calcular el total de beneficiarios
            total_beneficiarios = total_por_año['CantidadDeBeneficiarios'].sum()

            # Crear el gráfico circular
            fig, ax = plt.subplots(figsize=(10, 10))

            # Función para formatear las etiquetas con el número y el porcentaje
            def label_format(pct, all_values):
                total = sum(all_values)
                absolute = int(pct / 100. * total)
                return f'{absolute} ({pct:.1f}%)'

            # Crear el gráfico circular
            wedges, texts, autotexts = ax.pie(total_por_año['CantidadDeBeneficiarios'], 
                                            labels=total_por_año['Año'], 
                                            autopct=lambda pct: label_format(pct, total_por_año['CantidadDeBeneficiarios']),
                                            startangle=90,
                                            colors=sns.color_palette("Blues_d", len(total_por_año)))

            ax.set_title("Distribución de Beneficiarios por Año", fontsize=14)
            ax.axis('equal')  # Para que el gráfico sea un círculo

            # Formato para el texto dentro del gráfico
            for text in autotexts:
                text.set_color('white')
                text.set_fontsize(10)

            # Añadir el total de beneficiarios como texto en el gráfico
            ax.text(0, 0, f'Total: {total_beneficiarios}', ha='center', va='center', fontsize=16, weight='bold')

            # Mostrar el gráfico
            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error en consulta de beneficiarios: {e}")

    def clustering_beneficiarios(self):
        try:
            # Seleccionamos las columnas para el análisis
            df_clustering = self.data[['NivelEscolaridad', 'TipoAsignacionBeneficio', 'CantidadDeBeneficiarios']]

            # Convertir las variables categóricas a variables numéricas
            df_clustering['NivelEscolaridad'] = pd.Categorical(df_clustering['NivelEscolaridad']).codes
            df_clustering['TipoAsignacionBeneficio'] = pd.Categorical(df_clustering['TipoAsignacionBeneficio']).codes

            # Usar KMeans para hacer el clustering
            kmeans = KMeans(n_clusters=3, random_state=42)
            df_clustering['Cluster'] = kmeans.fit_predict(df_clustering[['NivelEscolaridad', 'TipoAsignacionBeneficio', 'CantidadDeBeneficiarios']])

            # Crear el gráfico de clusters
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.scatterplot(data=df_clustering, x='NivelEscolaridad', y='CantidadDeBeneficiarios', hue='Cluster', palette='deep', ax=ax)

            ax.set_title("Clustering de Beneficiarios", fontsize=14)
            ax.set_xlabel("Nivel de Escolaridad", fontsize=12)
            ax.set_ylabel("Cantidad de Beneficiarios", fontsize=12)

            # Mostrar el gráfico
            self.mostrar_grafico(fig)

        except Exception as e:
            self.mostrar_mensaje(f"Error al realizar clustering: {e}")

    def distribucion_por_departamento(self):
        try:
            distribucion = self.data.groupby('NombreDepartamentoAtencion')['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))  # Aumentar el tamaño de la figura
            sns.barplot(data=distribucion, x='NombreDepartamentoAtencion', y='CantidadDeBeneficiarios', ax=ax, palette='Blues_d')
            ax.set_title("Distribución de beneficiarios por departamento", fontsize=14)
            ax.set_xlabel("Departamento", fontsize=12)
            ax.set_ylabel("Cantidad de Beneficiarios", fontsize=12)

            # Ajustar las etiquetas del eje X
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.tight_layout()  # Ajustar el diseño

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de distribución por departamento: {e}")

    def tipos_incentivos_recibidos(self):
        try:
            incentivos = self.data.groupby(['TipoBeneficio', 'TipoAsignacionBeneficio'])['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))  # Aumentar el tamaño de la figura
            sns.barplot(data=incentivos, x='TipoBeneficio', y='CantidadDeBeneficiarios', hue='TipoAsignacionBeneficio', ax=ax, palette='Set2')
            ax.set_title("Tipos de incentivos recibidos", fontsize=14)
            ax.set_xlabel("Tipo de Beneficio", fontsize=12)
            ax.set_ylabel("Cantidad de Beneficiarios", fontsize=12)

            # Ajustar las etiquetas del eje X
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.tight_layout()  # Ajustar el diseño

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de tipos de incentivos: {e}")

    def variacion_beneficiarios_tiempo(self):
        try:
            variacion = self.data.resample('Q', on='FechaInscripcionBeneficiario')['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))  # Aumentar el tamaño de la figura
            sns.lineplot(data=variacion, x='FechaInscripcionBeneficiario', y='CantidadDeBeneficiarios', ax=ax, marker='o', color='coral')
            ax.set_title("Variación de beneficiarios en el tiempo", fontsize=14)
            ax.set_xlabel("Fecha", fontsize=12)
            ax.set_ylabel("Cantidad de Beneficiarios", fontsize=12)
            plt.tight_layout()  # Ajustar el diseño

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de variación en el tiempo: {e}")

    def relacion_incentivo_educacion(self):
        try:
            relacion = self.data.groupby(['TipoBeneficio', 'NivelEscolaridad'])['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))  # Aumentar el tamaño de la figura
            sns.barplot(data=relacion, x='TipoBeneficio', y='CantidadDeBeneficiarios', hue='NivelEscolaridad', ax=ax, palette='Pastel1')
            ax.set_title("Relación entre tipo de incentivo y nivel educativo", fontsize=14)
            ax.set_xlabel("Tipo de Beneficio", fontsize=12)
            ax.set_ylabel("Cantidad de Beneficiarios", fontsize=12)

            # Ajustar las etiquetas del eje X
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.tight_layout()  # Ajustar el diseño

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de relación incentivo y educación: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
