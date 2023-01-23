from .trait_interpreter import TraitInterpreter


class NotchPropertyTraitInterpreter(TraitInterpreter):
    """
    Passthrough interpreter intended to work with NotchAssembler.

    Sample data that this interpreter expects  from config:
    {
        node: $F_Material1
        property: Material, Colour
        options:
          Red: 1, 0, 0, 1
          Green: 0, 1, 0, 1
          Blue: 0, 0, 1, 1
    }
    """
    def interpret(self, trait_value: str, feature_properties: dict) -> dict:
        return {
            'node': feature_properties['node'],
            'property': feature_properties['property'],
            'value': trait_value
        }
