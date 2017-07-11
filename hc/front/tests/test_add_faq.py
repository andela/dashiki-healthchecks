from hc.front.models import (FaqItem, FaqCategory)
from hc.front.forms import (AddFaqCategoryForm, AddFaqForm)
from hc.test import BaseTestCase
from django.urls import reverse


class AddFaqTestCase(BaseTestCase):

    def test_submit_empty_forms(self):
        category_form = AddFaqCategoryForm({})
        faq_item_form = AddFaqForm({})
        self.assertFalse(category_form.is_valid())
        self.assertFalse(faq_item_form.is_valid())

    def test_create_faq_cat(self):
        self.client.login(username="admin@test.com", password="pass")
        data = {'category': 'Category One'}
        form = AddFaqCategoryForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse("hc-save-cat"), data)
        # self.assertRedirects(response, "/docs/faq/")

        response = self.client.get(reverse("hc-docs-faq"))
        self.assertContains(response, "Category One", status_code=200)
        self.client.logout()

    def test_create_faq(self):
        self.client.login(username="admin@test.com", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        category.save()
        data = {'title': 'FAQ Title', 'body': 'FAQ Body', 'category': category.id}
        form = AddFaqForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse("hc-save-faq"), data)
        self.assertRedirects(response, "/docs/faq/")

        response = self.client.get(reverse("hc-docs-faq"))
        self.assertContains(response, "FAQ Body", status_code=200)
        self.assertContains(response, "FAQ Title", status_code=200)
        self.assertContains(response, "Category One", status_code=200)
        self.client.logout()

    def test_edit_faq(self):
        self.client.login(username="admin@test.com", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        faq = FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category)
        faq.save()
        new_data = {'title': 'FAQ Title Edited', 'body': 'FAQ Body Edited', 'category': category.id}

        response = self.client.get(reverse("hc-faq-edit", kwargs={'id': faq.id}))
        self.assertContains(response, "FAQ Body", status_code=200)

        response = self.client.post(reverse("hc-save-faq-edit", kwargs={'id': faq.id}), data=new_data)
        self.assertRedirects(response, "/docs/faq/", status_code=302)

        response = self.client.get(reverse("hc-docs-faq"))
        self.assertContains(response, "FAQ Body Edited", status_code=200)
        self.assertContains(response, "FAQ Title Edited", status_code=200)
        self.client.logout()

    def test_edit_faq_cat(self):
        self.client.login(username="admin@test.com", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        category.save()
        new_data = {'category': 'Category Edited'}

        response = self.client.get(reverse("hc-cat-edit", kwargs={'id': category.id}))
        self.assertContains(response, "Category One", status_code=200)

        response = self.client.post(reverse("hc-save-cat-edit", kwargs={'id': category.id}), data=new_data)
        self.assertRedirects(response, "/docs/faq/", status_code=302)

        response = self.client.get(reverse("hc-docs-faq"))
        self.assertContains(response, "Category Edited", status_code=200)
        self.client.logout()

    def test_access_to_faq_creation(self):
        response = self.client.get(reverse("hc-save-faq"))
        self.assertContains(response, "", status_code=302)
        self.assertIn("/accounts/login/", response.url)

    def test_delete_faq(self):
        self.client.login(username="admin@test.com", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        faq = FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category)
        faq.save()
        FaqItem.objects.create(title='FAQ Title2', body='FAQ Body2', category=category).save()

        response = self.client.get(reverse("hc-faq-delete", kwargs={'id': faq.id}))
        count = FaqItem.objects.count()
        self.assertContains(response, "", status_code=302)
        self.assertEqual(count, 1)
        self.client.logout()

    def test_delete_faq_category(self):
        self.client.login(username="admin@test.com", password="pass")
        category = FaqCategory.objects.create(category='Category One')
        FaqItem.objects.create(title='FAQ Title', body='FAQ Body', category=category).save()
        FaqItem.objects.create(title='FAQ Title2', body='FAQ Body2', category=category).save()

        response = self.client.get(reverse("hc-cat-delete", kwargs={'id': category.id}))
        count_cat = FaqCategory.objects.count()
        count_items = FaqItem.objects.count()
        self.assertContains(response, "", status_code=302)
        self.assertEqual(count_cat, 0)
        self.assertEqual(count_items, 0)
        self.client.logout()
