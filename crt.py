import requests
from bs4 import BeautifulSoup
import json
import csv
import re
from datetime import datetime


class CrtShScraper:
    """
    Clase para obtener certificados de https://crt.sh/ asociados a un dominio
    y trabajar con los resultados (exportar a JSON/CSV, filtrar, etc.).
    Además, procesa los valores 'Common Name' y 'Matching Identities' para
    separar dominios que aparecen pegados sin un delimitador claro.
    """

    def __init__(self, domain_info: str):
        self.domain_info = domain_info
        # Lista de diccionarios con la info de los certificados
        self.certificates_info = []

        # Regex para encontrar dominios en un string
        self.domain_pattern = re.compile(
            r"\b((?:[A-Za-z0-9-]+\.)+[A-Za-z0-9-]+)\b"
        )

    def insert_separator_aragon_es(self, text: str) -> str:
        """
        Inserta un espacio tras cada 'aragon.es' (o 'aragon.es' seguido de subdominios)
        cuando NO hay ya un delimitador. Así evitamos que se pegue con el siguiente dominio.

        Ejemplo:
          'cmeetingserver01.aragon.escmeetingserver02.aragon.es'
        se convierte en
          'cmeetingserver01.aragon.es cmeetingserver02.aragon.es'
        """
        # Si deseas que esto actúe también sobre *.salud.aragon.es u otros sub-subdominios,
        # puedes ajustar la regex. Por ejemplo, para 'aragon.es' exacto:
        pattern = re.compile(r'(aragon\.es)([A-Za-z0-9])')
        return pattern.sub(r'\1 \2', text)

    def get_domain_crt(self, domain_info: str) -> list[dict]:
        """
        Petición GET a crt.sh para el dominio recibido,
        parsea el HTML y devuelve una lista de diccionarios con la info de cada certificado.
        Además, reescribe 'Common Name' y 'Matching Identities' para que sean
        listas de dominios correctamente separados.
        """
        url = f"https://crt.sh/?q={domain_info}&exclude=expired"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data from crt.sh: Status Code {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        main_table = soup.find('th', string='Certificates')
        if not main_table:
            print("No se encontró la cabecera 'Certificates' en la página.")
            return []

        main_table = main_table.find_parent('table')
        if not main_table:
            print("No se encontró la tabla principal que contiene 'Certificates'.")
            return []

        data_table = main_table.find('table')
        if not data_table:
            print("No se encontró la tabla de datos dentro de la tabla principal.")
            return []

        certificates_info = []
        headers = [th.get_text(strip=True) for th in data_table.find_all('th')]
        rows = data_table.find_all('tr')[1:]  # saltar la fila de cabecera

        for row in rows:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                certificate = {
                    headers[i]: cells[i].get_text(strip=True)
                    for i in range(len(cells))
                }

                # Renombrar "Logged At⇧" a "Logged At" (opcional)
                if "Logged At⇧" in certificate:
                    certificate["Logged At"] = certificate.pop("Logged At⇧")

                # ==============================================================
                # PROCESAR 'Common Name':
                # 1) Insertar espacio tras 'aragon.es' si está pegado a lo siguiente
                # 2) Usar la regex para extraer dominios
                cn_raw = certificate.get("Common Name", "")
                cn_cleaned = self.insert_separator_aragon_es(cn_raw)
                cn_list = self.domain_pattern.findall(cn_cleaned)
                # Si no hay nada, dejamos una lista vacía; si hay dominios, los guardamos.
                certificate["Common Name"] = cn_list

                # ==============================================================
                # PROCESAR 'Matching Identities':
                mi_raw = certificate.get("Matching Identities", "")
                mi_cleaned = self.insert_separator_aragon_es(mi_raw)
                mi_list = self.domain_pattern.findall(mi_cleaned)
                certificate["Matching Identities"] = mi_list

                certificates_info.append(certificate)

        return certificates_info

    def get_domain_names(self) -> list[str]:
        """
        Retorna una lista con TODOS los dominios
        encontrados en Common Name y Matching Identities,
        sin duplicados, de todos los certificados en self.certificates_info.
        Asumiendo que 'Common Name' y 'Matching Identities'
        son listas de strings (si hiciste ese procesamiento en get_domain_crt).
        """
        domain_names = set()

        for cert in self.certificates_info:
            # Si Common Name es una lista
            cn = cert.get("Common Name", [])
            if isinstance(cn, list):
                for dom in cn:
                    domain_names.add(dom)
            elif isinstance(cn, str):
                # En caso de que siga siendo un string
                domain_names.add(cn)

            # Si Matching Identities es una lista
            mi = cert.get("Matching Identities", [])
            if isinstance(mi, list):
                for dom in mi:
                    domain_names.add(dom)
            elif isinstance(mi, str):
                domain_names.add(mi)

        return sorted(domain_names)

    def fetch_certificates(self) -> None:
        """
        Llama a get_domain_crt() con self.domain_info
        y guarda el resultado en self.certificates_info.
        """
        self.certificates_info = self.get_domain_crt(self.domain_info)

    def get_certificates(self) -> list[dict]:
        """Devuelve la lista completa de certificados parseados."""
        return self.certificates_info

    def filter_valid_certificates(self) -> list[dict]:
        """
        Retorna solo los certificados aún válidos (compara 'Not After' con la fecha actual).
        """
        valid = []
        today = datetime.now().date()
        for cert in self.certificates_info:
            not_after_str = cert.get("Not After")
            if not_after_str:
                try:
                    not_after_date = datetime.strptime(not_after_str, "%Y-%m-%d").date()
                    if not_after_date >= today:
                        valid.append(cert)
                except ValueError:
                    # Si no coincide el formato o hay error parseando fecha, lo ignoramos
                    pass
        return valid

    def export_json(self, filepath: str) -> None:
        """
        Exporta self.certificates_info a un archivo JSON.
        """
        if not self.certificates_info:
            print("No hay certificados para exportar.")
            return

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.certificates_info, f, ensure_ascii=False, indent=4)

        print(f"Exportado a JSON en: {filepath}")

    def export_csv(self, filepath: str) -> None:
        """
        Exporta self.certificates_info a un archivo CSV.
        Nota: Como 'Common Name' y 'Matching Identities' son listas,
        podrías querer unirlas en un string (por ejemplo, con ',') antes de exportar.
        """
        if not self.certificates_info:
            print("No hay certificados para exportar.")
            return

        # Si quieres "aplanar" las listas en las columnas, conviértelas a string
        # antes de escribir CSV.
        flat_certs = []
        for cert in self.certificates_info:
            # Creamos una copia con conversiones a string
            cert_copy = dict(cert)
            if isinstance(cert_copy.get("Common Name"), list):
                cert_copy["Common Name"] = " ".join(cert_copy["Common Name"])
            if isinstance(cert_copy.get("Matching Identities"), list):
                cert_copy["Matching Identities"] = " ".join(cert_copy["Matching Identities"])
            flat_certs.append(cert_copy)

        fieldnames = list(flat_certs[0].keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_certs)

        print(f"Exportado a CSV en: {filepath}")


