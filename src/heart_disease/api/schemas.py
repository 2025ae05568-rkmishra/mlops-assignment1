from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator

Code = StrictInt
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    age: Annotated[StrictInt, Field(ge=1, le=120)]
    sex: Code
    cp: Code
    trestbps: Annotated[Number, Field(gt=0, le=350)]
    chol: Annotated[Number, Field(gt=0, le=1000)]
    fbs: Code
    restecg: Code
    thalach: Annotated[Number, Field(gt=0, le=300)]
    exang: Code
    oldpeak: Annotated[Number, Field(ge=-10, le=20)]
    slope: Code
    ca: Code | None
    thal: Code | None

    @field_validator("sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal")
    @classmethod
    def valid_category(cls, value, info):
        from heart_disease.features.schema import CATEGORIES

        if value is not None and value not in CATEGORIES[info.field_name]:
            raise ValueError("Unrecognized source category code")
        return value


class PredictionResponse(BaseModel):
    request_id: str
    prediction: Literal[0, 1]
    positive_class_probability: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    confidence: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    threshold: Annotated[float, Field(ge=0, le=1)]
    model_version: str
    schema_version: str


class ErrorResponse(BaseModel):
    error: str
    request_id: str
    fields: list[dict[str, str]] | None = None
