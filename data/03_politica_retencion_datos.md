# Política de Clasificación y Retención de Datos - Company Cloud

## 1. Clasificación de Activos de Información
La información procesada y almacenada en Company Cloud se clasifica en cuatro categorías de criticidad:
- **Nivel 1 - Público:** Información destinada a divulgación general (documentación abierta de API, artículos de marketing).
- **Nivel 2 - Interno:** Datos operativos de uso exclusivo de empleados (diagramas de red internos, actas de reuniones técnicas).
- **Nivel 3 - Confidencial:** Información comercial sensible, métricas financieras agregadas y código fuente propietario.
- **Nivel 4 - Crítico / PII:** Datos de identificación personal de usuarios (nombres, correos, documentos de identidad, información de tarjetas de crédito).

## 2. Períodos de Retención de Datos
- **Registros de Auditoría y Acceso (Logs):** Se conservan durante **365 días calendario** en almacenamiento frío (Cold Storage) cifrado mediante AES-256-GCM.
- **Datos de Cuenta de Usuarios Activos:** Se mantienen durante la vigencia del contrato de servicio.
- **Datos tras Cancelación de Cuenta:** Los datos operativos se eliminan a los **30 días** posteriores a la baja del cliente.
- **Registros Contables y de Facturación:** Por exigencias legales y fiscales, se conservan durante un período obligatorio de **5 años fiscales**.

## 3. Protocolo de Anonimización y Privacidad
Antes de transferir datos de telemetría a almacenes de analítica como BigQuery o Snowflake:
- Se eliminan las columnas que contienen nombres, emails o direcciones IP.
- Los identificadores de usuario (`user_id`) se reemplazan mediante un hash irreversible utilizando el algoritmo **SHA-256 con Salt secreta rotativa**.
- Cualquier conjunto de datos resultante debe contener un tamaño de cohorte mínima de `k=10` para prevenir ataques de reidentificación estadística.

## 4. Destrucción Segura de Medios de Almacenamiento
- La eliminación lógica de bases de datos se realiza ejecutando sobreescritura criptográfica (Cryptographic Erasure / Crypto-shredding), destruyendo la clave de descifrado del volumen.
- Los discos de hardware retirados en centros de datos físicos deben pasar por desmagnetización y posterior destrucción física certificada con trituración a partículas de tamaño menor a 2 milímetros.

