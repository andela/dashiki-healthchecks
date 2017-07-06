from hc.front.models import (FaqItem, FaqCategory)
from hc.front.forms import (AddFaqCategoryForm, AddFaqForm)
from hc.test import BaseTestCase
from django.urls import reverse


class AddFaqTestCase(BaseTestCase):

    def test_create_faq_cat(self):
        self.client.login(username="admin", password="pass")
        form = AddFaqCategoryForm({'category': 'Category One'})
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertEqual(result.category, "Category One")
        self.client.logout()

    def test_create_faq(self):
        category = FaqCategory.objects.create(category='Category One')
        faq = FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category)
        faq.save()
        self.assertEqual(faq.title, 'FAQ Title')
        self.assertEqual(faq.body, 'FAQ Body')
        self.assertEqual(category.category, 'Category One')

    def test_submit_empty_forms(self):
        category_form = AddFaqCategoryForm({})
        faq_item_form = AddFaqForm({})
        self.assertFalse(category_form.is_valid())
        self.assertFalse(faq_item_form.is_valid())

    def test_edit_faq(self):
        self.client.login(username="admin", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        faq = FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category)
        faq.save()
        response = self.client.get(reverse("hc-faq-edit", kwargs={'id': faq.id}))
        self.assertContains(response, "", status_code=302)
        self.client.logout()

    def test_access_to_faq_creation(self):
        response = self.client.get(reverse("hc-save-faq"))
        self.assertContains(response, "", status_code=302)
        self.assertIn("/accounts/login/", response.url)

    def test_delete_faq(self):
        self.client.login(username="admin", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        faq = FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category)
        faq.save()
        FaqItem.objects.create(title='FAQ Title2', body='FAQ Body2', category=category).save()
        response = self.client.get(reverse("hc-faq-delete", kwargs={'id': faq.id}))
        count = FaqItem.objects.count()
        print("Counted: {}".format(str(count)))
        self.assertContains(response, "", status_code=302)
        # self.assertEqual(count, 1)
        self.client.logout()

    def test_delete_faq_category(self):
        self.client.login(username="admin", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category).save()
        FaqItem.objects.create(title='FAQ Title2', body='FAQ Body2', category=category).save()
        response = self.client.get(reverse("hc-cat-delete", kwargs={'id': category.id}))
        count_cat = FaqCategory.objects.count()
        count_items = FaqItem.objects.count()
        print("Counted: {}, {}".format(str(count_cat), str(count_items)))
        self.assertContains(response, "", status_code=302)
        # self.assertEqual(count_cat, 0)
        # self.assertEqual(count_items, 0)
        self.client.logout()
