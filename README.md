# Visualizador de árboles sintácticos (automaton-simulator)

Este repositorio contiene la solución del laboratorio organizada por ramas (cada branch corresponde a la solución de un ejercicio). Incluye una aplicación que convierte expresiones regulares de notación infix a postfix (con animación) y construye el árbol sintáctico resultante.

Video de demostración del ejercicio 1:
https://youtu.be/G1JCtFw-vEM

Resumen de los problemas

- **Problema 1 (75%)**
	- Implementar la construcción del árbol sintáctico a partir de la conversión infix → postfix (Shunting Yard ya implementado en laboratorio previo).
	- Requisitos principales:
		- Crear objetos para almacenar la información de cada nodo del árbol sintáctico.
		- Utilizar una librería para dibujar el árbol en pantalla (esta implementación usa `pygame`).
		- Aplicar la simplificación para las extensiones `+` y `?` (se expanden internamente antes de construir el árbol).
		- Mostrar la ejecución completa: conversión infix → postfix (animada) y construcción del árbol.
		- El programa lee `expresiones.txt` y procesa cada línea. Expresiones de prueba incluidas:
			1. `(a* | b*)+`
			2. `((ε | a) | b*)*`
			3. `(a | b)* abb (a | b)*`
			4. `0? (1?)? 0*`

- **Problema 2 (25%)**
	- Utilizar el Lema de Arden para encontrar la expresión regular equivalente a un autómata dado y documentar todo el procedimiento.

Uso rápido

1. Recomendado: Python 3.11 o 3.12 (algunas ruedas precompiladas de `pygame` en Windows funcionan mejor con estas versiones).
2. (Opcional) Instalar dependencias de la GUI:

```bash
python -m pip install pygame
```

3. Ejecutar la aplicación principal:

```bash
python main.py
```

Puntos técnicos

- La aplicación muestra la versión simplificada de `INFIX` (con `+` y `?` ya expandidas) y mantiene la animación del proceso de conversión en la fila `POSTFIX`. El árbol se construye a partir del postfix simplificado.
- Archivos clave:
	- `main.py` — punto de entrada
	- `visualizer.py` — interfaz gráfica y dibujo
	- `postfix.py` — tokenización, conversión y funciones de expansión/simplificación
	- `syntax_tree.py` — construcción del árbol y snapshots de pasos

Si quieres que añada capturas de pantalla, pasos detallados de instalación para Windows, o que integre el enlace del video en la web del repo, dímelo y lo agrego.