from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy

from conduit.apps.articles.models import Article, Tag
from conduit.apps.authentication.models import User


class ArticlesTests(APITestCase):
    def setUp(self):
        username = 'testuser'
        email = 'test@example.com'
        password = 'testpassword'
        self.test_user = User.objects.create_user(username, email, password)
        self.client.credentials(HTTP_AUTHORIZATION="{0} {1}".format('Token', self.test_user.token))

    def test_should_create_article(self):
        expected_article = {
            'title': 'title',
            'body': 'body',
            'author': self.test_user.id
        }
        response = self.client.post(reverse('articles:articles-list'), data=expected_article)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        from_db = Article.objects.get(slug=response.data['slug'])
        actual = {
            'title': from_db.title,
            'body': from_db.body,
            'author': self.test_user.id
        }
        self.assertEqual(actual, expected_article)

    def test_should_create_article_based_on_authorized_user(self):
        expected_article = {
            'title': 'title',
            'body': 'body',
        }
        response = self.client.post(reverse('articles:articles-list'), data=expected_article)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        from_db = Article.objects.get(slug=response.data['slug'])
        actual = {
            'title': from_db.title,
            'body': from_db.body,
            'author': from_db.author.id
        }
        expected_article['author'] = self.test_user.id
        self.assertEqual(actual, expected_article)

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

    def test_should_update_single_article(self):
        original_article = mommy.make(Article, slug=None, author=self.test_user.profile)
        another_user = User.objects.create_user('new_name', 'a@b.com')
        article_payload = {
            'title': 'title',
            'body': 'body',
            'author': another_user.id
        }

        response = self.client.put(reverse('articles:articles-detail', kwargs={'slug': original_article.slug}),
                                   data=article_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        from_db = Article.objects.get(slug=original_article.slug)
        actual = {
            'title': from_db.title,
            'body': from_db.body,
            'author': another_user.id
        }
        self.assertEqual(actual, article_payload)

    def test_should_retrieve_article_by_tag(self):
        tag1 = Tag.objects.create(tag='tag1', slug='tag1')
        tag2 = Tag.objects.create(tag='tag2', slug='tag2')
        expected_article = mommy.make(Article, slug=None, tags=[tag1], author=self.test_user.profile)
        mommy.make(Article, slug=None, tags=[tag2], author=self.test_user.profile)

        response = self.client.get(reverse('articles:articles-list'), {'tag': tag1.tag})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['slug'], expected_article.slug)

    def test_should_retrieve_article_by_author(self):
        another_user = User.objects.create_user('new_name', 'a@b.com')
        expected_article = mommy.make(Article, slug=None, author=another_user.profile)
        mommy.make(Article, slug=None, author=self.test_user.profile)

        response = self.client.get(reverse('articles:articles-list'), {'author': another_user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['slug'], expected_article.slug)
