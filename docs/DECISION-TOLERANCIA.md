# Decisión de tolerancia (issue #2) — borrador para OK

Fecha: 2026-10-12. Origen: respuesta de Agustín.

## Datos
- Descentrado de pieza sobre el giratorio: se supone **5 mm** (valor de diseño, sin medir).
- Error objetivo de medición: **0,25 mm**.
- El sensor ToF no se usa para "rechazar" piezas descentradas: sirve para **corregir matemáticamente** la medición.

## Decisión propuesta
1. El descentrado de hasta 5 mm es aceptado; no hay umbral de rechazo. El ToF mide la distancia al borde en cada ángulo y el software ajusta el centro de rotación real (ajuste de círculo/elipse por mínimos cuadrados) y resta esa excentricidad.
2. El 0,25 mm es el objetivo del sistema completo, no del ToF solo. Se busca con **pasadas sucesivas multiplexadas**: varias vueltas, con la pieza en distinta fase o reposicionada, y se promedian/fusionan. El error aleatorio baja ~1/√N; el error sistemático (fase, calibración) se detecta al comparar pasadas.
3. Validación: medir un patrón (cilindro o pin calibrado) a 0 y 5 mm de descentrado, N = 1, 4 y 8 pasadas, y reportar error vs N. Si con N=8 no se llega a 0,25 mm, el límite está en el ToF y se reabre la discusión (otro sensor o triangulación láser).

## Qué cierra y qué no
- Cierra #2 (umbral): no hay umbral; hay modelo de corrección + objetivo 0,25 mm.
- Sigue abierto: si se compra un PlutoSDR (#5, #8, #9), independiente de esta decisión.
- Riesgo: la resolución típica de un ToF barato (VL53L1X) es del orden de 1 mm; llegar a 0,25 mm depende del promediado y puede no alcanzar. Hay que medirlo antes de comprometer la cifra.
