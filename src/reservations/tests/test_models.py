from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from djmoney.money import Money
from unittest.mock import patch
from ..models import TicketPurchase, Payment, PointsPayment
from activities.models import Ticket, Activity, Tour
from profiles.models import CreditCard
from django.core.exceptions import ValidationError

User = get_user_model()

class ModelsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.activity = Tour.objects.create(name="Test Activity", allow_points=True, points_gift=10, takeoff_date=timezone.now() + timezone.timedelta(days=1), refund_rate=10, duration= timezone.timedelta(days=1), upfront_rate= 100)
        self.ticket = Ticket.objects.create(activity=self.activity, price=Money(50, 'USD'), stock=10, valid_until=timezone.now() + timezone.timedelta(days=1), points_discount_price=12, points_discount= 24)
        self.user.creditcard = CreditCard.objects.create(user=self.user, balance=Money(100, 'USD'))  # Assuming CreditCard model
       

    def test_ticket_purchase_creation(self):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        self.assertEqual(reservation.unpaid_amount.amount, Decimal('0.00'))
        self.assertFalse(reservation.scanned)
        self.assertFalse(reservation.canceled)
        self.assertIsNone(reservation.scan_date)

    def test_ticket_validation(self):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        reservation.clean()
        self.assertEqual(reservation.validation_message, {})

    def test_ticket_validation_invalid(self):
        self.ticket.is_valid = False
        self.ticket.save()
        reservation = TicketPurchase(owner=self.user, ticket=self.ticket)
        with self.assertRaises(ValidationError):
            reservation.clean()

    @patch('myapp.models.convert_money', return_value=Money(100, 'USD'))
    def test_payment_creation(self, mock_convert_money):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        payment = Payment.objects.create(
            content_object=reservation,
            amount=Money(50, 'USD'),
            discount=Decimal('0.10')
        )
        self.assertEqual(payment.amount.amount, Decimal('50.00'))
        self.assertEqual(payment.discount, Decimal('0.10'))

    def test_points_payment_creation(self):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        points_payment = PointsPayment.objects.create(
            content_object=reservation,
            amount=50
        )
        self.assertEqual(points_payment.amount, 50)

    def test_payment_clean_insufficient_funds(self):
        self.user.creditcard.balance = Money(10, 'USD')
        self.user.creditcard.save()
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        payment = Payment(
            content_object=reservation,
            amount=Money(50, 'USD'),
            discount=Decimal('0.10')
        )
        with self.assertRaises(ValidationError):
            payment.clean()

    def test_points_payment_clean_insufficient_points(self):
        self.user.pointswallet.num_points = 10
        self.user.pointswallet.save()
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        points_payment = PointsPayment(
            content_object=reservation,
            amount=50
        )
        with self.assertRaises(ValidationError):
            points_payment.clean()

    @patch('myapp.models.TicketPurchase.save', side_effect=TicketPurchase.save)
    def test_ticket_purchase_save(self, mock_save):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        reservation.save()
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.stock, 9)

    @patch('myapp.models.Payment.save', side_effect=Payment.save)
    def test_payment_save(self, mock_save):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        payment = Payment.objects.create(
            content_object=reservation,
            amount=Money(50, 'USD'),
            discount=Decimal('0.10')
        )
        payment.save()
        self.user.creditcard.refresh_from_db()
        self.assertEqual(self.user.creditcard.balance, Money(50, 'USD'))

    @patch('myapp.models.PointsPayment.save', side_effect=PointsPayment.save)
    def test_points_payment_save(self, mock_save):
        reservation = TicketPurchase.objects.create(
            owner=self.user,
            ticket=self.ticket,
        )
        points_payment = PointsPayment.objects.create(
            content_object=reservation,
            amount=50
        )
        points_payment.save()
        self.user.pointswallet.refresh_from_db()
        self.assertEqual(self.user.pointswallet.num_points, 50)
