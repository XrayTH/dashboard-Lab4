import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from controlador import obtener_todos_beneficiarios

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de Beneficiarios")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f2f2f2')

        # Crear un Frame para los botones
        self.button_frame = ttk.Frame(self.root, padding=10)
        self.button_frame.grid(row=0, column=0, sticky="ew")

        # Crear botones para las diferentes consultas
        ttk.Button(self.button_frame, text="Número total de beneficiarios", command=self.total_beneficiarios).grid(row=0, column=0, padx=5)
        ttk.Button(self.button_frame, text="Distribución por departamento", command=self.distribucion_por_departamento).grid(row=0, column=1, padx=5)
        ttk.Button(self.button_frame, text="Tipos de incentivos recibidos", command=self.tipos_incentivos_recibidos).grid(row=0, column=2, padx=5)
        ttk.Button(self.button_frame, text="Variación de beneficiarios en el tiempo", command=self.variacion_beneficiarios_tiempo).grid(row=0, column=3, padx=5)
        ttk.Button(self.button_frame, text="Relación entre tipo de incentivo y nivel educativo", command=self.relacion_incentivo_educacion).grid(row=0, column=4, padx=5)

        # Crear un Frame para los gráficos
        self.canvas_graficos = tk.Frame(self.root)
        self.canvas_graficos.grid(row=1, column=0, sticky="nsew")

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
            # Obtener datos desde la función de controlador
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
            periodo_inicio = datetime(2012, 1, 1)
            periodo_fin = datetime(2015, 12, 31)
            total = self.data[(self.data['FechaInscripcionBeneficiario'] >= periodo_inicio) & 
                              (self.data['FechaInscripcionBeneficiario'] <= periodo_fin)]['CantidadDeBeneficiarios'].sum()
            self.mostrar_mensaje(f"Total de beneficiarios entre {periodo_inicio.date()} y {periodo_fin.date()}: {total}")
        except Exception as e:
            self.mostrar_mensaje(f"Error en consulta de beneficiarios: {e}")

    def distribucion_por_departamento(self):
        try:
            distribucion = self.data.groupby('NombreDepartamentoAtencion')['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=distribucion, x='NombreDepartamentoAtencion', y='CantidadDeBeneficiarios', ax=ax, palette='Blues_d')
            ax.set_title("Distribución de beneficiarios por departamento")
            ax.set_xlabel("Departamento")
            ax.set_ylabel("Cantidad de Beneficiarios")
            plt.xticks(rotation=45)
            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de distribución por departamento: {e}")

    def tipos_incentivos_recibidos(self):
        try:
            incentivos = self.data.groupby(['TipoBeneficio', 'TipoAsignacionBeneficio'])['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=incentivos, x='TipoBeneficio', y='CantidadDeBeneficiarios', hue='TipoAsignacionBeneficio', ax=ax, palette='Set2')
            ax.set_title("Tipos de incentivos recibidos")
            ax.set_xlabel("Tipo de Beneficio")
            ax.set_ylabel("Cantidad de Beneficiarios")
            plt.xticks(rotation=45)
            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de tipos de incentivos: {e}")

    def variacion_beneficiarios_tiempo(self):
        try:
            variacion = self.data.resample('Q', on='FechaInscripcionBeneficiario')['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=variacion, x='FechaInscripcionBeneficiario', y='CantidadDeBeneficiarios', ax=ax, marker='o', color='coral')
            ax.set_title("Variación de beneficiarios en el tiempo")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Cantidad de Beneficiarios")
            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de variación en el tiempo: {e}")

    def relacion_incentivo_educacion(self):
        try:
            relacion = self.data.groupby(['TipoBeneficio', 'NivelEscolaridad'])['CantidadDeBeneficiarios'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=relacion, x='TipoBeneficio', y='CantidadDeBeneficiarios', hue='NivelEscolaridad', ax=ax, palette='Pastel1')
            ax.set_title("Relación entre tipo de incentivo y nivel educativo")
            ax.set_xlabel("Tipo de Beneficio")
            ax.set_ylabel("Cantidad de Beneficiarios")
            plt.xticks(rotation=45)
            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de relación incentivo y educación: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
