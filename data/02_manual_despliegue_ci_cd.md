# Manual de Despliegue Continuo y Flujo CI/CD - Company Cloud

## 1. Modelo de Ramas (Branching Strategy)
Company adopta un modelo de desarrollo basado en tronco (Trunk-Based Development):
- La rama `main` contiene el código que refleja el estado de producción o listo para producción.
- Las ramas de funcionalidad (feature branches) deben tener un ciclo de vida corto, no mayor a 48 horas.
- Todo Pull Request (PR) requiere la aprobación obligatoria de al menos 2 pares revisores (code reviewers) y la aprobación del pipeline de validación automatizada.

## 2. Pipeline de Integración Continua (CI)
Cada commit entrante a una rama o PR dispara la siguiente secuencia de checks:
1. **Linting y Estilo:** Validación estricta con Flake8, Ruff y Prettier.
2. **Análisis Estático de Seguridad (SAST):** Escaneo de vulnerabilidades mediante Semgrep y Trivy.
3. **Pruebas Unitarias y de Integración:** Requiere una cobertura de código mínima del **80%** medida con pytest-cov. Si la cobertura cae por debajo del 80%, el pipeline se interrumpe automáticamente.

## 3. Estrategia de Despliegue en Producción
- Se utiliza la técnica de **Blue-Green Deployment** para garantizar cero tiempo de inactividad (Zero Downtime).
- El ambiente inactivo (ej. Green) recibe el tráfico nuevo de forma progresiva mediante un balanceador de carga NGINX.
- Se mantiene un monitoreo activo durante los primeros 15 minutos posteriores al corte de tráfico.

## 4. Criterios de Rollback Automatizado
El sistema de orquestación revertirá el tráfico al ambiente anterior de manera inmediata y sin intervención humana si se detecta alguna de las siguientes anomalías durante la ventana de evaluación de 5 minutos:
- Tasa de errores HTTP (códigos 5xx) superior al **1.5%** del total de peticiones.
- Latencia en el percentil 99 (p99) superior a **800 milisegundos**.
- Caída o fallo de salud en más del 20% de las instancias de pods en Kubernetes.

## 5. Ventanas Horarias de Despliegue
- Los despliegues programados a producción solo están permitidos los días **Martes y Jueves entre las 10:00 y las 14:00 UTC**.
- Quedan estrictamente prohibidos los despliegues los días Viernes, fines de semana o vísperas de feriados corporativos, salvo excepciones de parches de seguridad críticos autorizados por el CTO.

