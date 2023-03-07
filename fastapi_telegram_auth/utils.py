import hashlib
import hmac

from .types import TelegramLoginData


def validate(data: TelegramLoginData, secret_key: str) -> bool:
    # http://127.0.0.1:8000/login?
    # id=70331533&
    # first_name=Kirill&
    # username=lifintsev&
    # photo_url=https%3A%2F%2Ft.me%2Fi%2Fuserpic%2F320%2FEn2e5GdTDTilWO0Oij--s31K8Gj0dVFXBCoVJaZdAAY.jpg&
    # auth_date=1678203054&
    # hash=3d9a9e16aa4d9a2b9faf6fdcf98ad45b5255c25a50b4fa1b92d13c6000be4248
    telegram_data = data.dict(
        exclude_unset=True,
        exclude_none=True,
        exclude_defaults=True
    )
    data_check_string = '\n'.join(sorted([
        f"{key}={value or 'null'}"
        for key, value in telegram_data.items()
        if key != 'hash' and value is not None
    ]))
    secret_key = hashlib.sha256(secret_key.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return data.hash == calculated_hash
