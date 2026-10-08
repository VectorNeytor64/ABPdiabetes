document.addEventListener('DOMContentLoaded', () => {
    // Referencias a Elementos DOM
    const gpaNumberInput = document.getElementById('gpa');
    const glucosaRangeInput = document.getElementById('glucosa-range');
    const hba1cInput = document.getElementById('hba1c');
    const ptogInput = document.getElementById('ptog');
    const casualInput = document.getElementById('casual');
    
    // Status Pills DOM
    const gpaStatusPill = document.getElementById('gpa-status-pill');
    const hba1cStatusPill = document.getElementById('hba1c-status-pill');
    const ptogStatusPill = document.getElementById('ptog-status-pill');
    const casualStatusPill = document.getElementById('casual-status-pill');

    const btnEvaluar = document.getElementById('btn-evaluar');
    const diabetesForm = document.getElementById('diabetes-form');

    const resultsPlaceholder = document.getElementById('results-placeholder');
    const resultsContent = document.getElementById('results-content');
    
    const gaugePointer = document.getElementById('gauge-pointer');
    const resGlucosaVal = document.getElementById('res-glucosa-val');
    const statusBanner = document.getElementById('status-banner');
    const resDiagnostico = document.getElementById('res-diagnostico');
    const resRiesgoBadge = document.getElementById('res-riesgo-badge');
    const resMotivo = document.getElementById('res-motivo');
    const resRecomendaciones = document.getElementById('res-recomendaciones');
    const riskFactorsContainer = document.getElementById('risk-factors-container');
    const riskFactorsList = document.getElementById('risk-factors-list');

    // Ficha Paciente DOM
    const resPacienteNombre = document.getElementById('res-paciente-nombre');
    const resPacienteTelefono = document.getElementById('res-paciente-telefono');
    const resPacienteCorreo = document.getElementById('res-paciente-correo');
    const resPacienteDireccion = document.getElementById('res-paciente-direccion');
    const resPacienteAntecedentes = document.getElementById('res-paciente-antecedentes');

    // Modal de Alerta Crítica DOM
    const modalAlertaCritica = document.getElementById('modal-alerta-critica');
    const modalPacienteNombre = document.getElementById('modal-paciente-nombre');
    const modalPacienteContacto = document.getElementById('modal-paciente-contacto');
    const btnCerrarAlerta = document.getElementById('btn-cerrar-alerta');

    // Audio Context para Sintetizador de Alarma Sonora de Emergencia
    let audioCtx = null;
    let alarmInterval = null;

    // Asegurar estado inicial desactivado/oculto al cargar la página
    detenerAlertaSonora();
    if (modalAlertaCritica) {
        modalAlertaCritica.classList.add('hidden');
    }

    // =========================================================================
    // ACTUALIZACIÓN DE BADGES / STATUS PILLS EN VIVO
    // =========================================================================
    function actualizarStatusGPa(val) {
        if (!gpaStatusPill) return;
        if (isNaN(val) || val === null || val === '') {
            gpaStatusPill.className = 'live-status-pill pill-neutral';
            gpaStatusPill.textContent = 'Sin valor';
            return;
        }
        if (val < 100) {
            gpaStatusPill.className = 'live-status-pill pill-normal';
            gpaStatusPill.textContent = '🟢 Normal';
        } else if (val >= 100 && val <= 125) {
            gpaStatusPill.className = 'live-status-pill pill-predia';
            gpaStatusPill.textContent = '🟡 Prediabetes';
        } else {
            gpaStatusPill.className = 'live-status-pill pill-diab';
            gpaStatusPill.textContent = '🔴 Límite Diabetes';
        }
    }

    function actualizarStatusHbA1c(val) {
        if (!hba1cStatusPill) return;
        if (isNaN(val) || val === null || val === '') {
            hba1cStatusPill.className = 'live-status-pill pill-neutral';
            hba1cStatusPill.textContent = 'Opcional';
            return;
        }
        if (val < 5.7) {
            hba1cStatusPill.className = 'live-status-pill pill-normal';
            hba1cStatusPill.textContent = '🟢 Normal';
        } else if (val >= 5.7 && val <= 6.4) {
            hba1cStatusPill.className = 'live-status-pill pill-predia';
            hba1cStatusPill.textContent = '🟡 Prediabetes';
        } else {
            hba1cStatusPill.className = 'live-status-pill pill-diab';
            hba1cStatusPill.textContent = '🔴 Límite Diabetes';
        }
    }

    function actualizarStatusPTOG(val) {
        if (!ptogStatusPill) return;
        if (isNaN(val) || val === null || val === '') {
            ptogStatusPill.className = 'live-status-pill pill-neutral';
            ptogStatusPill.textContent = 'Opcional';
            return;
        }
        if (val < 140) {
            ptogStatusPill.className = 'live-status-pill pill-normal';
            ptogStatusPill.textContent = '🟢 Normal';
        } else if (val >= 140 && val <= 199) {
            ptogStatusPill.className = 'live-status-pill pill-predia';
            ptogStatusPill.textContent = '🟡 Prediabetes';
        } else {
            ptogStatusPill.className = 'live-status-pill pill-diab';
            ptogStatusPill.textContent = '🔴 Límite Diabetes';
        }
    }

    function actualizarStatusCasual(val) {
        if (!casualStatusPill) return;
        if (isNaN(val) || val === null || val === '') {
            casualStatusPill.className = 'live-status-pill pill-neutral';
            casualStatusPill.textContent = 'Opcional';
            return;
        }
        if (val < 140) {
            casualStatusPill.className = 'live-status-pill pill-normal';
            casualStatusPill.textContent = '🟢 Normal';
        } else if (val >= 140 && val < 200) {
            casualStatusPill.className = 'live-status-pill pill-predia';
            casualStatusPill.textContent = '🟡 Elevado';
        } else {
            casualStatusPill.className = 'live-status-pill pill-diab';
            casualStatusPill.textContent = '🔴 Sospecha / Criterio';
        }
    }

    // Inicializar estados
    if (gpaNumberInput) actualizarStatusGPa(parseFloat(gpaNumberInput.value));

    // Listeners de inputs en vivo
    if (hba1cInput) {
        hba1cInput.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            actualizarStatusHbA1c(isNaN(val) ? '' : val);
        });
    }

    if (ptogInput) {
        ptogInput.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            actualizarStatusPTOG(isNaN(val) ? '' : val);
        });
    }

    if (casualInput) {
        casualInput.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            actualizarStatusCasual(isNaN(val) ? '' : val);
        });
    }

    // Sincronizar Slider con Input Numérico de Glucosa en Ayunas (GPa)
    if (glucosaRangeInput && gpaNumberInput) {
        glucosaRangeInput.addEventListener('input', (e) => {
            gpaNumberInput.value = e.target.value;
            actualizarStatusGPa(parseFloat(e.target.value));
        });

        gpaNumberInput.addEventListener('input', (e) => {
            let val = parseFloat(e.target.value);
            if (!isNaN(val)) {
                if (val > 250) glucosaRangeInput.value = 250;
                else if (val < 40) glucosaRangeInput.value = 40;
                else glucosaRangeInput.value = val;
                actualizarStatusGPa(val);
            } else {
                actualizarStatusGPa('');
            }
        });
    }

    // =========================================================================
    // CONTROL DE ALARMA MÉDICA Y SINTETIZADOR DE VOZ
    // =========================================================================
    function iniciarAlertaSonora() {
        detenerAlertaSonora(); // Limpiar previas
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;

            audioCtx = new AudioContext();

            function emitirBeepEmergencia() {
                if (!audioCtx || audioCtx.state === 'closed') return;
                
                const now = audioCtx.currentTime;
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();

                osc.type = 'sawtooth';
                // Frecuencia médica: 880 Hz a 1040 Hz
                osc.frequency.setValueAtTime(880, now);
                osc.frequency.exponentialRampToValueAtTime(1040, now + 0.15);

                gain.gain.setValueAtTime(0.3, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start(now);
                osc.stop(now + 0.25);
            }

            emitirBeepEmergencia();
            alarmInterval = setInterval(emitirBeepEmergencia, 450);
        } catch (e) {
            console.warn('No se pudo reproducir la alarma sonora:', e);
        }
    }

    function reproducirVozAlerta(texto) {
        if ('speechSynthesis' in window) {
            try {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(texto);
                utterance.lang = 'es-ES';
                utterance.rate = 0.92;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;

                const voices = window.speechSynthesis.getVoices();
                const vozEspañol = voices.find(v => v.lang.startsWith('es'));
                if (vozEspañol) {
                    utterance.voice = vozEspañol;
                }

                window.speechSynthesis.speak(utterance);
            } catch (e) {
                console.warn('Error al reproducir locución de voz:', e);
            }
        }
    }

    function detenerAlertaSonora() {
        if (alarmInterval) {
            clearInterval(alarmInterval);
            alarmInterval = null;
        }
        if (audioCtx) {
            try {
                audioCtx.close();
            } catch (e) {}
            audioCtx = null;
        }
        if ('speechSynthesis' in window) {
            try {
                window.speechSynthesis.cancel();
            } catch (e) {}
        }
    }

    // Listener para cerrar la alarma sonora y el modal
    if (btnCerrarAlerta) {
        btnCerrarAlerta.addEventListener('click', () => {
            detenerAlertaSonora();
            if (modalAlertaCritica) {
                modalAlertaCritica.classList.add('hidden');
            }
        });
    }

    // =========================================================================
    // =========================================================================
    // ENVÍO DE EVALUACIÓN DIAGNÓSTICA
    // =========================================================================
    async function realizarEvaluacion() {
        const formData = new FormData(diabetesForm);
        const data = {};
        
        // Recolectar todos los campos excepto los checkboxes de enfermedades (se manejan aparte)
        formData.forEach((value, key) => {
            if (key === 'enfermedades_previas') return; // Se procesa abajo
            if (value.trim() !== "") {
                data[key] = value.trim();
            }
        });

        // Capturar todos los checkboxes de enfermedades preexistentes seleccionados
        const enfermedadesChecked = Array.from(
            document.querySelectorAll('input[name="enfermedades_previas"]:checked')
        ).map(cb => cb.value);
        
        // Incluir el campo de otras enfermedades si se completó
        const otrasEnfermedades = document.getElementById('otras_enfermedades');
        if (otrasEnfermedades && otrasEnfermedades.value.trim()) {
            enfermedadesChecked.push(otrasEnfermedades.value.trim());
        }
        
        data['enfermedades_previas'] = enfermedadesChecked;

        // Asegurar estado de checkbox de síntomas
        const tieneSintomasCheck = document.getElementById('tiene_sintomas');
        if (tieneSintomasCheck) {
            data['tiene_sintomas'] = tieneSintomasCheck.checked ? 'si' : 'no';
        }


        // Feedback de carga
        btnEvaluar.disabled = true;
        btnEvaluar.innerHTML = `<span class="pulse-dot"></span> Evaluando Diagnóstico Clínico...`;

        try {
            const response = await fetch('/api/evaluar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.error || 'Ocurrió un error en la evaluación.');
                return;
            }

            // Renderizar Resultados
            renderizarResultados(result);

        } catch (err) {
            console.error('Error al comunicar con la API:', err);
            alert('No se pudo conectar con el servidor backend de evaluación.');
        } finally {
            btnEvaluar.disabled = false;
            btnEvaluar.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span>Ejecutar Evaluación Clínica</span>
            `;
        }
    }

    function renderizarResultados(res) {
        // Revelar panel de resultados
        resultsPlaceholder.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        // Notificación de estado de envío por correo
        const emailStatusBanner = document.getElementById('email-status-banner');
        const emailStatusText = document.getElementById('email-status-text');
        if (emailStatusBanner && emailStatusText) {
            if (res.correo_mensaje) {
                emailStatusBanner.classList.remove('hidden');
                emailStatusText.textContent = res.correo_mensaje;
            } else {
                emailStatusBanner.classList.add('hidden');
            }
        }

        // Actualizar datos del paciente en la ficha clínica
        if (resPacienteNombre) resPacienteNombre.textContent = res.nombre || 'Paciente';
        if (resPacienteTelefono) resPacienteTelefono.textContent = res.telefono || 'No especificado';
        if (resPacienteCorreo) resPacienteCorreo.textContent = res.correo || 'No especificado';
        if (resPacienteDireccion) resPacienteDireccion.textContent = res.direccion || 'No especificada';
        if (resPacienteAntecedentes) resPacienteAntecedentes.textContent = res.antecedentes_medicos || 'Sin antecedentes reportados';

        // Valor de Medición e Indicador Visual
        resGlucosaVal.textContent = typeof res.glucosa === 'number' ? `${res.glucosa} mg/dL` : `${res.glucosa}`;
        const percentage = Math.min(100, Math.max(0, res.porcentaje_medidor));
        gaugePointer.style.left = `${percentage}%`;

        // Diagnóstico y Esquema de Colores (adaptando fuente y contrastes según el color)
        resDiagnostico.textContent = res.diagnostico;
        resDiagnostico.style.color = res.color;
        resRiesgoBadge.textContent = `Riesgo: ${res.nivel_riesgo}`;
        resRiesgoBadge.style.borderColor = res.color;
        resRiesgoBadge.style.color = res.color;
        resRiesgoBadge.style.backgroundColor = `${res.color}15`;
        
        statusBanner.style.borderLeftColor = res.color;
        statusBanner.style.boxShadow = `0 4px 16px ${res.color}25`;

        // Motivo / Criterio Clínico
        resMotivo.textContent = res.motivo;

        // Factores de riesgo adicionales
        if (res.factores_riesgo && res.factores_riesgo.length > 0) {
            riskFactorsContainer.classList.remove('hidden');
            riskFactorsList.innerHTML = '';
            res.factores_riesgo.forEach(factor => {
                const li = document.createElement('li');
                li.textContent = factor;
                riskFactorsList.appendChild(li);
            });
        } else {
            riskFactorsContainer.classList.add('hidden');
        }

        // Recomendaciones
        resRecomendaciones.innerHTML = '';
        res.recomendaciones.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            resRecomendaciones.appendChild(li);
        });

        // EVALUACIÓN DE NIVELES CRÍTICOS / ALERTA DE ATENCIÓN CLÍNICA
        if (res.es_critico) {
            if (modalPacienteNombre) modalPacienteNombre.textContent = res.nombre || 'Paciente';
            if (modalPacienteContacto) {
                const contactos = [res.telefono, res.correo].filter(Boolean).join(' | ');
                modalPacienteContacto.textContent = contactos || 'Sin contacto directo';
            }

            const modalTitle = document.getElementById('modal-title');
            const modalSubtitle = document.getElementById('modal-subtitle');
            const modalWarningMsg = document.getElementById('modal-warning-msg');

            let textoVoz = "";

            if (res.categoria_codigo === 'prediabetes') {
                if (modalTitle) modalTitle.textContent = '⚠️ ¡ALERTA CLÍNICA - PREDIABETES DETECTADA!';
                if (modalSubtitle) modalSubtitle.textContent = 'Se han detectado niveles de glucemia en rango de Prediabetes (GPa 100-125 mg/dL, HbA1c 5.7-6.4% o PTOG 140-199 mg/dL).';
                if (modalWarningMsg) {
                    modalWarningMsg.innerHTML = '<strong>⚠️ Indicación Médica:</strong> El paciente presenta un nivel de riesgo moderado/intermedio. Se recomienda agendar una consulta médica para adoptar cambios preventivos en el estilo de vida y realizar seguimiento.';
                }
                textoVoz = "Alerta, atención. Presentas prediabetes, comunícate con tu médico de confianza y asiste a consulta para prevención.";
            } else {
                if (modalTitle) modalTitle.textContent = '🚨 ¡ALERTA DE ATENCIÓN CLÍNICA URGENTE!';
                if (modalSubtitle) modalSubtitle.textContent = 'Se ha detectado un nivel de glucosa en rango crítico / límite diagnóstico de Diabetes Mellitus (GPa ≥ 126 mg/dL, HbA1c ≥ 6.5% o PTOG/Casual ≥ 200 mg/dL).';
                if (modalWarningMsg) {
                    modalWarningMsg.innerHTML = '<strong>⚠️ Indicación Médica Inmediata:</strong> El paciente ha alcanzado o superado el umbral clínico de diabetes. Por favor diríjase de inmediato a consulta médica para recibir evaluación y manejo terapéutico profesional.';
                }
                textoVoz = "Alerta, atención. Presentas diabetes alta, comunícate con tu médico de confianza y asiste lo más rápido a consulta.";
            }

            if (modalAlertaCritica) {
                modalAlertaCritica.classList.remove('hidden');
            }
            // Disparar alarma auditiva sintetizada (beeps) y voz hablada en español
            iniciarAlertaSonora();
            reproducirVozAlerta(textoVoz);
        } else {
            detenerAlertaSonora();
            if (modalAlertaCritica) modalAlertaCritica.classList.add('hidden');
        }

        // Scroll suave en móviles
        if (window.innerWidth < 920) {
            document.getElementById('results-card').scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Listener para el botón de envío
    btnEvaluar.addEventListener('click', realizarEvaluacion);
});
