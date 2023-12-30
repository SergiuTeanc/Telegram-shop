from yoomoney import Quickpay, Client
import random
from bot.misc import EnvKeys


def quick_pay(message):
    bill = Quickpay(
        receiver=EnvKeys.RECEIVER_TOKEN,
        quickpay_form="shop",
        targets="Sponsor",
        paymentType="SB",
        sum=message.text,
        label=str(message.from_user.id) + '_' + str(random.randint(1000000000, 9999999999))
    )
    label = bill.label
    url = bill.base_url
    return label, url


async def check_payment_status(label: str):
    client = Client(EnvKeys.CLIENT_TOKEN)
    history = client.operation_history(label=label)
    for operation in history.operations:
        return operation.status
