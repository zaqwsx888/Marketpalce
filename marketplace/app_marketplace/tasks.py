from django.urls import reverse
from django.db import transaction
from marketplace.settings import get_base_url
from .models import OrderModel, PaymentModel, CartModel
from .serializers import PaymentStatusSerializer
from marketplace.celery import app
from import_export_celery.models import ImportJob
from import_export_celery import tasks
from django.utils.translation import ugettext as _
import requests


@app.task
def change_status_all_jobs():
    import_jobs = ImportJob.objects.filter(
        job_status='[Dry run] 5/5 Import job finished'
    ).all()
    for import_job in import_jobs:
        try:
            tasks._run_import_job(import_job, dry_run=False)
        except Exception as e:
            import_job.errors += _("Import error %s") % e + "\n"
            tasks.change_job_status(
                import_job, "import", "Import error", dry_run=False
            )
            import_job.save()
            return


@app.task
def payment_request(data):
    response = requests.post(
        url=get_base_url() + reverse('payments_api'), json=data)
    if 200 <= response.status_code < 300:
        result = response.json()
        serializer_result = PaymentStatusSerializer(data=result)

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
    else:
        order_number = data.get('order_number')
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
