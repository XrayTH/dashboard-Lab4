import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from controlador import obtener_todos_beneficiarios

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de Beneficiarios")
        self.root.geometry("1000x700")

        # Cargar datos con control de errores
        try:
            self.data = self.cargar_datos()
        except Exception as e:
            self.mostrar_mensaje(f"Error al cargar datos: {e}")
            self.data = pd.DataFrame()  # Cargar un DataFrame vacío si hay error

        # Crear la interfaz gráfica
        self.crear_widgets()

    def cargar_datos(self):
        try:
            # Obtener datos desde la función de controlador
            beneficiarios = obtener_todos_beneficiarios()

            # Asignar nombres de columnas explícitamente
            columnas = [
                'id', 'CodigoDepartamentoAtencion', 'EstadoBeneficiario',
                'FechaInscripcionBeneficiario', 'Genero', 'NivelEscolaridad',
                'NombreDepartamentoAtencion', 'TipoAsignacionBeneficio', 
                'TipoBeneficio', 'RangoBeneficioConsolidadoAsignado', 
                'RangoEdad', 'Titular', 'CantidadDeBeneficiarios'
            ]
            
            # Convertir la lista de beneficiarios en un DataFrame con nombres de columnas
            df = pd.DataFrame(beneficiarios, columns=columnas)

            # Convertir la columna de fecha al tipo datetime
            df['FechaInscripcionBeneficiario'] = pd.to_datetime(df['FechaInscripcionBeneficiario'])

            return df
        except Exception as e:
            self.mostrar_mensaje(f"Error al convertir datos: {e}")
            return pd.DataFrame()  # Retorna DataFrame vacío si ocurre un error


    def crear_widgets(self):
        # Crear botones para las diferentes consultas
        ttk.Button(self.root, text="Número total de beneficiarios", command=self.total_beneficiarios).pack(pady=10)
        ttk.Button(self.root, text="Distribución por departamento", command=self.distribucion_por_departamento).pack(pady=10)
        ttk.Button(self.root, text="Tipos de incentivos recibidos", command=self.tipos_incentivos_recibidos).pack(pady=10)
        ttk.Button(self.root, text="Variación de beneficiarios en el tiempo", command=self.variacion_beneficiarios_tiempo).pack(pady=10)
        ttk.Button(self.root, text="Relación entre tipo de incentivo y nivel educativo", command=self.relacion_incentivo_educacion).pack(pady=10)

    def total_beneficiarios(self):
        try:
            # Consulta: Total de beneficiarios en un periodo específico
            periodo_inicio = datetime(2020, 1, 1)
            periodo_fin = datetime(2023, 12, 31)
            total = self.data[(self.data['FechaInscripcionBeneficiario'] >= periodo_inicio) & 
                              (self.data['FechaInscripcionBeneficiario'] <= periodo_fin)]['CantidadDeBeneficiarios'].sum()
            
            # Crear una ventana para mostrar el resultado
            self.mostrar_mensaje(f"Total de beneficiarios entre {periodo_inicio.date()} y {periodo_fin.date()}: {total}")
        except Exception as e:
            self.mostrar_mensaje(f"Error en consulta de beneficiarios: {e}")

    def distribucion_por_departamento(self):
        try:
            # Consulta: Distribución por departamento
            distribucion = self.data.groupby('NombreDepartamentoAtencion')['CantidadDeBeneficiarios'].sum()
            
            fig, ax = plt.subplots()
            distribucion.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_title("Distribución de beneficiarios por departamento")
            ax.set_xlabel("Departamento")
            ax.set_ylabel("Cantidad de Beneficiarios")

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de distribución por departamento: {e}")

    def tipos_incentivos_recibidos(self):
        try:
            # Consulta: Tipos de incentivos recibidos
            incentivos = self.data.groupby(['TipoBeneficio', 'TipoAsignacionBeneficio'])['CantidadDeBeneficiarios'].sum().unstack()

            fig, ax = plt.subplots()
            incentivos.plot(kind='bar', stacked=True, ax=ax)
            ax.set_title("Tipos de incentivos recibidos")
            ax.set_xlabel("Tipo de Beneficio")
            ax.set_ylabel("Cantidad de Beneficiarios")

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de tipos de incentivos: {e}")

    def variacion_beneficiarios_tiempo(self):
        try:
            # Consulta: Variación de beneficiarios en el tiempo
            variacion = self.data.resample('Q', on='FechaInscripcionBeneficiario')['CantidadDeBeneficiarios'].sum()
            
            fig, ax = plt.subplots()
            variacion.plot(kind='line', ax=ax, marker='o', color='coral')
            ax.set_title("Variación de beneficiarios en el tiempo")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Cantidad de Beneficiarios")

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de variación en el tiempo: {e}")

    def relacion_incentivo_educacion(self):
        try:
            # Consulta: Relación entre tipo de incentivo y nivel educativo
            relacion = self.data.groupby(['TipoBeneficio', 'NivelEscolaridad'])['CantidadDeBeneficiarios'].sum().unstack()
            
            fig, ax = plt.subplots()
            relacion.plot(kind='bar', stacked=True, ax=ax)
            ax.set_title("Relación entre tipo de incentivo y nivel educativo")
            ax.set_xlabel("Tipo de Beneficio")
            ax.set_ylabel("Cantidad de Beneficiarios")

            self.mostrar_grafico(fig)
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar gráfico de relación incentivo y educación: {e}")

    def mostrar_mensaje(self, mensaje):
        # Ventana de mensaje
        ventana = tk.Toplevel(self.root)
        ventana.title("Resultado")
        tk.Label(ventana, text=mensaje).pack(pady=20)

    def mostrar_grafico(self, fig):
        # Integrar gráficos Matplotlib en Tkinter
        ventana = tk.Toplevel(self.root)
        ventana.title("Gráfico")
        
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
