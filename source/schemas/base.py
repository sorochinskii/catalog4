from pydantic import BaseModel, Field, create_model


class OptionalFieldsMixin:
    @classmethod
    def optional_fields(cls) -> type[BaseModel]:
        fields = {
            name: (info.annotation | None, Field(default=None))
            for name, info in cls.model_fields.items()
        }
        name = f"Optional{cls.__name__}"
        model = create_model(name, __base__=cls, **fields)
        return model


class BaseSchema(BaseModel, OptionalFieldsMixin):
    ...
