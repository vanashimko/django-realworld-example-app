from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy

from conduit.apps.articles.models import Article
from conduit.apps.authentication.models import User


class ArticlesTests(APITestCase):
    def setUp(self):
        username = 'testuser'
        email = 'test@example.com'
        password = 'testpassword'
        self.test_user = User.objects.create_user(username, email, password)
        self.client.credentials(HTTP_AUTHORIZATION="{0} {1}".format('Token', self.test_user.token))

    def test_should_create_article(self):
        article_payload = {
            'title': 'title',
            'body': 'body',
            'author': self.test_user.id
        }
        response = self.client.post(reverse('articles:articles-list'), data={
            'article': article_payload
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        from_db = Article.objects.get(slug=response.data['slug'])
        actual = {
            'title': from_db.title,
            'body': from_db.body,
            'author': self.test_user.id
        }
        self.assertEqual(actual, article_payload)

    def test_should_retrieve_all_articles(self):
        quantity = 3
        mommy.make(Article, author=self.test_user.profile, _quantity=quantity)

        response = self.client.get(reverse('articles:articles-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], quantity)
        self.assertEqual(len(response.data['results']), quantity)

    def test_should_retrieve_single_article(self):
        article = mommy.make(Article, slug=None, author=self.test_user.profile)

        response = self.client.get(reverse('articles:articles-detail', kwargs={'slug': article.slug}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], article.title)
