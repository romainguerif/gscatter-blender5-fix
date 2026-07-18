import bpy


def get_input_from_identifier(inputs: bpy.types.NodeInputs, identifier: str):
    for input in inputs:
        if input.identifier == identifier:
            return input


def get_output_from_identifier(outputs: bpy.types.NodeOutputs, identifier: str):
    for output in outputs:
        if output.identifier == identifier:
            return output
