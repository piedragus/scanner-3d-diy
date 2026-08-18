# Isla Giratoria — Arquitectura

Escáner multimodal de habitaciones: LiDAR + térmica + RF de penetración de paredes. Nodo completamente autónomo y giratorio. Caso de uso: inspección a pedido (industria 4.0) — mapear el interior de paredes de una planta o vivienda para el propio dueño/cliente, con salida en mapa de realidad aumentada.

## Decisiones cerradas

### Mecánica y montaje
- **Sin slip ring** (estaba en la spec original, se identificó como error/alucinación) — nodo 100% autónomo, batería, MCU, sensores y almacenamiento giran solidarios.
- Distribución de peso simétrica: **Lado A (bloque óptico) / Lado B (bloque RF)**, para cancelación de momento de inercia.

### Electrónica — dual MCU
- **ESP32 WROOM** (tiempo-crítico): ADC ADS1256 (30kSPS, SPI), 3 home switches (interrupciones), control TMC2209 (UART).
- **ESP32-S3** (carga pesada): cámara OV5640 (DVP), térmica MLX90640, LiDAR TFmini Plus, SD (FatFS), Wi-Fi en ráfagas.
- Comunicación entre ambos: **UART**, el WROOM manda paquetes cortos `{step_count, home_flag_id, timestamp_local}`, el S3 los usa para timestampear/geo-referenciar angularmente cada frame que guarda.
- Motivo del split: un solo MCU (S3) tiene riesgo real de contención (DMA de cámara + JPEG encoding + Wi-Fi burst compitiendo con el muestreo de ADC de baja latencia y el conteo de pasos) — separar responsabilidades elimina ese riesgo sin necesitar optimización fina de RTOS/scheduling.

### Referencia angular
- **3 home switches ópticos montados en el rotor** (no en la base — la base solo tiene una flag pasiva sin electrónica), separados 120° entre sí.
- Detección de fallo por mayoría: se comparan los 3 intervalos angulares entre flancos consecutivos (A→B, B→C, C→A); si uno difiere de los otros dos (que coinciden entre sí), se aísla el segmento con anomalía sin descartar la corrección de los otros dos.
- Conteo de pasos del stepper como referencia continua entre home switches.
- **Se evaluó y se descartó** aplicar el mismo truco de flanco simple/doble del turntable de Precision Part (reducir a 1 sensor) — en Isla Giratoria los 3 sensores existen para dar *redundancia de arbitraje por mayoría*, algo que un solo sensor con patrón de pulso no puede proveer (no hay con qué contrastar una lectura ambigua o ruidosa).

### Energía
- **2x 21700, 2S1P** — una celda por lado del eje (A óptico / B RF), aprovechando la simetría de balance ya definida.
- Se descartaron: 9V litio primaria (autonomía real ~20-40min bajo la carga del sistema, no recargable), 18650 2S1P (menor autonomía que 21700 a igual cantidad de celdas), 18650 2S2P (mismo total de celdas que 21700 2S1P pero más volumen total y más soldaduras).
- Autonomía estimada: ~4.5-5h.

### Ground / EMI
- **AGND/DGND separados, unión de punto único** — necesario por la combinación de ADC de 24 bits + etapas RF sensibles a ruido de conmutación digital en la misma plataforma.
- Pendiente actualizar en la spec: el shielding de cobre (EMI) debe conectarse explícitamente al punto de unión definido, no a "GND común" como decía el documento original.

### Sensores (no-RF)
- LiDAR TFmini Plus — geometría 3D.
- Térmica MLX90640 — mapa de calor (fugas, instalaciones).
- Cámara OV5640 (mismo módulo que Precision Part).

## Subsistema RF — objetivo redefinido

**No es medición pasiva de RF ambiente.** Es un **radar activo de penetración de paredes** (through-wall imaging radar), para inspección industrial/residencial a pedido, con salida en mapa de realidad aumentada de lo que hay dentro de una pared.

