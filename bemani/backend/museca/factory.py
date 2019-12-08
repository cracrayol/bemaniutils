from typing import Any, Dict, List, Optional, Type

from bemani.backend.base import Base, Factory
from bemani.backend.museca.museca1 import Museca1
from bemani.backend.museca.museca1plus import Museca1Plus
from bemani.common import Model, VersionConstants
from bemani.data import Data


class MusecaFactory(Factory):

    MANAGED_CLASSES: List[Type[Base]] = [
        Museca1,
        Museca1Plus,
    ]

    @classmethod
    def register_all(cls) -> None:
        for game in ['PIX']:
            Base.register(game, MusecaFactory)

    @classmethod
    def create(cls, data: Data, config: Dict[str, Any], model: Model, parentmodel: Optional[Model]=None) -> Optional[Base]:

        def version_from_date(date: int) -> Optional[int]:
            if date <= 2016072600:
                return VersionConstants.MUSECA
            if date > 2016072600:
                return VersionConstants.MUSECA_1_PLUS
            return None

        if model.game == 'PIX':
            version = version_from_date(model.version)
            if version == VersionConstants.MUSECA:
                return Museca1(data, config, model)
            if version == VersionConstants.MUSECA_1_PLUS:
                return Museca1Plus(data, config, model)

        # Unknown game version
        return None
