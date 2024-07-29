from shop_yoomoney import Quickpay, Authorize


async def create_pay(amount, label, token):
    quickpay = Quickpay(
        receiver=token[:token.find('.')],
        quickpay_form="button",
        targets="Покупка купона",
        paymentType="AC",
        sum=amount,
        label=label,
    )
    return quickpay.base_url


def auth():
    Authorize(
        client_id="572C10D5ED487343A09E20B097D5B1C4FBEC922334FB20B5E5F94E379037183C",
        client_secret='03FCE05049A21ACC05A4060F1DA0571AF31CE102B309DEC570854E6F32168E6F5510EB0C22F03C9FF78892524FECBE97CE566DE8A48B4879AA8039ACD28111E8',
        redirect_uri="https://ya.ru/",
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop",
               ])