### Arquitectura conceptual
- **TX simple, boresight fijo** — sin steering electrónico en transmisión. El apuntado grueso lo resuelve el pan/tilt mecánico existente.
- **RX array con beamforming digital** — resuelve dirección angular electrónicamente por diferencia de fase entre canales, sin necesitar barrido mecánico fino. Esto es lo que permite construir el mapa (un TX/RX único solo da distancia, no dirección).
- **Frecuencias:** emisión en la frecuencia más alta con el array espaciado a λ/2 de esa frecuencia (evita grating lobes), más subarmónicas descendentes (freq/2, freq/4, freq/8) para modular la profundidad de penetración — a menor frecuencia el array se vuelve "eléctricamente más chico" (d/λ decrece), ensanchando el haz sin introducir aliasing espacial.
- **Técnica de forma de onda: FMCW** (Frequency Modulated Continuous Wave) — chirp de frecuencia creciente, la distancia se obtiene de la beat-frequency entre TX y eco recibido. Más simple/barato de implementar que radar de pulso.

### Cadena de front-end — pendiente, con un descarte importante
- **Downconversion RF antes del ADC** — sigue siendo el gap original sin resolver: se necesita LNA → mezclador/detector → filtro anti-aliasing antes de digitalizar, porque ningún ADC de bajo costo muestrea directamente a 5-10GHz.
- **Se evaluó y se descartó la familia TI AFE58xx (AFE5809/AFE5816)** como front-end multicanal — son chips diseñados para **ultrasonido** (rango de MHz), no para RF de gigahercios; requerirían de todos modos la etapa de downconversion previa que ya era el gap pendiente, y no la resuelven. Costo estimado de un diseño discreto propio con AFE58xx + downconversion + PCB multicapa (BGA de 289 pines): ~USD 800-1500+, sin contar el riesgo de diseño de RF a gigahercios desde cero.

### Camino recomendado — SDR
- **Prototipo inicial: 1x ADALM-PLUTO** (~USD 100-150) — validar FMCW básico (medir distancia por beat-frequency) antes de cualquier inversión mayor.
- **Escalado a array:** 2x PlutoSDR sincronizados, o 1x LimeSDR (2x2 MIMO nativo, ~USD 250-400) para el primer experimento real de beamforming (diferencia de fase entre 2 canales).
- **Sistema completo de referencia: ADALM-PHASER** (Analog Devices, ~USD 2800) — kit open source que integra 8 RX + 2 TX + downconversion + LO synthesizer + chip beamformer (ADAR1000) + array de antenas parche, 10-11GHz, chirps FMCW de 500MHz de ancho de banda. Resuelve de fábrica todo lo que un diseño discreto (AFE58xx + RF propio) tendría que resolver desde cero.

### Referencias / proyectos open reusables (a explorar, no evaluados en profundidad todavía)
- Radar TW MIMO 4x4 a 2.4GHz — array virtual de 16 elementos combinando 4 TX × 4 RX, con de-ramping FMCW para digitalizar a tasas bajas.
- GNU Radio + USRP — implementaciones de radar FMCW funcionando en tiempo real, sobre SDR.
- Diseños de radar FMCW low-cost basados en microcontrolador/ADC tipo Arduino.
- Paper de imaging a través de paredes con estimación 3D rango-ángulo-Doppler (estructura shift-invariant) — reduce elementos de antena necesarios.
- RPCA (Robust PCA) con estructura Kronecker — separación de clutter de pared vs. objetos reales detrás.

### Sin definir
- **Form factor del subsistema RF** — confirmado que **no** va en el volumen 40x40x40cm de Precision Part. Sin definir si integra a la Isla Giratoria original o es un dispositivo/proyecto separado.
- Cantidad final de elementos RX del array (define resolución angular del mapa).

## Gaps menores pendientes

1. Interfaz del LiDAR TFmini Plus — UART vs. I2C, sin fijar (evitar conflicto con el UART ya usado entre WROOM↔S3).
2. Ubicación física de cada MCU respecto a Lado A/Lado B — probablemente WROOM cerca del bloque RF (Lado B) y S3 cerca del bloque óptico (Lado A), pero no está formalizado.

## Historial de decisiones revertidas

- ~~Slip ring de 12 contactos~~ → eliminado, nodo autónomo.
- ~~AS5048A/AS5600 (encoder magnético absoluto)~~ → descartado por conflicto con eje hueco (paso de cables) → 3 home switches ópticos + conteo de pasos.
- ~~2 home switches~~ → 3 (2 no permite arbitraje de fallo, con 3 sí por mayoría).
- ~~2x 18650~~ → 2x 21700 (mejor autonomía a igual cantidad de celdas).
- ~~9V litio~~ → descartado (autonomía real insuficiente, no recargable).
- ~~AFE5809/AFE5816 (TI, ultrasonido)~~ → descartado como front-end RF, se va por SDR (Pluto/LimeSDR/Phaser).
