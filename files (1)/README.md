# BrotIA

Asistente conversacional de huerta en casa pensado para Formosa y Chaco (Argentina). Incluye una capacitación
de cuatro clases con autoevaluación y emite un certificado en PDF a nombre de **BrotIA**.

> Estado: prototipo. `agente.py` (conversación con IA) no fue probado contra la API real.
> El calendario de siembra es nacional (ProHuerta) y debe validarse para el NEA.

## Qué hace
- `/capacitacion`: cuatro clases, autoevaluación de 8 preguntas (aprueba con 70%) y certificado.
- Certificado en PDF con nombre completo y DNI, tres firmantes, código de verificación y QR.
- Aviso de privacidad antes de pedir datos: la persona decide si los da. Si dice que no, puede hacer
  el curso pero no recibe certificado. Los datos no se guardan.
- Conversación sobre huerta con IA (opcional), apoyada en `datos/calendario_siembra.csv`.

## Interfaz web
```bash
flask --app web.app run
```
Abrí http://127.0.0.1:5000. Incluye el chat con el logo, la capacitación, la autoevaluación, el aviso de datos
y la descarga del certificado. El servidor no guarda estado: el historial del chat vive en el navegador y el PDF se
genera en memoria. Para producción usá un servidor WSGI (por ejemplo gunicorn) detrás de HTTPS.

Limitación conocida: la autoevaluación es auto-aplicada y las respuestas correctas viajan en el código, por lo que
una persona técnica podría saltearla llamando a la API. Si el certificado debe tener más valor, hay que tomar el
examen del lado del servidor con preguntas variables.

## Instalación
```bash
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # completá BROTIA_SECRET (y ANTHROPIC_API_KEY si querés la IA)
python -m brotia.cli
```
Pruebas: `python -m unittest discover tests`

Los recursos gráficos (logo y banner) están en `assets/`.

## Despliegue web
BrotIA va a funcionar en web. Al hacer la capa web: generar el PDF en memoria y entregarlo para descarga,
no registrar en logs los campos nombre y DNI, usar HTTPS y no guardar el PDF en el servidor.

## Firmas
Las imágenes de firma NO están en este repositorio (están en `.gitignore`). Copiá `amadey_alex.png`,
`aguilera_david.png` y `zabala_matias.png` en la carpeta `firmas/` del servidor. Sin ellas el certificado
se genera igual, con la línea de firma vacía.

## Pendientes antes de publicar
1. Confirmar nombres y títulos de los firmantes en `brotia/config.py`.
2. Confirmar que cada firmante autorizó el uso de su firma en los certificados.
3. Revisar el aviso de privacidad (`brotia/privacidad.py`) con una persona con conocimiento legal.
4. Completar las filas "Verificar" del calendario contra el PDF original y validar las épocas para Chaco y Formosa.
5. Elegir una licencia para el repositorio.
6. No subir nunca `.env` ni la clave `BROTIA_SECRET`: quien la tenga puede fabricar códigos válidos.

## Verificación de certificados
El código se calcula con HMAC a partir de nombre, DNI, fecha y curso. Quien verifica necesita esos datos y
la clave secreta; el código por sí solo no revela datos personales. Ver `brotia/certificado.py: verificar`.

## Estructura
```
brotia/        código (config, privacidad, certificado, capacitación, agente, cli)
web/           interfaz web (Flask)
assets/        logo, banner y estilos
datos/         calendario de siembra en CSV
docs/          fuentes consultadas
firmas/        imágenes de firma (ignoradas por git)
tests/         pruebas
```
