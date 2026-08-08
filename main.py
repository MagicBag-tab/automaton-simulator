import os
import sys
from postfix import infix_to_postfix
from tree import Tree
from simulator import TreeVisualizer

def procesar_expresiones(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        print(f"Error: no se encontró el archivo '{nombre_archivo}'")
        return

    with open(nombre_archivo, encoding='utf-8') as archivo:
        for linea in archivo:
            expresion = linea.strip()
            if not expresion:
                continue

            resultado = infix_to_postfix(expresion)
            print(f"Expresión: {expresion}")
            print(f"Postfix: {resultado}\n")

            tree = Tree(resultado)
            visualizer = TreeVisualizer(tree, expresion)
            visualizer.draw()


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else 'expresiones.txt'
    procesar_expresiones(ruta)


if __name__ == '__main__':
    main()
