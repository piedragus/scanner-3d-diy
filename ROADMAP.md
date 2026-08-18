# Roadmap

## Estado actual: revisión de arquitectura (sin código, sin hardware fabricado)

Ambos proyectos están en etapa de diseño iterativo — resolviendo gaps e inconsistencias antes de comprometer firmware o fabricación. Ver `ARCHITECTURE.md` de cada proyecto para el detalle completo.

---

## Precision Part

### Fase 0 — Cerrar gaps de arquitectura (en curso)
- [ ] Calibración de los 12 planos láser (4 emisores × 3 cámaras) — requiere gauge block escalonado (fabricar/comprar) + script de calibración (retroproyección + fit por SVD).
- [ ] Definir umbral de tolerancia de descentrado (ToF).
- [ ] Confirmar lente/FOV de las cámaras OV5640.
- [ ] Caracterizar ancho/perfil de línea láser en función de distancia (por módulo real comprado).

### Fase I — Firmware (ESP32-S3)
- Control de posición angular del turntable vía TMC2209 (UART, micropasos).
- Lógica de home switch (single/double flank) + corrección de contador de pasos en vivo.
- Disparo simultáneo de 4 emisores láser + captura sincronizada de 3 cámaras.
- Secuencia de preview: ToF (radio + centrado) + estimación de altura por cámara → cálculo de paso angular adaptativo.

### Fase II — Hardware
- Montaje de torre con 3 cámaras en arco vertical + 4 emisores láser (posiciones de azimut/tilt/rotación de plano ya definidas).
- Fabricación o compra del gauge block escalonado.
- Validación mecánica del turntable (vibración, settling time real).

### Fase III — Procesamiento (PC)
- Pipeline de fotogrametría (SfM + MVS) como reconstrucción base.
- Pipeline de triangulación láser (detección de línea + retroproyección con planos calibrados) como anclaje métrico.
- Fusión de ambas nubes de puntos (escala + corrección de drift).
- Exportación a .PLY.

### Fase IV — Validación
- Escaneo de piezas patrón de dimensiones conocidas, medición de error real vs. teórico.
- Ajuste de paso angular / tiempos de captura según resultados.

---

## Isla Giratoria

### Fase 0 — Cerrar gaps de arquitectura (en curso)
- [ ] Definir form factor del subsistema RF (separado del cubo de Precision Part).
- [ ] Resolver interfaz LiDAR (UART vs I2C).
- [ ] Formalizar ubicación física de MCUs (Lado A/B).
- [ ] Actualizar conexión de shielding EMI al punto de unión de ground correcto.

### Fase I — Firmware
- ESP32 WROOM: driver SPI ADS1256, lectura de 3 home switches con detección de fallo por mayoría, control TMC2209.
- ESP32-S3: driver de cámara OV5640, térmica MLX90640, LiDAR, FatFS sobre SD, lógica de Wi-Fi burst ("radio silence").
- Protocolo UART entre ambos MCU (step_count, home_flag_id, timestamp).

### Fase II — Hardware
- Balanceo dinámico Lado A/Lado B.
- Ground plane separado (AGND/DGND, punto único).

### Fase II-RF — Subsistema de radar (nueva rama de trabajo, en paralelo)
- [ ] Prototipo mínimo: 1x ADALM-PLUTO, validar FMCW básico (medir distancia por beat-frequency) sin array ni pared de por medio.
- [ ] Escalar a 2 canales (2x Pluto o LimeSDR 2x2) — validar concepto de diferencia de fase para estimar ángulo.
- [ ] Evaluar necesidad de escalar a ADALM-PHASER (8RX/2TX) según resultados del prototipo.
- [ ] Definir downconversion + cadena RF completa una vez validado el concepto en SDR.
- [ ] Revisar proyectos open (GNU Radio FMCW, radar MIMO 4x4, algoritmos RPCA para separar clutter de pared) antes de diseñar desde cero.

### Fase III — Procesamiento
- Visor WebXR (Three.js) — capas RGB / térmica / RF por frecuencia, con offsets y matriz de calibración vía JSON.
- Algoritmo de reconstrucción de mapa RF (rango-ángulo desde el RX array).

### Fase IV — Validación
- Pruebas de campo en entornos controlados, sintonía de filtros FIR.
- Validación de precisión del mapa RF contra estructuras conocidas.

---

## Notas de proceso

- Se prioriza revisión verbal de arquitectura antes de comprometer código o compras grandes.
- Cambios de alcance se documentan en la sección "Historial de decisiones revertidas" de cada `ARCHITECTURE.md`, no se borran silenciosamente.
