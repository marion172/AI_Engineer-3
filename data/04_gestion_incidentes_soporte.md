# Protocolo de Gestión de Incidentes y Soporte Técnico - Company Cloud

## 1. Niveles de Severidad y Matriz de SLA
Los incidentes en Company Cloud se tipifican según el impacto en la operación y los usuarios, estableciendo los siguientes Acuerdos de Nivel de Servicio (SLA):

| Nivel | Definición | Tiempo Máximo de Primera Respuesta | Frecuencia de Actualización de Estado |
|---|---|---|---|
| **Sev-1 (Crítico)** | Caída total de la plataforma, indisponibilidad de API principal o filtración masiva de datos. | **15 minutos** | Cada 30 minutos |
| **Sev-2 (Mayor)** | Degradación severa del servicio afectando a más del 25% de usuarios sin alternativa o workaround. | **1 hora** | Cada 2 horas |
| **Sev-3 (Menor)** | Falla parcial en componente no crítico; existe un procedimiento de mitigación temporal. | **8 horas hábiles** | Cada 24 horas |
| **Sev-4 (Cosmético)** | Errores menores de interfaz gráfica, inconsistencias tipográficas o peticiones de mejora. | **48 horas hábiles** | Semanal |

## 2. Protocolo de Escalamiento para Incidentes Sev-1
1. **Detección y Notificación:** Las alertas de monitoreo (Datadog/PagerDuty) disparan llamadas directas al teléfono del Ingeniero de Guardia On-Call.
2. **Apertura de War Room:** El ingeniero de guardia abre de inmediato una sala de videollamada de emergencia y un canal de Slack dedicado `#incident-sev1-[fecha]`.
3. **Escalamiento Obligatorio:** Si la causa raíz no es identificada en los primeros **20 minutos**, se escala automáticamente al Engineering Lead y al Director de Infraestructura.
4. **Comunicaciones a Clientes:** El Incident Commander publica actualizaciones en la página pública de estado (`status.Company.io`) dentro de los 30 minutos posteriores a la confirmación de la falla.

## 3. Análisis de Causa Raíz (Post-Mortem / RCA)
- Para todo incidente calificado como Sev-1 o Sev-2, es obligatorio redactar y publicar un documento de Post-Mortem sin culpas (Blameless Post-Mortem).
- El plazo máximo para la presentación del Post-Mortem preliminar es de **72 horas** posteriores a la resolución del incidente.
- El documento debe incluir: línea temporal precisa de los eventos, causa raíz identificada, impacto medido (usuarios y transacciones perdidas) y un plan de acción correctivo con dueños asignados.

