from datetime import datetime, timezone
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.entities.code.models import QRCode
from src.entities.transaction.models import Transaction
from src.entities.user.models import User


class QRCodeService:
    @staticmethod
    async def generate_qr_codes(
        session: AsyncSession,
        value: int,
        quantity: int,
    ) -> list[QRCode]:
        """
        Generate new qr_codes
        """
        qr_codes = []
        for _ in range(quantity):
            qr_code = QRCode(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                redeemed=False,
                value=value,
                user_id=None,
                redeemed_at=None,
            )

            session.add(qr_code)
            qr_codes.append(qr_code)

        await session.commit()
        return qr_codes

    @staticmethod
    async def get_qr_code_by_id(session: AsyncSession, id: uuid.UUID) -> QRCode | None:
        """
        Get a qr_code by its code
        """
        statement = select(QRCode).where(QRCode.id == id)
        result = await session.exec(statement)
        return result.first()

    # @staticmethod
    # async def get_user_qr_codes(
    #     session: AsyncSession, user_id: uuid.UUID
    # ) -> Sequence[QRCode]:
    #     """
    #     Get all qr_codes for a user
    #     """
    #     statement = select(QRCode).where(QRCode.user_id == user_id)
    #     result = await session.exec(statement)
    #     return result.all()

    @staticmethod
    async def redeem_qr_code(
        session: AsyncSession, qr_code: QRCode, user: User
    ) -> QRCode | None:
        """
        Redeem a qr_code
        """
        qr_code.redeemed = True
        qr_code.redeemed_at = datetime.now()
        qr_code.user_id = user.id

        user.points += qr_code.value
        user.redeemed_code_count += 1

        transaction = Transaction(
            id=uuid.uuid4(),
            user_id=user.id,
            amount=qr_code.value,
            timestamp=datetime.now(timezone.utc),
        )
        session.add(transaction)
        await session.commit()
        await session.refresh(user)
        await session.refresh(qr_code)
        return qr_code
