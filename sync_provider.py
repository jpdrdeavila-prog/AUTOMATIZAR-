"""Contrato isolado para integrações oficiais futuras com plataformas educacionais."""
from abc import ABC, abstractmethod

class SyncUnavailable(RuntimeError): pass

class SyncProvider(ABC):
    """Um provedor só deve ser implementado após autorização e documentação oficial."""
    @abstractmethod
    def fetch_tasks(self, authorized_user):
        raise NotImplementedError

class SalaDoFuturoProvider(SyncProvider):
    def fetch_tasks(self, authorized_user):
        raise SyncUnavailable("Não há método público oficial confirmado para esta integração.")
