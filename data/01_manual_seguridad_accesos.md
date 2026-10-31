# Política de Seguridad y Control de Accesos - NovaCore Cloud

## 1. Alcance y Objetivos
Este documento define los estándares obligatorios de seguridad lógica y control de acceso a la infraestructura de servidores, clústeres y bases de datos de NovaCore Cloud. Aplica a todos los colaboradores, contratistas y sistemas automatizados.

## 2. Autenticación Multifactor (MFA)
- La autenticación multifactor es estrictamente obligatoria para todas las cuentas de usuario con acceso a la red corporativa y consolas administrativas.
- Métodos aprobados: Llaves de seguridad de hardware FIDO2 (YubiKey) y aplicaciones autenticadoras TOTP (Google Authenticator, Microsoft Authenticator).
- Los métodos basados en SMS o llamadas telefónicas quedan expresamente prohibidos por su vulnerabilidad ante ataques de SIM swapping.

## 3. Ciclo de Vida y Rotación de Credenciales
- **Contraseñas humanas:** Deben contener al menos 16 caracteres alfanuméricos y símbolos especiales. La rotación periódica es obligatoria cada 90 días calendario.
- **Service Accounts y API Keys:** Las claves de acceso de aplicaciones deben rotarse de forma automatizada cada 30 días.
- **Bloqueo por intentos fallidos:** Una cuenta quedará temporalmente bloqueada tras 5 intentos fallidos consecutivos durante un período de 15 minutos.

## 4. Matriz de Control de Acceso Basado en Roles (RBAC)
Los accesos se gestionan aplicando el principio de menor privilegio (Least Privilege) mediante cuatro roles estándar:
- **Role Admin:** Acceso completo para configuración de infraestructura, administración de usuarios y políticas de facturación.
- **Role Operator:** Permiso de despliegue, reinicio de servicios, gestión de contenedores y visualización de métricas operativas.
- **Role Auditor:** Acceso de solo lectura a registros de auditoría, logs de trazabilidad y configuraciones de compliance.
- **Role Developer:** Acceso a entornos de desarrollo y staging, con permisos de lectura limitados en métricas de producción.

## 5. Acceso a la Red y Túneles VPN
- Todo acceso a las consolas de administración internas debe cursarse a través del túnel VPN propietario **NovaGate**.
- El gateway de NovaGate opera exclusivamente en el puerto seguro **TCP 8443**.
- Las sesiones inactivas de VPN se terminarán automáticamente tras 60 minutos de inactividad.

## 6. Procedimiento de Revocación de Emergencia
En caso de sospecha de compromiso o despido de personal:
1. El equipo de Seguridad de la Información (SecOps) ejecuta el script `novactl auth revoke --user <id>`.
2. Se invalidan todos los tokens JWT activos en el Redis Session Store en menos de 60 segundos.
3. Se rotan de inmediato las llaves maestras de cifrado que pudieran haber estado expuestas.

