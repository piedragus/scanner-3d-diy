# Onboarding — Para quien retome este proyecto

Guía rápida para entender el estado del proyecto sin tener que leer todo el historial de decisiones.

## Por dónde empezar

1. Leé el `README.md` para la visión general de los dos proyectos.
2. Andá al `ARCHITECTURE.md` del proyecto que te interese (`precision-part/` o `isla-giratoria/`) — cada uno tiene:
   - **Decisiones cerradas**, organizadas por subsistema.
   - **Gaps pendientes**, con lo que falta resolver antes de poder avanzar a firmware/hardware real.
   - **Historial de decisiones revertidas**, para entender *por qué* algo no quedó como en el documento original (evita repetir una discusión ya cerrada).
3. El `ROADMAP.md` tiene las fases (0 a IV) de cada proyecto y qué corresponde a cada una.
4. Los **Issues** de este repo reflejan los gaps pendientes listados en cada `ARCHITECTURE.md` — son el punto de entrada más directo si querés ponerte a trabajar en algo concreto ahora mismo.

## Glosario rápido (términos usados en los docs)

- **ToF** — Time of Flight, sensor de distancia.
- **DVP** — Digital Video Port, interfaz paralela de cámara compatible con ESP32 (a diferencia de MIPI-CSI, que no lo es).
- **FMCW** — Frequency Modulated Continuous Wave, técnica de radar usada en Isla Giratoria (chirp de frecuencia, mide distancia por beat-frequency).
- **SDR** — Software Defined Radio, plataforma de radio genérica programable (ej. PlutoSDR, LimeSDR).
- **SfM / MVS** — Structure from Motion / Multi-View Stereo, técnicas de fotogrametría para reconstrucción 3D desde múltiples fotos.
- **Home switch** — sensor de referencia de posición angular "cero", usado para corregir deriva de conteo de pasos en los steppers.
- **Gauge block escalonado** — pieza patrón con escalones de altura conocida, usada para calibrar el plano de cada línea láser contra cada cámara.
- **TGC** — Time-Gain Control (término de ultrasonido, relevante solo porque se evaluó y descartó un chip de esa familia para Isla Giratoria).

## Filosofía de trabajo de este proyecto

- **No se escribe código ni se fabrica hardware hasta cerrar la arquitectura.** Las discusiones de diseño son iterativas y verbales/escritas antes de comprometer una decisión.
- **Los cambios de alcance se documentan, no se borran.** Si releés algo que contradice una decisión anterior, buscá primero en "Historial de decisiones revertidas" — probablemente ya se discutió el porqué.
- Preguntas abiertas grandes (ej. form factor del subsistema RF de Isla Giratoria) están marcadas explícitamente como "sin definir", no asumidas.

## Estado al momento de este commit (17 agosto 2026)

- **Precision Part:** arquitectura casi cerrada. Falta ejecutar la calibración de planos láser (12 combinaciones) — es el gap bloqueante para pasar a Fase I de firmware.
- **Isla Giratoria:** arquitectura de plataforma (mecánica, dual-MCU, energía) cerrada. El subsistema de radar (RF) está en fase conceptual — se definió el enfoque (TX simple + RX array, FMCW, SDR) pero no hay hardware ni form factor decidido todavía.
