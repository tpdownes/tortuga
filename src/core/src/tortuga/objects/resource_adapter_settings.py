import os.path

from .schemas import resource_adapter_settings as schemas


SETTING_TYPES = {}


class SettingNotFoundError(Exception):
    pass


def get_setting_class(type_):
    """
    Gets the setting class for a specified type name.

    :param str type_:             the type name of the setting
    :return:                      the class for the requested type
    :raises SettingNotFoundError: if the setting class is not found

    """
    try:
        return SETTING_TYPES[type_]
    except KeyError:
        raise SettingNotFoundError()


class SettingValidationError(Exception):
    pass


class SettingMeta(type):
    """
    Metaclass for resource adapter settings.

    The purpose of this metaclass is to register settings in a so that they
    can easily be looked-up by type.

    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'BaseSetting':
            return

        SETTING_TYPES[cls.type] = cls


class BaseSetting(metaclass=SettingMeta):
    """
    A resoruce adapter configuration variable.

    """
    type = None
    schema = None

    def __init__(self, **kwargs):
        self.description = kwargs.get('description', '')
        self.required = kwargs.get('required', False)
        self.secret = kwargs.get('secret', False)
        self.values = kwargs.get('values', [])
        self.mutually_exclusive = kwargs.get('mutually_exclusive', [])

    def validate(self, value):
        """
        Validates the value against the validation rules for this
        variable.

        :raises SettingValidationError: if the value is not valid, the
                                        exception message will indicate the
                                        problem.

        """
        if not self.type:
            raise Exception('Setting type not set')
        self.validate_values()

    def validate_values(self, value):
        """
        Validates whether or not the value is one of the required values.
        If values is an empty list, then any value is valid.

        :raises SettingValidationError: if the value is not one of the
                                        required values.

        """
        if self.values and value not in self.values:
            raise SettingValidationError(
                'Value must be one of: {}'.format(self.values))


class BooleanSetting(BaseSetting):
    type = 'boolean'
    schema = schemas.BooleanSettingSchema

    def validate(self, value):
        if not isinstance(value, bool):
            raise SettingValidationError('Value must be an boolean')
        super().validate(value)


class FileSetting(BaseSetting):
    type = 'file'
    schema = schemas.FileSettingSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.must_exist = kwargs.get('must_exist', True)

    def validate(self, value):
        if not isinstance(value, str):
            raise SettingValidationError('File name must be a string')
        super().validate(value)
        if self.must_exist and not os.path.exists(value):
            raise SettingValidationError('File does not exist')


class IntegerSetting(BaseSetting):
    type = 'integer'
    schema = schemas.IntegerSettingSchema

    def validate(self, value):
        if not isinstance(value, int):
            raise SettingValidationError('Value must be a integer')
        super().validate(value)


class StringSetting(BaseSetting):
    type = 'string'
    schema = schemas.StringSettingSchema

    def validate(self, value):
        if not isinstance(value, str):
            raise SettingValidationError('Value must be a string')
        super().validate(value)