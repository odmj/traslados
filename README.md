# Concurso de Traslados

Aplicación web desarrollada en Python y Streamlit para calcular distancias entre localidades y centros educativos, facilitando el análisis y ordenación de destinos en concursos de traslados.

## Aplicación

https://concursotraslados.streamlit.app/

## Funcionalidades

- Cálculo automático de distancias.
- Comparación de múltiples destinos.
- Interfaz sencilla orientada a personal docente.
- Consulta rápida desde navegador.

## Vídeo demostración

[![Ver vídeo](images/tutorial.JPG)](https://youtu.be/oFLQIy7hySQ)

## Arquitectura

Usuario

↓

Aplicación Streamlit

↓

Google Maps Distance Matrix API

↓

Resultados de distancia

## Tecnologías

- Python
- Streamlit
- Google Maps Distance Matrix API

## Estructura del proyecto

- `traslados.py` → interfaz principal de la aplicación y gestión de la interacción con el usuario.
- `core.py` → lógica de negocio, procesamiento de datos y consultas a Google Maps Distance Matrix API para el cálculo de distancias.

## Autor

Jorge Olleros
