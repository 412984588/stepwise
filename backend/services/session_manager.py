from dataclasses import dataclass
from datetime import datetime, timezone

from backend.models.enums import HintLayer, SessionStatus, UnderstandingLevel


LAYER_ORDER = [HintLayer.CONCEPT, HintLayer.STRATEGY, HintLayer.STEP]
CONFUSION_THRESHOLD = 3


@dataclass
class LayerTransition:
    new_layer: HintLayer
    should_advance: bool
    is_downgrade: bool
    reset_confusion: bool


class SessionManager:
    def determine_transition(
        self,
        current_layer: HintLayer,
        understanding_level: UnderstandingLevel,
        confusion_count: int,
    ) -> LayerTransition:
        if understanding_level == UnderstandingLevel.UNDERSTOOD:
            return self._handle_understood(current_layer)

        new_confusion = confusion_count + 1

        if new_confusion >= CONFUSION_THRESHOLD:
            return LayerTransition(
                new_layer=current_layer,
                should_advance=False,
                is_downgrade=True,
                reset_confusion=False,
            )

        return LayerTransition(
            new_layer=current_layer,
            should_advance=False,
            is_downgrade=False,
            reset_confusion=False,
        )

    def _handle_understood(self, current_layer: HintLayer) -> LayerTransition:
        if current_layer not in LAYER_ORDER:
            return LayerTransition(
                new_layer=current_layer,
                should_advance=False,
                is_downgrade=False,
                reset_confusion=True,
            )

        current_idx = LAYER_ORDER.index(current_layer)

        if current_idx < len(LAYER_ORDER) - 1:
            next_layer = LAYER_ORDER[current_idx + 1]
            return LayerTransition(
                new_layer=next_layer,
                should_advance=True,
                is_downgrade=False,
                reset_confusion=True,
            )

        return LayerTransition(
            new_layer=HintLayer.COMPLETED,
            should_advance=True,
            is_downgrade=False,
            reset_confusion=True,
        )

    def get_next_sequence(self, current_sequence: int, is_same_layer: bool) -> int:
        if is_same_layer:
            return current_sequence + 1
        return 1

    def can_reveal_solution(self, current_layer: HintLayer, status: SessionStatus) -> bool:
        if status in (SessionStatus.COMPLETED, SessionStatus.REVEALED):
            return True
        return current_layer == HintLayer.STEP

    def get_completed_layers(self, current_layer: HintLayer) -> list[str]:
        if current_layer not in LAYER_ORDER:
            if current_layer in (HintLayer.COMPLETED, HintLayer.REVEALED):
                return [layer.value.upper() for layer in LAYER_ORDER]
            return []

        current_idx = LAYER_ORDER.index(current_layer)
        return [LAYER_ORDER[i].value.upper() for i in range(current_idx)]
