# Documento Técnico Original: Sistemas de Escaneo Multimodal (v1.0)

**Fecha:** 14 de agosto, 2026
**Estado:** Documento histórico de referencia — muchas decisiones aquí fueron revisadas. Ver `ARCHITECTURE.md` de cada proyecto para el estado actual.

---

Este documento se conserva como snapshot del punto de partida. Cambios clave respecto a este documento:

- Cámara IMX219 (MIPI-CSI) → reemplazada por OV5640 (DVP), incompatible nativo con ESP32.
- Slip ring en Isla Giratoria → eliminado (era un error de diseño).
- Encoder AS5048A → descartado por conflicto con eje hueco → 3 home switches ópticos.
- Baterías 2x18650 → 2x21700.
- Radar RF pasivo → redefinido como radar activo de penetración de paredes (through-wall imaging).
- Turntable de Precision Part → arquitectura de reconstrucción invertida: fotogrametría como base, láser como anclaje métrico (no al revés).

Ver el historial completo de decisiones en cada `ARCHITECTURE.md`.

(Contenido completo del documento original disponible en el historial de conversación del proyecto — pendiente de transcripción completa a este archivo si se necesita como referencia textual exacta.)
