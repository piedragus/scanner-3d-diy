"""Simula la medición de un cilindro descentrado con un ToF ruidoso, corrigiendo el descentrado por ajuste de círculo.
Pregunta: ¿cuántas pasadas N hacen falta para llegar a 0,25 mm de error en el diámetro? Uso: python3 sim_descentrado.py"""
import numpy as np

rng = np.random.default_rng(1)
R, PUNTOS, REPS = 40.0, 360, 200  # radio mm, muestras por vuelta, repeticiones Monte Carlo


def ajustar_circulo(x, y):
    A = np.c_[2 * x, 2 * y, np.ones_like(x)]
    b = x**2 + y**2
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    return cx, cy, np.sqrt(c + cx**2 + cy**2)


def medir(descentrado, sigma, n_pasadas):
    th = np.linspace(0, 2 * np.pi, PUNTOS, endpoint=False)
    cx0, cy0 = descentrado, 0.0
    diam = []
    for _ in range(n_pasadas):
        fase = rng.uniform(0, 2 * np.pi)
        t = th + fase
        x = cx0 + R * np.cos(t) + rng.normal(0, sigma, PUNTOS)
        y = cy0 + R * np.sin(t) + rng.normal(0, sigma, PUNTOS)
        diam.append(2 * ajustar_circulo(x, y)[2])
    return np.mean(diam)


print("sigma ToF (mm) | N pasadas | error rms del diametro (mm)  [descentrado 5 mm]")
for sigma in (0.3, 0.5, 1.0):
    for n in (1, 2, 4, 8, 16):
        e = [medir(5.0, sigma, n) - 2 * R for _ in range(REPS)]
        print(f"{sigma:14.1f} | {n:9d} | {np.sqrt(np.mean(np.square(e))):.3f}")
