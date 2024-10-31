from conexion import crear_conexion, cerrar_conexion

def obtener_todos_beneficiarios():
    """Obtiene todos los registros de la tabla beneficiarios"""
    conexion = crear_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT * FROM beneficiarios"
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    cursor.close()
    cerrar_conexion(conexion)
    return resultados

def obtener_beneficiarios_por_estado(estado):
    """Obtiene registros de beneficiarios filtrados por EstadoBeneficiario"""
    conexion = crear_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT * FROM beneficiarios WHERE EstadoBeneficiario = %s"
    cursor.execute(consulta, (estado,))
    resultados = cursor.fetchall()
    cursor.close()
    cerrar_conexion(conexion)
    return resultados
