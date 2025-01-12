#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import pandas as pd

from DnsInfo import get_dns_info
from crt import CrtShScraper


def export_data(data, export_format, filename_prefix):
    """
    Exporta 'data' en JSON, CSV o Excel, según 'export_format'.
    - data: lista o dict con los resultados.
    - export_format: 'json', 'csv' o 'xlsx'.
    - filename_prefix: prefijo para el nombre del archivo.
    """
    if isinstance(data, dict):
        data = [data]

    if not data:
        print("No hay datos para exportar.")
        return

    if export_format == "json":
        filename = f"{filename_prefix}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Exportado a {filename}")

    elif export_format == "csv":
        filename = f"{filename_prefix}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Exportado a {filename}")

    elif export_format == "xlsx":
        filename = f"{filename_prefix}.xlsx"
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Exportado a {filename}")

    else:
        print("Formato de exportación no reconocido. Opciones: json, csv, xlsx.")


def expand_dns_records(dns_data):
    """
    Expande los registros DNS en un formato tabular.

    Args:
        dns_data (list): Lista de diccionarios con información DNS.

    Returns:
        list: Lista expandida con un registro por fila.
    """
    expanded_rows = []
    for domain_data in dns_data:
        domain = domain_data["domain"]
        for record_type, records in domain_data.items():
            if record_type == "domain" or not records:
                continue
            try:
                for record in records:
                    expanded_row = {"domain": domain, "record_type": record_type, **record}
                    expanded_rows.append(expanded_row)
            except (TypeError, ValueError):
                expanded_rows.append({"domain": domain, "record_type": record_type, "value": records})
    return expanded_rows


def main():
    parser = argparse.ArgumentParser(
        description="Herramienta CLI para consultar información DNS y certificados (crt.sh)."
    )
    parser.add_argument(
        "-crt", "--certificate",
        help="Dominio para buscar certificados en crt.sh (un solo dominio)."
    )
    parser.add_argument(
        "-dns", "--dnsinfo",
        help="Uno o varios dominios (separados por comas) para info DNS."
    )
    parser.add_argument(
        "-all", "--allinfo",
        help="Realiza una búsqueda completa: encuentra dominios relacionados en crt.sh con un dominio base y consulta su información DNS.",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv", "xlsx"],
        help="Formato de exportación (json, csv, xlsx). Opcional."
    )
    parser.add_argument(
        "-o", "--outfile",
        default="output",
        help="Prefijo para el archivo de salida (default: 'output')."
    )

    args = parser.parse_args()

    if not args.certificate and not args.dnsinfo and not args.allinfo:
        parser.print_help()
        sys.exit(0)

    # ------------------------------------------------------------------------
    # OPCIÓN 1: CERTIFICADOS (crt.sh)
    # ------------------------------------------------------------------------
    if args.certificate:
        domain = args.certificate
        print(f"Buscando certificados para: {domain}")
        scraper = CrtShScraper(domain)
        scraper.fetch_certificates()
        certs = scraper.get_certificates()

        print(f"Se han obtenido {len(certs)} certificados para {domain}.")
        if args.format:
            export_data(certs, args.format, args.outfile)
        else:
            for c in certs[:3]:
                print(c)

    # ------------------------------------------------------------------------
    # OPCIÓN 2: DNS INFO
    # ------------------------------------------------------------------------
    if args.dnsinfo:
        domain_list = [d.strip() for d in args.dnsinfo.split(",") if d.strip()]
        results = []
        for dom in domain_list:
            print(f"\nObteniendo info DNS para: {dom}")
            data = get_dns_info(dom)
            results.append(data)
            print(data)

        # Expandir registros DNS antes de exportar
        expanded_results = expand_dns_records(results)
        if args.format:
            export_data(expanded_results, args.format, args.outfile)
        else:
            for row in expanded_results[:10]:
                print(row)

    # ------------------------------------------------------------------------
    # OPCIÓN 3: BÚSQUEDA COMPLETA (crt.sh + DNS INFO)
    # ------------------------------------------------------------------------
    if args.allinfo:
        domain_base = args.allinfo
        print(f"Buscando todos los dominios relacionados con: {domain_base}")

        # Buscar dominios relacionados en crt.sh
        scraper = CrtShScraper(domain_base)
        scraper.fetch_certificates()
        related_domains = scraper.get_domain_names()

        print(f"Se encontraron {len(related_domains)} dominios relacionados.")
        print("Iniciando consulta DNS para los dominios encontrados...")

        results = []
        for dom in related_domains:
            print(f"\nObteniendo info DNS para: {dom}")
            data = get_dns_info(dom)
            results.append(data)
            print(data)

        # Expandir registros DNS y exportar
        expanded_results = expand_dns_records(results)
        if args.format:
            export_data(expanded_results, args.format, args.outfile)
        else:
            for row in expanded_results[:10]:
                print(row)


if __name__ == "__main__":
    main()
