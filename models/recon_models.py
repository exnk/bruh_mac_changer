from pydantic import BaseModel, Field


class Subdomain(BaseModel):
    url: str = Field(default=None)
    ip: str = Field(default=None)
    tech: None | dict = Field(default=None)


class Cert(BaseModel):
    id: str = Field(default=None)
    tbs_sha256: str = Field(default=None)
    dns_names: list = Field(default=[])
    pubkey_sha256: str = Field(default=None)


class Address(BaseModel):
    address: str = Field(default=None)
    ttl: int = Field(default=None)


class MX(BaseModel):
    exchange: str = Field(default=None)
    priority: str | int = Field(default=None)


class Host(BaseModel):
    url: str = Field(default=None)
    tech: None | dict = Field(default=None)
    subdomains: list[Subdomain] = Field(default=[])
    A: list[Address] = Field(default=[])
    mx: list[MX] = Field(default=[])
    NS: list = Field(default=[])
    dns: str = Field(default=None)
    reverse_dns: str = Field(default=None)
    certs: list[Cert] = Field(default=[])
