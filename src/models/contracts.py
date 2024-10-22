from dataclasses import dataclass


@dataclass
class ERC20:
    abi: str = open('./assets/abi/erc20.json', 'r').read()


@dataclass
class ClaimContract:
    address: str = '0xE8bE8eB940c0ca3BD19D911CD3bEBc97Bea0ED62'
    abi: str = open('./assets/abi/claim_abi.json', 'r').read()


@dataclass
class ScrollContract:
    address: str = '0xd29687c813d741e2f938f4ac377128810e217b1b'
