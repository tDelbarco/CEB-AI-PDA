# 🤖 CEB-AI: Chrome Extension Builder AI

## 🌟 Visión General

**CEB-AI** (Chrome Extension Builder AI) es una **Plataforma de Creación Asistida por IA** diseñada para que los usuarios puedan generar rápidamente **Extensiones de Chrome personalizadas**. Estas extensiones buscan **añadir funcionalidades o mejorar la experiencia** en sitios web específicos.

El núcleo del proyecto es un ecosistema de **mejora continua**, donde los usuarios tienen la **posibilidad de colaborar** para elevar la calidad y funcionalidad de las extensiones creadas en la plataforma.

---

## 🎯 Objetivos Clave

| Eje del Proyecto | Descripción |
| :--- | :--- |
| **Creación de Funcionalidades** | Crear extensiones funcionales (HTML, JS, CSS, Manifest V3) que añaden características a sitios web que estos no ofrecen, usando **Python** como *backend* de orquestación. |
| **Análisis de Selectores** | Implementar un sistema inteligente para ayudar a los usuarios a obtener **identificadores y selectores clave** del HTML de los sitios web, facilitando la creación del *prompt*. |
| **Colaboración (PDA)** | Establecer la **Plataforma de Desarrollo Abierto (PDA)**, un ecosistema donde las funcionalidades de las extensiones pueden ser **mejoradas y extendidas** por la comunidad a través de contribuciones. |
| **Ética y Enfoque** | Asegurar que las extensiones generadas mejoren la experiencia del usuario (ej., productividad), **sin afectar modelos de negocio legítimos**. |

---

## ⚙️ Arquitectura y Metodología

### 1. Gestión Inteligente del Contexto (RAG System)

La alta precisión en la generación de código se logra mediante un sistema que **reutiliza inteligentemente la lógica de código existente** de extensiones ya probadas.

* El sistema identifica las funcionalidades específicas requeridas por el *prompt* del usuario.
* Solo los fragmentos de código de extensiones anteriores que realizan tareas similares se inyectan en el *prompt* de Gemini, asegurando la **coherencia del código** y la **eficiencia del *pipeline***.

### 2. Análisis de Selectores Inteligentes (EIS)

Esta funcionalidad simplifica la interacción del usuario al automatizar la identificación de selectores CSS.

* **Captura Dinámica:** El usuario utiliza una **Extensión Auxiliar de Chrome** para obtener el **HTML en su estado final y dinámico** de la página de destino.
* **Inferencia Semántica:** El HTML capturado se envía a la aplicación, donde se analiza la estructura del HTML que se complementa con una descripción del usuario, e **identifica los atributos y selectores clave** que son ideales para la creación de la extensión.

### 3. Modelo de Feedback Granular y Colaboración

El desarrollo se enfoca en la **trazabilidad de la calidad**. Los usuarios evalúan **funcionalidades específicas** dentro de una extensión.

* Esto genera **datos precisos sobre fallos**, lo que permite a otros usuarios corregir estos fallos o **añadir nuevas funcionalidades** a las extensiones de otro usuario.
