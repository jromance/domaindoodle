import dns.resolver

from RecordType import RecordType


def get_dns_info(domain_name: str) -> dict:
    print("Obteniendo la información de DNS de " + domain_name + "...")
    records = {"domain": domain_name,
               "A": get_rdtype_register(domain_name, RecordType.A.value) or "",
               "AAAA": get_rdtype_register(domain_name, RecordType.AAAA.value) or "",
               "SOA": get_rdtype_register(domain_name, RecordType.SOA.value) or "",
               "MX": get_rdtype_register(domain_name, RecordType.MX.value) or "",
               "TXT": get_rdtype_register(domain_name, RecordType.TXT.value) or "",
               "CNAME": get_rdtype_register(domain_name, RecordType.CNAME.value) or "",
               "NS": get_rdtype_register(domain_name, RecordType.NS.value) or "",
               "DNSKEY": get_rdtype_register(domain_name, RecordType.DNSKEY.value) or "",
               "HINFO": get_rdtype_register(domain_name, RecordType.HINFO.value) or "",
               "LOC": get_rdtype_register(domain_name, RecordType.LOC.value) or "",
               "MG": get_rdtype_register(domain_name, RecordType.MG.value) or "",
               "MINFO": get_rdtype_register(domain_name, RecordType.MINFO.value) or "",
               "MR": get_rdtype_register(domain_name, RecordType.MR.value) or "",
               "NSEC": get_rdtype_register(domain_name, RecordType.NSEC.value) or "",
               "NSEC3": get_rdtype_register(domain_name, RecordType.NSEC.value) or "",
               "NSEC3PARAM": get_rdtype_register(domain_name, RecordType.NSEC3PARAM.value) or "",
               "NSAP": get_rdtype_register(domain_name, RecordType.NSAP.value) or "",
               "KEY": get_rdtype_register(domain_name, RecordType.KEY.value) or "",
               "RP": get_rdtype_register(domain_name, RecordType.RP.value) or "",
               "RRSIG": get_rdtype_register(domain_name, RecordType.RRSIG.value) or "",
               "RT": get_rdtype_register(domain_name, RecordType.RT.value) or "",
               "SRV": get_rdtype_register(domain_name, RecordType.SRV.value) or "",
               "WKS": get_rdtype_register(domain_name, RecordType.WKS.value) or "",
               "PX": get_rdtype_register(domain_name, RecordType.PX.value) or "",
               "X25": get_rdtype_register(domain_name, RecordType.X25.value) or "",
               }
    return records


def get_rdtype_register(domain_info: str, rdtype: str) -> list:
    records = []
    try:
        answer = dns.resolver.resolve(domain_info, rdtype)

        if rdtype == "MX":
            records = [{
                'domain': domain_info,
                'rdtype': rdtype,
                'preference': record.preference,
                'exchange': record.exchange.to_text()
            } for record in answer]

        elif rdtype == 'SOA':
            records = [{
                'domain': domain_info,
                'rdtype': rdtype,
                'mname': record.mname.to_text(),
                'rname': record.rname.to_text(),
                'serial': record.serial,
                'refresh': record.refresh,
                'retry': record.retry,
                'expire': record.expire,
                'minimum': record.minimum
            } for record in answer]

        else:
            # General handling for other record types
            records = [{
                'domain': domain_info,
                'rdtype': rdtype,
                'address': record.to_text()
            } for record in answer]

    except dns.resolver.NoAnswer:
        # No se encontró respuesta para este tipo de registro
        return []
    except dns.resolver.NXDOMAIN:
        # El dominio no existe
        return []
    except dns.exception.Timeout:
        # Timeout de la consulta
        return []
    except dns.exception.DNSException as e:
        # Cualquier otro error DNS
        return []

    return records
