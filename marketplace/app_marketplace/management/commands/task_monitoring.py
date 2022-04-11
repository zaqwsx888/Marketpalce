import sys
from celery.result import AsyncResult
from ...models import OrderModel, PaymentModel, CartModel
from ...serializers import PaymentStatusSerializer, PaymentSerializer
from django.core.management.base import BaseCommand
from djangoProject.celery import app
from django.db import transaction


def my_monitor(celery_app):
    """
    Функция мониторинга событий задач celery. В зависимости от события,
     выполняются две функции, основные задачи которых завершение заказа,
      фиксирование статуса оплаты и очистка корзины при успешной оплате.
    """
    def announce_completed_tasks(event):
        """Функция, выполняющаяся при успешном завершении задачи."""
        result = AsyncResult(event['uuid'])
        serializer_result = PaymentStatusSerializer(data=result.result)

        # Если результат оплаты от API оплаты прошел проверку валидности,
        # выполняем завершение заказа
        if serializer_result.is_valid():
            order_number = serializer_result.data.get('order_number')
            status = serializer_result.data.get('status')
            order = OrderModel.objects.filter(
                pk=order_number).select_related('cart').first()
            if order:
                with transaction.atomic():
                    # Завершаем заказ в любом случае
                    order.status = 'completed'
                    order.save(update_fields=['status'])

                    # В зависимости от статуса ответа устанавливаем
                    # подтверждение оплаты в True или False в модели оплаты
                    if status == 'paid':
                        PaymentModel.objects.update_or_create(
                            order=order,
                            price=order.order_total_price,
                            prove=True
                        )

                        # Корзину переводим в статус "Завершено"
                        cart = CartModel.objects.filter(
                            order__pk=order.pk,
                            status='actively'
                        ).prefetch_related('products').first()
                        if cart:
                            cart.status = 'completed'
                            cart.save(update_fields=['status'])
                    else:
                        # В модели оплаты поле подтверждения устанавливаем
                        # в False
                        PaymentModel.objects.update_or_create(
                            order=order,
                            price=order.order_total_price,
                            prove=False
                        )
            else:
                # Если заказ с текущим номером отсутствует, ничего не делаем
                pass

        # Если результат от API оплаты не прошел проверку валидности,
        # проверяем на какой запрос был отправлен ответ
        # чтобы завершить данный заказ
        elif result.args is not None and len(result.args):
            serializer_payment_details = PaymentSerializer(data=result.args[0])
            if serializer_payment_details.is_valid():
                order_number = serializer_payment_details.data.get(
                    'order_number')
                order = OrderModel.objects.filter(
                    pk=order_number).select_related('cart').first()
                if order:
                    with transaction.atomic():
                        # Завершаем заказ
                        order.status = 'completed'
                        order.save(update_fields=['status'])

                        # В модели оплаты поле подтверждения устанавливаем
                        # в False
                        PaymentModel.objects.update_or_create(
                            order=order,
                            price=order.order_total_price,
                            prove=False
                        )
                else:
                    pass

    def task_not_completed(event):
        """
        Функция, выполняющаяся в случае отклонения задачи или в
         случае невыполнения задачи
        """
        result = AsyncResult(event['uuid'])
        if result.args is not None and len(result.args):
            serializer_payment_details = PaymentSerializer(
                data=result.args[0])
            if serializer_payment_details.is_valid():
                order_number = serializer_payment_details.data.get(
                    'order_number')
                order = OrderModel.objects.filter(
                    pk=order_number).select_related('cart').first()
                if order:
                    with transaction.atomic():
                        # Завершаем заказ
                        order.status = 'completed'
                        order.save(update_fields=['status'])

                        # В модели оплаты поле подтверждения устанавливаем
                        # в False
                        PaymentModel.objects.update_or_create(
                            order=order,
                            price=order.order_total_price,
                            prove=False
                        )
                else:
                    # Если заказ с текущим номером отсутствует,
                    # ничего не делаем
                    pass

    try:
        with celery_app.connection() as connection:
            recv = celery_app.events.Receiver(connection, handlers={
                'task-succeeded': announce_completed_tasks,
                'task-failed': task_not_completed,
                'task-revoked': task_not_completed,
            })
            recv.capture(limit=None, timeout=None, wakeup=True)
    except (KeyboardInterrupt, SystemExit):
        print("EXCEPTION KEYBOARD INTERRUPT")
        sys.exit()


class Command(BaseCommand):

    def handle(self, *args, **options):
        my_monitor(app)
