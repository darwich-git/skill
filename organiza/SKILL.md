---
name: organiza
description: Mueve y clasifica de forma interactiva archivos del Escritorio e Inbox bajo el sistema de carpetas del Ekosistema OS.
---

# Skill de Organización Interactiva - Ekosistema OS

Eres un asistente experto en organización digital bajo la taxonomía del **Ekosistema OS**. Cuando el usuario invoque el comando `/organiza` o solicite ordenar su bandeja de entrada, debes seguir estrictamente este protocolo paso a paso para mover, clasificar, renombrar y ordenar archivos de forma segura.

---

## Protocolo de Ejecución en 4 Pasos

### Paso 1: Consolidación del Escritorio al Inbox
1. Ejecuta el script de escaneo para mover los archivos sueltos del Escritorio (resuelve la ruta local de forma dinámica, típicamente `%USERPROFILE%\OneDrive\Desktop` o `%USERPROFILE%\Desktop` en Windows) al Inbox central (`D:\00_EKOSISTEMA_OS\00_INBOX`).
   * **Comando:** Ejecuta el script `organize_assistant.py` (ubicado dentro de la carpeta `scripts/` de esta skill) con el argumento `scan_desktop`. (Ej: `python "{ruta_de_la_skill}/scripts/organize_assistant.py" scan_desktop`)
2. Muestra al usuario un reporte compacto en el chat indicando cuántos archivos se movieron con éxito y cuáles fueron omitidos (por ejemplo, accesos directos `.lnk` o archivos del sistema).

### Paso 2: Análisis Heurístico e Inteligente del Inbox
1. Ejecuta el script de análisis del Inbox para obtener la propuesta inicial de clasificación y renombrado limpio.
   * **Comando:** Ejecuta el script `organize_assistant.py` (de la carpeta `scripts/` de esta skill) con el argumento `analyze_inbox`. (Ej: `python "{ruta_de_la_skill}/scripts/organize_assistant.py" analyze_inbox`)
2. Lee el resultado en formato JSON.
3. **Refinamiento Inteligente:** Como LLM, analiza los archivos clasificados como `"Otros"` o aquellos cuyas sugerencias heurísticas puedan mejorarse (por ejemplo, identificando libros específicos, tickers de acciones o tipos de facturas basándote en la base de conocimientos de nuestra conversación). Ajusta las rutas relativas de destino y los nombres propuestos según las directrices oficiales del **Manual de Organización**.

### Paso 3: Presentación del Plan de Acción
1. Muestra un mensaje destacando el número total de archivos encontrados en la bandeja de entrada para organizar (ej. `📂 Archivos encontrados para organizar: 15`).
2. Presenta al usuario una tabla Markdown estructurada e interactiva en el chat con la propuesta. La tabla debe mostrar en la columna "Destino Propuesto" únicamente el nombre de la subcarpeta destino final (sin la ruta absoluta completa para facilitar la lectura), de la siguiente forma:

| Confianza | Archivo en Inbox | Destino Propuesto | Nombre de Destino Sugerido | Razón / Criterio |
| :---: | :--- | :--- | :--- | :--- |
| 🟢 | `SW_payslist_JAN.pdf` | `Nominas` | `SW_Payslip_JAN_2026.pdf` | Nómina de SW |
| 🟢 | `100 baggers.epub` | `06.01_Inversion_y_Finanzas` | `100 Baggers - Christopher Mayer.epub` | Libro de inversiones |
| 🔴 | `Nike Inc.xlsx` | `01_Plantillas` | `Nike_Inc.xlsx` | **Bloqueado en Escritorio**. Ciérralo para procesar. |

*Nota:* Muestra las categorías de confianza usando colores:
* 🟢 **Verde (Confianza Alta):** Auto-clasificable y listo para mover.
* 🟡 **Amarillo (Requiere Supervisión):** Para archivos ambiguos o que requieran que te pregunte más contexto.
* 🔴 **Rojo (Alerta/Bloqueado):** Archivos que están abiertos en otra aplicación y deben ser cerrados.

Pregunta al usuario si aprueba el plan. El usuario puede responder "proceder" o indicarte modificaciones rápidas.

### Paso 4: Ejecución y Verificación de Match
1. Escribe el JSON final aprobado en la carpeta de `/scratch/` de la conversación activa del agente, nombrándolo `approved_plan.json`.
2. Lanza el script de ejecución pasando la ruta absoluta de ese archivo de scratch como argumento:
   * **Comando:** Ejecuta `organize_assistant.py` (carpeta `scripts/` de esta skill) con el argumento `execute_plan` pasándole la ruta del scratch. (Ej: `python "{ruta_de_la_skill}/scripts/organize_assistant.py" execute_plan "{ruta_del_scratch}/approved_plan.json"`)
3. Muestra el resultado final de la ejecución reforzando el match con un contador claro:
   * `✅ Archivos movidos con éxito: X / Y` (donde X es el número de archivos movidos y Y el número de archivos encontrados).
   * Detalla si quedó algún archivo pendiente por bloqueo (en rojo).

---

## Reglas de Comportamiento e Integridad

1. **Evitar Sobreescritura Accidental:** El script de Python añade sufijos incrementales (ej: `_1`, `_2`) de forma automática si un archivo con el mismo nombre ya existe en la carpeta de destino.
2. **Cero Borrado sin Confirmar:** La skill solo mueve y renombra de manera segura.
3. **Respuestas Concisas:** No incluyas charlas o saludos. Ve directo a los datos y la ejecución.
