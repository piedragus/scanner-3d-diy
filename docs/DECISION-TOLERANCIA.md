# Decisión de tolerancia (issue #2)

Fecha: 2026-10-12. Origen: respuestas de Agustín.

## Dos números distintos
- **Descentrado de la pieza sobre el giratorio: lo mide el ToF.** Se supone hasta **5 mm** (valor de diseño, sin medir). No es una tolerancia a cumplir ni un umbral de rechazo: es la magnitud que el ToF mide para corregirla.
- **0,25 mm: exactitud dimensional deseada de la pieza medida** (objetivo del escáner, no del ToF).

## Decisión
1. Issue #2 (umbral de descentrado): no hay umbral de rechazo. Se acepta hasta ~5 mm; el ToF mide la excentricidad en cada ángulo y el software la compensa (ajuste de centro de rotación por mínimos cuadrados) antes de calcular dimensiones.
2. Objetivo de exactitud dimensional: 0,25 mm, a buscar con pasadas sucesivas multiplexadas (varias vueltas, fase o posición distinta, fusionadas). El error aleatorio baja ~1/√N; el sistemático se detecta comparando pasadas.
3. Validación: pieza patrón calibrada (cilindro/pin/gauge) a 0 y 5 mm de descentrado, N = 1, 4 y 8 pasadas, error vs N. Si con N = 8 no se llega a 0,25 mm, reabrir (otro sensor o triangulación láser).

## Riesgos
- La corrección es tan buena como la resolución del ToF: un VL53L1X típico ronda 1 mm. Hay que medir el piso real antes de comprometer 0,25 mm.
- Un descentrado grande puede sacar la pieza del foco/FOV de cámaras y láseres; verificar que 5 mm no lo haga.

## Aparte: PlutoSDR
ADALM-PLUTO = SDR de Analog Devices (~USD 100-150) para el subsistema RF de la isla giratoria (radar FMCW que atraviesa paredes, ver isla-giratoria/ARCHITECTURE.md). Sirve para validar FMCW básico antes de invertir más. No tiene relación con esta decisión ni con la medición de piezas.
