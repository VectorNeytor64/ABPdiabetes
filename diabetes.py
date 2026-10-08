# Programa de evaluación de Diabetes Mellitus en Python
# Proyecto de Aula (ABP) - Universidad del Sinú Elías Bechara Zainúm

from app import calcular_riesgo_diabetes

def ejecutar_cli():
    print("==================================================")
    print("      EVALUACIÓN CLÍNICA DE DIABETES MELLITUS     ")
    print("    Proyecto de Aula ABP - Universidad del Sinú   ")
    print("==================================================\n")

    nombre = input("Nombre del paciente [Paciente]: ").strip() or "Paciente"
    telefono = input("Número de teléfono: ").strip()
    correo = input("Correo electrónico: ").strip()
    direccion = input("Dirección de hogar: ").strip()
    antecedentes = input("Antecedentes médicos: ").strip()

    respuesta = input("\n¿El paciente presenta síntomas claros de hiperglucemia severa?\n"
                      "(Poliuria, polidipsia, pérdida de peso inexplicable) [S/N]: ").strip().upper()
    tiene_sintomas = (respuesta == "S")

    print("\n--- INGRESO DE PRUEBAS DE LABORATORIO ---")
    print("(Si no cuenta con el dato de alguna prueba, presione Enter o ingrese -1)\n")

    def leer_val(prompt):
        val = input(prompt).strip()
        if not val or val == "-1":
            return None
        try:
            return float(val)
        except ValueError:
            return None

    hba1c = leer_val("1. Hemoglobina Glicosilada - HbA1c (%) (Límite > 3.0% / ≥ 6.5%): ")
    gpa = leer_val("2. Glucemia Plasmática en Ayunas - GPa (mg/dL) (Límite ≥ 126): ")
    ptog = leer_val("3. Prueba de Tolerancia Oral a la Glucosa - PTOG (mg/dL) (Límite ≥ 200): ")
    casual = leer_val("4. Glucemia al Azar / Casual (mg/dL) (Límite ≥ 200): ")

    resultado = calcular_riesgo_diabetes({
        'nombre': nombre,
        'telefono': telefono,
        'correo': correo,
        'direccion': direccion,
        'antecedentes_medicos': antecedentes,
        'tiene_sintomas': tiene_sintomas,
        'hba1c': hba1c,
        'gpa': gpa,
        'ptog': ptog,
        'casual': casual
    })

    if 'error' in resultado:
        print(f"\n❌ Error: {resultado['error']}")
        return

    print("\n==================================================")
    print("              RESULTADO DEL DIAGNÓSTICO           ")
    print("==================================================")
    print(f"PACIENTE: {resultado['nombre']}")
    if resultado['telefono']: print(f"Teléfono: {resultado['telefono']}")
    if resultado['correo']: print(f"Correo: {resultado['correo']}")
    if resultado['direccion']: print(f"Dirección: {resultado['direccion']}")
    if resultado['antecedentes_medicos']: print(f"Antecedentes: {resultado['antecedentes_medicos']}")
    print("--------------------------------------------------")
    print(f"DIAGNÓSTICO: {resultado['diagnostico']}")
    print(f"Motivo: {resultado['motivo']}")
    print(f"Nivel de riesgo: {resultado['nivel_riesgo']}")
    print("--------------------------------------------------")
    print("Recomendaciones:")
    for rec in resultado['recomendaciones']:
        print(f" • {rec}")
    
    if resultado.get('es_critico'):
        if resultado.get('categoria_codigo') == 'prediabetes':
            print("\n⚠️ ¡ALERTA CLÍNICA - PREDIABETES!")
            print("El paciente presenta valores en rango de Prediabetes.")
            print("Se recomienda consulta médica para iniciar medidas preventivas.")
        else:
            print("\n🚨 ¡ALERTA DE ATENCIÓN CLÍNICA URGENTE!")
            print("El paciente ha alcanzado el límite diagnóstico crítico de Diabetes.")
            print("Se recomienda acudir INMEDIATAMENTE a un centro médico / de urgencias.")
    print("==================================================\n")

if __name__ == "__main__":
    ejecutar_cli()