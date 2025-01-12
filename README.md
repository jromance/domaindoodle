# domaindoodle
Domain Doodle es un proyecto que voy realizando en mis ratos libres para investigar un dominio. Actualmente se puede recopilar los registros dns y a través de scrapping certificados asociados a un dominio desde la web https://crt.sh/
Ejecución

El programa principal es main.py, que soporta los siguientes argumentos de línea de comandos.

python main.py [--certificate <dominio>] [--dnsinfo <dominio1,dominio2,...>] [--format <formato>] [--outfile <prefijo>]

Opciones principales
1. Buscar certificados en crt.sh

python main.py --certificate <dominio> [--format <formato>] [--outfile <prefijo>]

    <dominio>: Dominio para buscar certificados (ej. example.com).
    --format: Opcional. Formato de exportación (json, csv, xlsx).
    --outfile: Opcional. Prefijo para el archivo exportado (por defecto: output).

Ejemplo:

python main.py --certificate example.com --format json --outfile certificados

Salida:

    Exportará un archivo certificados.json con los datos de los certificados del dominio example.com.

2. Obtener registros DNS

python main.py --dnsinfo <dominio1,dominio2,...> [--format <formato>] [--outfile <prefijo>]

    <dominio1,dominio2,...>: Lista de dominios separados por comas.
    --format: Opcional. Formato de exportación (json, csv, xlsx).
    --outfile: Opcional. Prefijo para el archivo exportado (por defecto: output).

Ejemplo:

python main.py --dnsinfo example.com,google.com --format csv --outfile dnsinfo

Salida:

    Exportará un archivo dnsinfo.csv con la información DNS de los dominios example.com y google.com.
4. Consulta completa con dominio base (example.es):

python main.py --allinfo example.es --format xlsx --outfile full_report
3. Mostrar ayuda

python main.py --help