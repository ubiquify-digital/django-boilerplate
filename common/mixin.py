import re


# Convert from camelCase to snake_case
def camel_to_snake(name: str) -> str:
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)  # camelCase → camel_Case
    name = re.sub(r"([a-zA-Z])([0-9])", r"\1_\2", name)  # word+digit → word_digit
    name = re.sub(r"([0-9])([a-zA-Z])", r"\1_\2", name)  # digit+word → digit_word
    return name.lower()


# Convert from snake_case to camelCase
def snake_to_camel(name):
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_case_response(func):
    def inner_func(*args, **kwargs):
        response = func(*args, **kwargs)
        response.data["data"] = {
            snake_to_camel(key): value for key, value in response.data["data"].items()
        }
        return response

    return inner_func


class CamelSnakeMixin:
    """
    Mixin to handle conversion of camelCase to snake_case and vice versa
    during serialization and deserialization in DRF serializers.
    """

    def to_internal_value(self, data):
        """
        Convert the incoming data from camelCase to snake_case before deserializing.
        """
        # Convert keys from camelCase to snake_case
        if isinstance(data, dict):
            data = {camel_to_snake(k): v for k, v in data.items()}

        return super().to_internal_value(data)

    def to_representation(self, instance):
        """
        Convert the outgoing data from snake_case to camelCase before serializing.
        """
        # Get the base representation
        representation = super().to_representation(instance)

        # For ModelSerializer, representation is already a dict
        # For Serializer, we need to handle the case where instance might be a dict
        if not isinstance(representation, dict):
            if isinstance(instance, dict):
                representation = instance
            else:
                # If instance is not a dict, convert it to a dict using the serializer fields
                representation = {}
                for field_name, field in self.fields.items():
                    if field.source:
                        value = getattr(instance, field.source, None)
                    else:
                        value = getattr(instance, field_name, None)
                    representation[field_name] = value

        # Convert keys from snake_case to camelCase
        if isinstance(representation, dict):
            representation = {snake_to_camel(k): v for k, v in representation.items()}

        return representation

    def _convert_error_keys(self, errors):
        """
        Convert error keys from snake_case to camelCase.
        """
        if isinstance(errors, dict):
            converted_errors = {}
            for key, value in errors.items():
                camel_key = snake_to_camel(key)
                if isinstance(value, dict):
                    converted_errors[camel_key] = self._convert_error_keys(value)
                elif isinstance(value, list):
                    converted_errors[camel_key] = [
                        (
                            self._convert_error_keys(item)
                            if isinstance(item, dict)
                            else item
                        )
                        for item in value
                    ]
                else:
                    converted_errors[camel_key] = value
            return converted_errors
        return errors

    @property
    def errors(self):
        """
        Override the errors property to convert keys to camelCase.
        """
        errors = super().errors
        return self._convert_error_keys(errors)

    def is_valid(self, raise_exception=False):
        """
        Override is_valid to convert error keys to camelCase.
        """
        is_valid = super().is_valid(raise_exception=raise_exception)

        if not is_valid and hasattr(self, "_errors"):
            self._errors = self._convert_error_keys(self._errors)

        return is_valid
