from typing import Union

from pydantic import BaseModel, Field


class IP4(BaseModel):
    ip: Union[str, None] = Field(alias='ipv4_addr', default=None)
    mask: Union[str, None] = Field(alias='ipv4_mask', default=None)
    broadcast: Union[str, None] = Field(alias='ipv4_bcast', default=None)


class IP6(BaseModel):
    ip: Union[str, None] = Field(alias='ipv6_addr', default=None)
    mask: Union[str, None] = Field(alias='ipv6_mask', default=None)
    scope: Union[str, None] = Field(alias='pv6_scope', default=None)


class RX(BaseModel):
    packets: Union[str, None] = Field(alias='rx_packets', default=None)
    errors: Union[str, None] = Field(alias='rx_errors', default=None)
    dropped: Union[str, None] = Field(alias='rx_dropped', default=None)
    overruns: Union[str, None] = Field(alias='rx_overruns', default=None)
    frame: Union[str, None] = Field(alias='rx_frame', default=None)
    bytes: Union[str, None] = Field(alias='rx_bytes', default=None)


class TX(BaseModel):
    packets: Union[str, None] = Field(alias='tx_packets', default=None)
    errors: Union[str, None] = Field(alias='tx_errors', default=None)
    dropped: Union[str, None] = Field(alias='tx_dropped', default=None)
    overruns: Union[str, None] = Field(alias='tx_overruns', default=None)
    carrier: Union[str, None] = Field(alias='tx_carrier', default=None)
    collisions: Union[str, None] = Field(alias='tx_collisions', default=None)
    bytes: Union[str, None] = Field(alias='tx_bytes', default=None)


class Ifmodel(BaseModel):

    name: str
    flags: int
    state: Union[list, None]
    mtu: int
    ip4: IP4 = Field(alias='ip4', default=None)
    ip6: IP6 = Field(alias='ip6', default=None)
    type: Union[str, None]
    mac: str = Field(alias='mac_addr', default=None)
    metric: Union[str, None]
    tx: TX
    rx: RX
