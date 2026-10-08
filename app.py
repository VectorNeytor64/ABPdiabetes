import os
import random
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

def parse_float(val):
    if val is None or val == '' or val == '-1':
        return None
    try:
        f = float(val)
        return f if f >= 0 else None
    except (ValueError, TypeError):
        return None

def enviar_correo_resultado(correo_destino, nombre_paciente, resultado):
    """
    Envía un correo electrónico formal con el CERTIFICADO CLÍNICO
    y la FICHA TÉCNICA del paciente para el Proyecto de Aula (ABP) - Universidad del Sinú.
    """
    if not correo_destino or '@' not in correo_destino:
        return False, "Correo electrónico no proporcionado o inválido."

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    remitente = os.getenv('SMTP_FROM', smtp_user or 'noreply@diagnosticodiabetes.com')

    # Datos para el Certificado Diagnóstico
    folio = f"CERT-CLINICO-{datetime.datetime.now().strftime('%Y')}-{random.randint(10000, 99999)}"
    fecha_emision = datetime.datetime.now().strftime("%d/%m/%Y %H:%M hs")
    color = resultado.get('color', '#3b82f6')

    # Formateo de recomendaciones y factores de riesgo
    recs_html = "".join([f"<li>{r}</li>" for r in resultado.get('recomendaciones', [])])
    factores_html = "".join([f"<li>{f}</li>" for f in resultado.get('factores_riesgo', [])])
    factores_section = f"<tr><td colspan='2' style='padding-top:15px;'><strong style='color:#334155;'>Hallazgos / Factores Detectados:</strong><ul style='margin-top:6px;'>{factores_html}</ul></td></tr>" if factores_html else ""

    # Valores Biométricos
    edad_str = f"{int(resultado['edad'])} años" if resultado.get('edad') else "No registrada"
    peso_str = f"{resultado['peso']} kg" if resultado.get('peso') else "No registrado"
    estatura_str = f"{resultado['estatura']} cm" if resultado.get('estatura') else "No registrada"
    imc_str = f"{resultado['imc']} kg/m² ({resultado['imc_categoria']})" if resultado.get('imc') else "No calculado"
    antecedente_fam = "Sí (Padres o Hermanos)" if resultado.get('antecedente_familiar') == 'si' else "No / Desconocido"
    sintomas_str = "Sí (Poliuria, polidipsia o pérdida de peso)" if resultado.get('tiene_sintomas') else "No reporta síntomas severos"

    # Pruebas de Laboratorio
    gpa_str = f"{resultado['gpa']} mg/dL (Límite ≥ 126)" if resultado.get('gpa') is not None else "No evaluada"
    hba1c_str = f"{resultado['hba1c']}% (Límite ≥ 6.5)" if resultado.get('hba1c') is not None else "No evaluada"
    ptog_str = f"{resultado['ptog']} mg/dL (Límite ≥ 200)" if resultado.get('ptog') is not None else "No evaluada"
    casual_str = f"{resultado['casual']} mg/dL (Límite ≥ 200)" if resultado.get('casual') is not None else "No evaluada"

    # Sección HTML de Enfermedades Preexistentes Declaradas (para el certificado)
    enfermedades_previas_lista = resultado.get('enfermedades_previas', [])
    if enfermedades_previas_lista:
        enf_items_html = "".join([
            f"<li style='margin-bottom:5px; padding: 4px 0; border-bottom: 1px solid #f1f5f9;'>"
            f"<span style='color:#dc2626; font-weight:600; margin-right:6px;'>●</span>{e}</li>"
            for e in enfermedades_previas_lista
        ])
        enf_section_html = f"""
        <div class='section-title' style='font-size:13px;font-weight:700;color:#334155;text-transform:uppercase;
            letter-spacing:0.8px;margin-top:25px;margin-bottom:12px;border-bottom:2px solid #e2e8f0;padding-bottom:5px;'>
            🏥 Historial Clínico Previo — Enfermedades Preexistentes Declaradas
        </div>
        <div style='background:#fff5f5; border: 2px solid #fecaca; border-radius:12px; padding:16px 18px; margin-bottom:18px;'>
            <p style='font-size:12px;color:#64748b;margin:0 0 10px 0;'>
                El paciente declaró padecer las siguientes enfermedades o condiciones médicas previas:
            </p>
            <ul style='margin:0; padding-left:20px; font-size:13px; color:#1e293b; line-height:1.6;'>
                {enf_items_html}
            </ul>
            <p style='font-size:11px;color:#94a3b8;margin:10px 0 0 0;font-style:italic;'>
                * Información declarada por el paciente. Debe ser verificada y confirmada por el médico tratante.
            </p>
        </div>
        """
    else:
        enf_section_html = """
        <div class='section-title' style='font-size:13px;font-weight:700;color:#334155;text-transform:uppercase;
            letter-spacing:0.8px;margin-top:25px;margin-bottom:12px;border-bottom:2px solid #e2e8f0;padding-bottom:5px;'>
            🏥 Historial Clínico Previo — Enfermedades Preexistentes Declaradas
        </div>
        <div style='background:#f8fafc; border: 1px dashed #cbd5e1; border-radius:10px; padding:12px 18px; margin-bottom:18px;'>
            <p style='font-size:13px;color:#94a3b8;margin:0;'>
                No se declararon enfermedades preexistentes en esta evaluación.
            </p>
        </div>
        """


    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Certificado de Evaluación Clínica</title>
        <style>
            body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 25px; color: #1e293b; }}
            .cert-card {{ background: #ffffff; max-width: 680px; margin: 0 auto; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
            .cert-header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 28px 30px; color: #ffffff; text-align: center; border-bottom: 5px solid {color}; }}
            .cert-header h1 {{ margin: 0; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; color: #f8fafc; }}
            .cert-header p {{ margin: 6px 0 0 0; font-size: 13px; color: #94a3b8; }}
            .cert-body {{ padding: 30px; }}
            .folio-bar {{ background: #f8fafc; border: 1px dashed #cbd5e1; padding: 10px 18px; border-radius: 10px; font-size: 12px; font-weight: bold; color: #475569; display: flex; justify-content: space-between; margin-bottom: 25px; }}
            
            .section-title {{ font-size: 13px; font-weight: 700; color: #334155; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 25px; margin-bottom: 12px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }}
            
            .diag-box {{ background: {color}15; border: 2px solid {color}; border-radius: 14px; padding: 22px; text-align: center; margin-bottom: 22px; }}
            .diag-title {{ font-size: 22px; font-weight: 800; color: {color}; margin: 0 0 6px 0; }}
            .diag-sub {{ font-size: 13px; font-weight: 600; color: #475569; margin: 0; }}
            
            .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; }}
            .info-table td {{ padding: 9px 12px; border-bottom: 1px solid #f1f5f9; }}
            .info-table td.label {{ font-weight: 600; color: #64748b; width: 38%; background: #f8fafc; border-radius: 4px; }}
            .info-table td.value {{ color: #0f172a; font-weight: 500; }}
            
            .motivo-box {{ background: #f8fafc; border-left: 4px solid {color}; padding: 14px 18px; border-radius: 6px; font-size: 13px; line-height: 1.5; color: #334155; margin-bottom: 20px; }}
            
            ul {{ margin: 0; padding-left: 20px; font-size: 13px; color: #334155; line-height: 1.6; }}
            li {{ margin-bottom: 6px; }}
            
            .cert-footer {{ background: #f8fafc; padding: 22px 30px; text-align: center; font-size: 11px; color: #64748b; border-top: 1px solid #e2e8f0; }}
            .stamp {{ font-weight: 700; color: #166534; background: #dcfce7; border: 1px solid #86efac; display: inline-block; padding: 6px 18px; border-radius: 20px; margin-bottom: 12px; }}
        </style>
    </head>
    <body>
        <div class="cert-card">
            <!-- Encabezado del Certificado -->
            <div class="cert-header">
                <h1>📜 Certificado de Evaluación Clínica</h1>
                <p>Proyecto de Aula (ABP) &bull; Universidad del Sinú Elías Bechara Zainúm</p>
            </div>

            <div class="cert-body">
                <!-- Barra de Folio y Fecha -->
                <div class="folio-bar">
                    <span><strong>FOLIO:</strong> {folio}</span>
                    <span><strong>FECHA EMISIÓN:</strong> {fecha_emision}</span>
                </div>

                <!-- Dictamen y Dictamen Diagnóstico -->
                <div class="diag-box">
                    <div class="diag-title">{resultado.get('diagnostico')}</div>
                    <div class="diag-sub">Nivel de Riesgo Clínico: {resultado.get('nivel_riesgo')}</div>
                </div>

                <div class="motivo-box">
                    <strong>Criterio Clínico Aplicado:</strong><br>
                    {resultado.get('motivo')}
                </div>

                <!-- SECCIÓN 1: FICHA TÉCNICA DEL PACIENTE -->
                <div class="section-title">👤 Ficha Técnica e Información del Paciente</div>
                <table class="info-table">
                    <tr>
                        <td class="label">Nombre Completo:</td>
                        <td class="value"><strong>{nombre_paciente}</strong></td>
                    </tr>
                    <tr>
                        <td class="label">Teléfono de Contacto:</td>
                        <td class="value">{resultado.get('telefono') or 'No registrado'}</td>
                    </tr>
                    <tr>
                        <td class="label">Correo Electrónico:</td>
                        <td class="value">{correo_destino}</td>
                    </tr>
                    <tr>
                        <td class="label">Dirección de Hogar:</td>
                        <td class="value">{resultado.get('direccion') or 'No registrada'}</td>
                    </tr>
                    <tr>
                        <td class="label">Antecedentes Médicos:</td>
                        <td class="value">{resultado.get('antecedentes_medicos') or 'Sin registro previo'}</td>
                    </tr>
                    <tr>
                        <td class="label">Edad / Peso / Estatura:</td>
                        <td class="value">{edad_str} | {peso_str} | {estatura_str}</td>
                    </tr>
                    <tr>
                        <td class="label">Índice de Masa Corporal (IMC):</td>
                        <td class="value">{imc_str}</td>
                    </tr>
                    <tr>
                        <td class="label">Antecedentes Familiares:</td>
                        <td class="value">{antecedente_fam}</td>
                    </tr>
                </table>

                <!-- SECCIÓN 1B: ENFERMEDADES PREEXISTENTES DECLARADAS -->
                {enf_section_html}

                <!-- SECCIÓN 2: REGISTRO DE LABORATORIO EVALUADO -->
                <div class="section-title">🧪 Registro de Laboratorio e Indicadores Clínicos</div>
                <table class="info-table">
                    <tr>
                        <td class="label">1. Glucemia en Ayunas (GPa):</td>
                        <td class="value"><strong>{gpa_str}</strong></td>
                    </tr>
                    <tr>
                        <td class="label">2. HbA1c (% Glicosilada):</td>
                        <td class="value"><strong>{hba1c_str}</strong></td>
                    </tr>
                    <tr>
                        <td class="label">3. PTOG 2 Horas:</td>
                        <td class="value"><strong>{ptog_str}</strong></td>
                    </tr>
                    <tr>
                        <td class="label">4. Glucemia Casual / Azar:</td>
                        <td class="value"><strong>{casual_str}</strong></td>
                    </tr>
                    <tr>
                        <td class="label">Síntomas Hiperglucémicos:</td>
                        <td class="value">{sintomas_str}</td>
                    </tr>
                    {factores_section}
                </table>

                <!-- SECCIÓN 3: PLAN DE RECOMENDACIONES -->
                <div class="section-title">📋 Plan y Recomendaciones Médicas Sugeridas</div>
                <ul>
                    {recs_html}
                </ul>
            </div>

            <!-- Pie del Certificado -->
            <div class="cert-footer">
                <div class="stamp">✓ EVALUACIÓN REGISTRADA - PROYECTO ABP 2026</div>
                <p><strong>AVISO ACADÉMICO / MÉDICO:</strong> Este certificado ha sido generado con fines formativos y de orientación preventiva por estudiantes pertenecientes a la <em>Universidad del Sinú Elías Bechara Zainúm</em>. En pacientes asintomáticos con 1 sola prueba alterada en el límite, se requiere confirmación médica formal mediante un segundo estudio de laboratorio en un día diferente.</p>
            </div>
        </div>
    </body>
    </html>
    """

    if not smtp_user or not smtp_password:
        print(f"[DEMO EMAIL] Certificado y Ficha Técnica completos generados para {correo_destino}. (Configure SMTP_USER y SMTP_PASSWORD en su servidor para envío real).")
        return True, f"Certificado y Ficha Técnica procesados para {correo_destino}"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Certificado de Evaluación Clínica - {nombre_paciente} [{folio}]"
        msg['From'] = remitente
        msg['To'] = correo_destino

        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(remitente, [correo_destino], msg.as_string())

        return True, f"Certificado y Ficha Técnica enviados con éxito a {correo_destino}"
    except Exception as e:
        print(f"[ERROR EMAIL] No se pudo enviar el certificado a {correo_destino}: {e}")
        return False, f"No se pudo enviar el certificado a {correo_destino}: {str(e)}"

def calcular_riesgo_diabetes(datos):
    """
    Evaluación diagnóstica basada en parámetros clínicos de laboratorio y cuadro sintomático:
    - Datos del paciente (Nombre, Teléfono, Correo, Dirección, Antecedentes Médicos)
    - Síntomas de hiperglucemia severa (Poliuria, polidipsia, pérdida de peso)
    - HbA1c (%) -> Límite HbA1c > 3.0% (Validación) / ≥ 6.5% (Diabetes)
    - Glucemia Plasmática en Ayunas (GPa - mg/dL) -> Límite ≥ 126 mg/dL (Diabetes)
    - Prueba de Tolerancia Oral a la Glucosa 2h (PTOG - mg/dL) -> Límite ≥ 200 mg/dL (Diabetes)
    - Glucemia al Azar / Casual (mg/dL) -> Límite ≥ 200 mg/dL (Diabetes)
    """
    nombre = datos.get('nombre', 'Paciente').strip() or 'Paciente'
    telefono = datos.get('telefono', '').strip()
    correo = datos.get('correo', '').strip()
    direccion = datos.get('direccion', '').strip()
    antecedentes_medicos = datos.get('antecedentes_medicos', '').strip()
    tiene_sintomas = str(datos.get('tiene_sintomas', '')).lower() in ['true', 'si', 's', '1', 'on']

    # Enfermedades preexistentes declaradas (puede venir como lista JSON o string separado por comas)
    enfermedades_raw = datos.get('enfermedades_previas', [])
    if isinstance(enfermedades_raw, list):
        enfermedades_previas = [e.strip() for e in enfermedades_raw if e.strip()]
    elif isinstance(enfermedades_raw, str) and enfermedades_raw.strip():
        enfermedades_previas = [e.strip() for e in enfermedades_raw.split(',') if e.strip()]
    else:
        enfermedades_previas = []

    # Captura de pruebas de laboratorio
    gpa = parse_float(datos.get('gpa') or datos.get('glucosa'))
    hba1c = parse_float(datos.get('hba1c'))
    ptog = parse_float(datos.get('ptog'))
    casual = parse_float(datos.get('casual'))

    # Al menos una prueba debe ser proporcionada
    if gpa is None and hba1c is None and ptog is None and casual is None:
        return {'error': 'Debes ingresar al menos el valor de una prueba de laboratorio (Glucosa en ayunas, HbA1c, PTOG o Glucosa casual).'}

    # Validación de límites fisiológicos (HbA1c > 3.0%)
    for valor, nombre_p in [(gpa, 'Glucosa en Ayunas'), (casual, 'Glucosa Casual'), (ptog, 'PTOG')]:
        if valor is not None and valor > 700:
            return {'error': f'El valor de {nombre_p} ({valor} mg/dL) está fuera de límites plausibles.'}
    if hba1c is not None and (hba1c < 3.0 or hba1c > 20.0):
        return {'error': f'El valor de HbA1c ({hba1c}%) está fuera de límites plausibles (debe ser mayor a 3.0% y hasta 20.0%).'}

    # Evaluación de criterios positivos para Diabetes
    pos_hba1c = hba1c is not None and hba1c >= 6.5
    pos_gpa = gpa is not None and gpa >= 126.0
    pos_ptog = ptog is not None and ptog >= 200.0
    pos_casual = casual is not None and casual >= 200.0

    # Evaluación de Prediabetes
    pre_hba1c = hba1c is not None and (5.7 <= hba1c <= 6.4)
    pre_gpa = gpa is not None and (100.0 <= gpa <= 125.0)
    pre_ptog = ptog is not None and (140.0 <= ptog <= 199.0)

    # Conteo de pruebas de laboratorio positivas
    pruebas_positivas = sum([pos_hba1c, pos_gpa, pos_ptog])

    # Lógica Diagnóstica (Implementando la regla clínica institucional)
    if tiene_sintomas and pos_casual:
        diagnostico = "DIABETES MELLITUS CONFIRMADA"
        categoria_codigo = "diabetes"
        nivel_riesgo = "Confirmado / Atención Médica Urgente"
        color = "#ef4444"
        motivo = "Paciente con síntomas claros de hiperglucemia severa y glucemia al azar ≥ 200 mg/dL."
        recomendaciones = [
            "Es imperativo consultar de inmediato a un médico especialista (Endocrinólogo).",
            "Iniciar protocolo de manejo metabólico y evaluación de laboratorios integrales.",
            "Mantener hidratación constante y acudir a un centro de atención clínica urgente."
        ]
        porcentaje_medidor = 95

    elif tiene_sintomas and (pos_hba1c or pos_gpa or pos_ptog):
        diagnostico = "DIABETES MELLITUS CONFIRMADA"
        categoria_codigo = "diabetes"
        nivel_riesgo = "Confirmado / Requiere Tratamiento"
        color = "#ef4444"
        motivo = "Paciente sintomático con al menos una prueba de laboratorio en rango diagnóstico de diabetes (GPa ≥ 126 mg/dL, HbA1c ≥ 6.5% o PTOG ≥ 200 mg/dL)."
        recomendaciones = [
            "Acudir de inmediato a consulta médica para valoración formal e inicio de plan terapéutico.",
            "Realizar monitoreo continuo de glucemia y evaluación renal/cardiovascular.",
            "Recibir orientación de educación en diabetes y plan nutricional personalizado."
        ]
        porcentaje_medidor = 90

    elif not tiene_sintomas and pruebas_positivas >= 2:
        diagnostico = "DIABETES MELLITUS CONFIRMADA"
        categoria_codigo = "diabetes"
        nivel_riesgo = "Confirmado (Criterio Multilaboratorio)"
        color = "#ef4444"
        motivo = "Paciente asintomático pero con 2 o más pruebas distintas alteradas en la misma evaluación (criterio confirmatorio concordante)."
        recomendaciones = [
            "Confirmación concordante entre pruebas distintas. Requiere consulta médica a la brevedad.",
            "Evaluación de hábitos de estilo de vida, perfil lipídico y función metabólica.",
            "Seguimiento especializado continuo."
        ]
        porcentaje_medidor = 85

    elif not tiene_sintomas and (pruebas_positivas == 1 or pos_casual):
        diagnostico = "RESULTADO POSITIVO PRELIMINAR"
        categoria_codigo = "preliminar"
        nivel_riesgo = "Elevado / Requiere Confirmación"
        color = "#f97316"
        motivo = "Al no presentar síntomas claros de hiperglucemia severa y tener solo 1 prueba alterada en el límite crítico (GPa ≥ 126 mg/dL, HbA1c ≥ 6.5% o PTOG/Casual ≥ 200 mg/dL), las pautas clínicas exigen repetir la prueba para confirmar."
        recomendaciones = [
            "No entrar en pánico: Al ser asintomático con una única prueba alterada, se debe REPETIR la prueba alterada en un día diferente para confirmar.",
            "Agendar consulta médica para programar la prueba de confirmación de laboratorio.",
            "Adopta medidas preventivas inmediatas en tu dieta reduciendo carbohidratos simples y azúcares."
        ]
        porcentaje_medidor = 78

    elif pre_hba1c or pre_gpa or pre_ptog:
        diagnostico = "PREDIABETES (Riesgo Elevado)"
        categoria_codigo = "prediabetes"
        nivel_riesgo = "Moderado / Intermedio"
        color = "#f59e0b"
        motivo = "Presenta valores en rango de alteración intermedia (HbA1c 5.7-6.4%, Glucosa ayunas 100-125 mg/dL o PTOG 140-199 mg/dL)."
        recomendaciones = [
            "La prediabetes se puede revertir con cambios en el estilo de vida.",
            "Reducir consumo de harinas refinadas, bebidas azucaradas y ultraprocesados.",
            "Realizar al menos 150 minutos a la semana de ejercicio aeróbico y de fuerza.",
            "Repetir controles de glucemia anualmente."
        ]
        porcentaje_medidor = 60

    else:
        diagnostico = "VALORES NORMALES"
        categoria_codigo = "normal"
        nivel_riesgo = "Bajo"
        color = "#10b981"
        motivo = "Ninguna de las pruebas ingresadas supera los umbrales clínicos de prediabetes ni diabetes."
        recomendaciones = [
            "Mantén un estilo de vida activo y alimentación balanceada.",
            "Realiza chequeos médicos preventivos de rutina una vez al año."
        ]
        porcentaje_medidor = 35

    # Determinación de Nivel Crítico / Alerta (Activado para Diabetes y Prediabetes)
    es_critico = categoria_codigo in ['diabetes', 'preliminar', 'prediabetes']

    # Evaluación de IMC y otros factores
    peso = parse_float(datos.get('peso'))
    estatura = parse_float(datos.get('estatura'))
    imc = None
    imc_categoria = None
    if peso and estatura:
        estatura_m = estatura / 100.0 if estatura > 3.0 else estatura
        if 0.5 <= estatura_m <= 2.5 and 20 <= peso <= 300:
            imc = round(peso / (estatura_m ** 2), 1)
            if imc < 18.5: imc_categoria = "Bajo peso"
            elif 18.5 <= imc < 25.0: imc_categoria = "Peso normal"
            elif 25.0 <= imc < 30.0: imc_categoria = "Sobrepeso"
            else: imc_categoria = "Obesidad"

    factores_riesgo = []
    if tiene_sintomas:
        factores_riesgo.append("Presencia de síntomas clásicos (Poliuria, polidipsia, pérdida de peso)")
    if pos_hba1c: factores_riesgo.append(f"HbA1c en rango diabetes: {hba1c}% (≥ 6.5%)")
    elif pre_hba1c: factores_riesgo.append(f"HbA1c en prediabetes: {hba1c}% (5.7% - 6.4%)")
    if pos_gpa: factores_riesgo.append(f"Glucosa ayunas (GPa) en rango límite crítico: {gpa} mg/dL (≥ 126 mg/dL)")
    elif pre_gpa: factores_riesgo.append(f"Glucosa ayunas (GPa) en prediabetes: {gpa} mg/dL (100 - 125 mg/dL)")
    if pos_ptog: factores_riesgo.append(f"PTOG 2h en rango límite crítico: {ptog} mg/dL (≥ 200 mg/dL)")
    elif pre_ptog: factores_riesgo.append(f"PTOG 2h en prediabetes: {ptog} mg/dL (140 - 199 mg/dL)")
    if pos_casual: factores_riesgo.append(f"Glucosa casual en rango límite crítico: {casual} mg/dL (≥ 200 mg/dL)")
    # Agregar enfermedades preexistentes declaradas como factores adicionales
    for enfermedad in enfermedades_previas:
        factores_riesgo.append(f"Antecedente declarado: {enfermedad}")

    if imc:
        factores_riesgo.append(f"IMC: {imc} kg/m² ({imc_categoria})")
    if datos.get('antecedente') == 'si':
        factores_riesgo.append("Antecedentes familiares directos de diabetes")
    if datos.get('actividad') == 'sedentario':
        factores_riesgo.append("Estilo de vida sedentario")

    val_mostrar = gpa or casual or ptog or (hba1c if hba1c else "--")

    return {
        'nombre': nombre,
        'telefono': telefono,
        'correo': correo,
        'direccion': direccion,
        'antecedentes_medicos': antecedentes_medicos,
        'enfermedades_previas': enfermedades_previas,
        'glucosa': val_mostrar,
        'diagnostico': diagnostico,
        'categoria_codigo': categoria_codigo,
        'nivel_riesgo': nivel_riesgo,
        'color': color,
        'motivo': motivo,
        'recomendaciones': recomendaciones,
        'porcentaje_medidor': porcentaje_medidor,
        'tiene_sintomas': tiene_sintomas,
        'hba1c': hba1c,
        'gpa': gpa,
        'ptog': ptog,
        'casual': casual,
        'edad': parse_float(datos.get('edad')),
        'peso': peso,
        'estatura': estatura,
        'antecedente_familiar': datos.get('antecedente', 'no'),
        'imc': imc,
        'imc_categoria': imc_categoria,
        'factores_riesgo': factores_riesgo,
        'es_critico': es_critico
    }

@app.route('/')
@app.route('/presentacion')
@app.route('/index2.html')
def presentacion():
    return render_template('index2.html')

@app.route('/app')
@app.route('/evaluador')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/imagenes/<path:filename>')
def serve_imagenes(filename):
    return send_from_directory('imagenes', filename)

@app.route('/api/evaluar', methods=['POST'])
def evaluar():
    datos = request.get_json() or request.form.to_dict()
    resultado = calcular_riesgo_diabetes(datos)
    if 'error' in resultado:
        return jsonify(resultado), 400

    correo_destino = datos.get('correo', '').strip()
    if correo_destino:
        exito, msg_correo = enviar_correo_resultado(correo_destino, resultado['nombre'], resultado)
        resultado['correo_enviado'] = exito
        resultado['correo_mensaje'] = msg_correo
    else:
        resultado['correo_enviado'] = False
        resultado['correo_mensaje'] = 'No se proporcionó correo electrónico.'

    return jsonify(resultado)

if __name__ == '__main__':
    print("Iniciando servidor de Evaluación de Diabetes Mellitus - Universidad del Sinú...")
    app.run(debug=True, port=5000)
