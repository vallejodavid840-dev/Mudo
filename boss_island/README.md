# Isla de Jefes

Prototipo original de run & gun (mecanica estilo "correr, disparar, esquivar
jefes con patrones") con hub de isla para elegir jefe, hasta 4 jugadores
locales, y dos jefes originales (Rey Rana y Espina). No usa ningun personaje,
sprite ni arte de ningun juego existente — todo es original y dibujado con
formas simples.

## Cómo correrlo (PC/Mac/Linux)

```bash
pip install -r requirements.txt
python3 main.py          # detecta mandos conectados automaticamente
python3 main.py 4        # fuerza 4 jugadores (usa teclado si no hay 4 mandos)
```

### Controles (sin mando)

| Jugador | Mover | Saltar | Disparar | Dash | Apuntar arriba/abajo |
|---|---|---|---|---|---|
| P1 | A / D | W | F | Shift izq | Flecha arriba/abajo |
| P2 | Flechas | Flecha arriba | Enter | Shift der | RePág/AvPág |
| P3 | J / L | I | K | O | U / M |
| P4 | Num 4/6 | Num 8 | Num 5 | Num + | Num 7/1 |

Con mando (joystick) conectado, se usa el stick izquierdo y los botones 0/1/2
(salto/dash/disparo) automáticamente, en el orden en que Windows/Linux los
detecte.

## Estado real: verificado, no inventado

Corrí una simulación automática sin pantalla (`smoke_test.py`) que confirma:
movimiento de los 4 jugadores, colisión de balas contra el jefe, muerte del
jefe al agotar su vida, y 600 fotogramas de combate sin excepciones. Ejecútalo
tú mismo para comprobarlo:

```bash
SDL_VIDEODRIVER=dummy python3 smoke_test.py
```

## Sobre el PKG de PS3 (la parte pendiente y honesta)

Esto **todavía no es un PKG de PS3**. Para llegar ahí falta un tramo real que
no puedo completar solo desde este entorno:

- Este código está en Python/pygame para poder escribirlo, correrlo y
  probarlo aquí mismo hoy. PS3 (vía PSL1GHT/homebrew) necesita C, con sus
  propias APIs de video (RSX) y mando — es un puerto, no una traducción
  automática.
- No tengo un PS3 para probar el resultado, ni el toolchain de PS3 instalado
  en este entorno (lo comprobé: no está, y el repo estándar de instalación
  me dio bloqueado al intentar bajarlo).
- El camino real: tú instalas el toolchain PSL1GHT en tu PC, y vamos
  adaptando este juego a C/PSL1GHT módulo por módulo (jugador, jefes, hub),
  compilando y probando en tu consola real en cada paso, hasta empaquetar el
  PKG final.

Este repo es la base jugable y verificada para arrancar ese puerto cuando
quieras seguir.
