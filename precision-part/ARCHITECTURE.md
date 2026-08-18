# Precision Part — Arquitectura

Escáner de precisión para piezas, turntable + fotogrametría multi-cámara con triangulación láser dual-color como anclaje métrico. Volumen de trabajo objetivo: 40x40x40cm.

## Decisiones cerradas

### Mecánica y control
- **Turntable** (no carril lineal) — TMC2209 en modo control de posición angular, micropasos 1/256.
- **Stop-and-scan** (no rotación continua) — el turntable se detiene en cada posición angular, captura, avanza.
- **MCU único: ESP32-S3** — sin necesidad de dual-MCU como en Isla Giratoria; la carga de trabajo (stepper + 3 cámaras + 4 láseres) no genera la contención que sí justifica dual-MCU en el otro proyecto.

### Referencia angular / anti step-loss
- **1 sensor óptico fijo + 4 flags en el plato giratorio.**
- Flag en 0° (home): un solo flanco.
- Flags en 90°/180°/270°: doble flanco (patrón de pulso), distinguido por ventana de tiempo entre flancos.
- El firmware corrige el contador de pasos **en vivo** en cada checkpoint (no solo detecta error, lo corrige), acotando la deriva máxima a un cuarto de vuelta en vez de una vuelta completa.
- Umbral de tolerancia por definir — si el desvío en un checkpoint supera el umbral, se marca el segmento como no confiable en vez de abortar todo el escaneo.

### Cámaras
- **3x OV5640 (DVP)**, 5MP — reemplaza al IMX219 original (MIPI-CSI, incompatible nativo con ESP32/ESP32-S3).
- Dispuestas en **arco vertical (elevación)**, no en distintas alturas paralelas — cubren la pieza desde distintos ángulos de vista verticales.
- Lente: pendiente de revisión (módulo genérico vs. M12 intercambiable) — importa más para Precision Part que para Isla Giratoria por la precisión de triangulación requerida.

### Reconstrucción — reframe clave
- **Fotogrametría (multi-view stereo, 3 cámaras, flash RGB) es el método de reconstrucción principal.**
- **Láser triangulación es anclaje de precisión métrica**, no cobertura de superficie completa — corrige escala/drift de la reconstrucción fotogramétrica y cubre zonas sin textura donde fotogrametría falla.
- Pipeline de post-proceso (Fase III): (a) SfM + MVS densa por fotogrametría (ej. COLMAP), (b) puntos de precisión por triangulación láser, (c) fusión/alineación usando puntos láser como referencia de escala y corrección de drift.

### Emisores láser
- **4 emisores totales: 2 rojos (~650nm) + 2 azules (~450-480nm)** — se descartó verde por mayor crosstalk con rojo en el filtro Bayer del OV5640 comparado con rojo/azul (extremos del espectro, mejor separación); se descartó sumar un 3er color (RGB completo) por complejidad de separación y disponibilidad/costo de módulos azules de calidad.
- Cada color separado **22.5° de azimut a cada lado de la torre de cámaras** (45° de separación total entre rojo y azul).
- **Rotación de plano de línea: 45° entre colores** (uno ortogonal al eje de la torre, el otro en diagonal) — evita paralelismo entre líneas de distinto color, mejora cobertura de gradiente en zonas de geometría compleja.
- Montados a la altura de la cámara central del arco.
- Módulos comerciales (AliExpress) de **90-120° de abanico, alta potencia** — sin necesidad de cálculo custom de ángulo de abanico dado el volumen de trabajo (40cm) y el ancho de abanico ya generoso disponible en catálogo.
- **Regla de diseño:** al menos una línea de cada color debe estar apuntada para cruzar el centro geométrico del turntable, garantizando cobertura en piezas de radio chico.
- **Disparo: todos los emisores simultáneos** (no secuencial por color) — con solo 4 líneas totales el riesgo de crosstalk/ambigüedad es mucho menor que con una grilla densa, y se gana velocidad de escaneo. Separación de líneas en post-proceso por canal de color (Bayer) + posición angular esperada.
- Se descartó el uso de un DOE de grilla densa (patrón matriz completo) a favor de líneas paralelas simples — más control de espaciado, calibración más simple, menos ambigüedad de correspondencia.
- Se descartó agregar azul como tercer canal junto a rojo/verde (RGB completo) — azul reemplaza a verde, no se suma.

### Detección de tamaño de pieza / centrado (preview previo al escaneo)
- **ToF dedicado** (radial, apuntando al centro) — mide distancia perimetral en una vuelta rápida de preview.
  - Define el **paso angular adaptativo** según una cuerda objetivo configurable (fórmula: `θ = 2·arcsin(cuerda/(2·r))`).
  - Detecta **descentrado** de la pieza (variación senoidal de distancia durante la vuelta) — y con qué fase/ángulo, indicando la dirección del desplazamiento.
- **Estimación de altura por cámara** (silueta/contorno, cámara central) — corre en paralelo al preview del ToF, define qué cámaras del arco participan del escaneo real (evita capturas inútiles si la pieza es más baja que el rango cubierto por el arco completo).
- Pendiente: algoritmo de estimación de altura (umbral simple de contraste vs. subproducto del pipeline de fotogrametría — este último no serviría para decidir *antes* del escaneo real, solo después).

## Gaps pendientes

1. **Calibración de planos láser (12 combinaciones: 4 emisores × 3 cámaras).**
   - Método: gauge block escalonado (a fabricar o comprar) + detección de línea (umbral adaptativo + centroide sub-píxel) + retroproyección (`X = Z·(u-cx)/fx`, etc.) + fit de plano por mínimos cuadrados (SVD).
   - Protocolo de captura definido: ~8-12 posiciones angulares del turntable × 2-3 posiciones radiales del gauge block, por cada uno de los 4 emisores (las 3 cámaras capturan simultáneamente en cada disparo, reduciendo el trabajo real a 4 secuencias de barrido, no 12).
   - Sin ejecutar todavía — falta el gauge block físico y el script de calibración.

2. **Umbral de tolerancia de descentrado** — sin definir valor numérico.

3. **Ancho/perfil de línea láser en función de distancia** — relevante tanto para la calibración de plano como para el cálculo de cobertura por paso angular; depende de las specs reales del módulo que se termine comprando.

4. **Lente de las cámaras OV5640** — confirmar FOV/distorsión una vez elegido el módulo específico.

## Estimaciones de tiempo (referencia)

Por paso (posición angular), secuencia: movimiento turntable → settling → captura RGB con flash → captura láser (todos simultáneos, un solo disparo tras el cambio a disparo combinado):

- Optimista: ~130ms/paso (versión con disparo secuencial rojo/verde, ya obsoleta tras pasar a disparo simultáneo — recalcular)
- Conservador: ~370ms/paso (ídem, base de referencia a ajustar)

Con paso fijo de 1° (peor caso, pieza llenando el turntable de 0.4m Ø): cuerda de ~3.49mm entre posiciones — **se resuelve con paso angular adaptativo vía ToF**, no con paso fijo.

## Historial de decisiones revertidas

- ~~Grilla DOE completa por color~~ → 2 líneas paralelas simples por color.
- ~~RGB (3 colores)~~ → rojo/azul (2 colores).
- ~~Disparo secuencial por color~~ → disparo simultáneo.
- ~~Sistema de tilt de cámara única~~ → se mantienen 3 cámaras fijas en arco.
- ~~Damero simple para calibración de plano láser~~ → gauge block escalonado (necesario para tener variación de Z conocida).
