p_list = []


class Product:
    index = 1  # 처음 세팅 1

    def __init__(self, name, price, count):
        self.name = name    # 상품명
        self.price = price  # 가격
        self.count = count  # 재고
        self.in_cart = 0    # 장바구니에 담은 수량

        # 인덱스 세팅
        self.index = Product.index  # 부여한 뒤
        Product.index += 1          # 카운트 +1


# 할인 쿠폰 (부모 클래스)
class Discount:
    def __init__(self, name='쿠폰 없음'):
        self.name = name

    def discount_amount(self, total):
        return 0


# 비율 할인 (최대 금액 제한)
class RateDiscount(Discount):
    def __init__(self, rate, max_amount):
        # 부모 속성이 하나니까 한칸에 전달 -> name이 아래 폼이 되는거임
        super().__init__(f'{int(rate * 100)}% 할인 (최대 {max_amount:,}원)')
        self.rate = rate
        self.max_amount = max_amount

    def discount_amount(self, total):
        return min(int(round(total * self.rate, 2)), self.max_amount)


# 정액 할인 (최소 구매 금액 조건)
class FixedDiscount(Discount):
    def __init__(self, amount, min_total):
        super().__init__(f'{amount:,}원 할인 ({min_total:,}원 이상 구매 시)')
        self.amount = amount
        self.min_total = min_total

    def discount_amount(self, total):
        return self.amount if total >= self.min_total else 0


coupons = [
    Discount(),
    RateDiscount(0.1, 5000),
    FixedDiscount(3000, 20000),
]
current_coupon = coupons[0]  # 현재 적용된 쿠폰 (한 번에 1장)


# 숫자 입력 도우미 (숫자가 아니면 다시 입력)
def input_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print('숫자를 입력해 주세요.')


# 금액 계산: (상품 합계, 할인, 배송비, 결제 금액)
def calc_amounts():
    total = sum(p.price * p.in_cart for p in p_list)
    if total == 0:
        return 0, 0, 0, 0
    discount = current_coupon.discount_amount(total)
    base = total - discount
    delivery = 0 if base >= 30000 else 3000
    return total, discount, delivery, base + delivery


# 초이스
def choice():
    while True:
        print('----------------------------------------------')
        print('1.상품목록 2.담기 3.빼기 4.장바구니 5.쿠폰 6.결제 q.종료')
        print('----------------------------------------------')

        sel = input('선택: ')
        if sel == '1':
            product_list(p_list)
        elif sel == '2':
            add_p()
        elif sel == '3':
            minus_p()
        elif sel == '4':
            cart()
        elif sel == '5':
            coupon()
        elif sel == '6':
            cash()
        elif sel == 'q':
            print('프로그램을 종료합니다.')
            break


# 1. 상품목록
def product_list(p_list):
    for p in p_list:
        if p.count == 0:
            print(f'{p.index}. {p.name}    {p.price:,} (품절)')
        else:
            print(f'{p.index}. {p.name}    {p.price:,} (재고 {p.count}개)')


# 2. 담기
def add_p():
    n = input_int('상품 번호: ')
    if not (1 <= n <= len(p_list)):
        print('없는 상품 번호입니다.')
        return

    product = p_list[n - 1]
    if product.count == 0:
        print('품절된 상품입니다.')
        return

    count = input_int('수량: ')
    if count <= 0:
        print('1개 이상 입력해 주세요.')
        return

    # 재고는 결제 때 줄어드니, 지금 담을 수 있는 수량 = 재고 - 이미 담은 수량
    available = product.count - product.in_cart
    if count > available:
        print(f'재고가 부족합니다. (담을 수 있는 수량: {available}개)')
        return

    product.in_cart += count
    print(f'{product.name} {count}개를 담았습니다.')


# 3. 빼기

# # 다른 접근 방법  - 중간 번호가 없다는 가정하에 유용
# def minus_p():
#     n = input_int('상품 번호: ')
#     if n not in [p.index for p in p_list]:
#         print('없는 상품 번호입니다.')
#         return
#     ...
   
def minus_p():
    n = input_int('상품 번호: ')
    if not (1 <= n <= len(p_list)):  
        print('없는 상품 번호입니다.')
        return

    product = p_list[n - 1]
    if product.in_cart == 0:
        print('장바구니에 담긴 수량이 없습니다.')
        return

    count = input_int('수량: ')
    if count <= 0:
        print('1개 이상 입력해 주세요.')
        return
    if count > product.in_cart:
        print(f'담은 수량보다 많이 뺄 수 없습니다. (뺄 수 있는 수량: {product.in_cart}개)')
        return

    product.in_cart -= count
    print(f'{product.name} {count}개를 뺐습니다.')


# 4. 장바구니
def cart():
    items = [p for p in p_list if p.in_cart > 0]
    if not items:
        print('장바구니가 비어 있습니다.')
        return

    total, discount, delivery, pay = calc_amounts()

    print('----------------------------------------')
    for p in items:
        print(f'{p.name}   x {p.in_cart}   {p.price * p.in_cart:,}원')
    print('----------------------------------------')
    print(f'상품 합계              {total:,}원')
    print(f'할인                  {-discount:,}원  [{current_coupon.name}]')
    print(f'배송비                {delivery:,}원')
    print(f'결제 금액              {pay:,}원')
    print('----------------------------------------')


# 5. 쿠폰
def coupon():
    global current_coupon

    print('----------------------------------------')
    for i, c in enumerate(coupons, start=1):
        print(f'{i}. {c.name}')
    print('----------------------------------------')

    n = input_int('쿠폰 번호: ')
    if not (1 <= n <= len(coupons)):
        print('없는 쿠폰 번호입니다.')
        return

    current_coupon = coupons[n - 1]
    print(f'[{current_coupon.name}] 쿠폰을 적용했습니다.')


# 6. 결제
def cash():
    global current_coupon

    items = [p for p in p_list if p.in_cart > 0]
    if not items:
        print('장바구니가 비어 있습니다.')
        return

    total, discount, delivery, pay = calc_amounts()

    # 영수증 출력
    print('============== 영수증 ==============')
    for p in items:
        print(f'{p.name}   x {p.in_cart}   {p.price * p.in_cart:,}원')
    print('------------------------------------')
    print(f'상품 합계              {total:,}원')
    print(f'할인                  {-discount:,}원  [{current_coupon.name}]')
    print(f'배송비                {delivery:,}원')
    print(f'결제 금액              {pay:,}원')
    print('====================================')

    # 재고 감소 (결제할 때만)
    for p in items:
        p.count -= p.in_cart
        p.in_cart = 0

    # 쿠폰 초기화
    current_coupon = coupons[0]

    print('결제가 완료되었습니다. 감사합니다!')


def main():
    # 상품 세팅
    p_list.append(Product('무선 이어폰', 89_000, 3))
    p_list.append(Product('텀블러', 15_000, 10))
    p_list.append(Product('보조 배터리', 32_000, 5))
    p_list.append(Product('마우스패드', 9_000, 0))
    p_list.append(Product('USB 허브', 18_000, 4))

    choice()


main()