from enum import Enum


class RecordType(Enum):
    A = "A"
    AAAA = "AAAA"
    SOA = "SOA"
    MX = "MX"
    TXT = "TXT"
    CNAME = "CNAME"
    NS = "NS"
    DLV = "DLV"
    DNSKEY = "DNSKEY"
    HINFO = "HINFO"
    # RDSI = "RDSI"
    LOC = "LOC"
    MG = "MG"
    MINFO = "MINFO"
    MR = "MR"
    NSEC = "NSEC"
    NSEC3 = "NSEC3"
    NSEC3PARAM = "NSEC3PARAM"
    NSAP = "NSAP"
    KEY = "KEY"
    RP = "RP"
    PTR = "PTR"
    RRSIG = "RRSIG"
    RT = "RT"
    SRV = "SRV"
    WKS = "WKS"
    PX = "PX"
    X25 = "X25"