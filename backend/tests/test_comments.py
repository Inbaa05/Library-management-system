"""Automated pytest test suite for comment pipeline and moderation."""
import pytest
from app.models.comment import Comment
from tests.conftest import auth_headers

def test_submit_comment_valid(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    res = client.post('/api/v1/comments/', json={
        'title': 'Need more Python programming books',
        'comment_text': 'The library currently has very few modern Python and data science books.',
        'category': 'book_suggestion'
    }, headers=headers)
    assert res.status_code == 201
    data = res.get_json()['data']
    assert data['title'] == 'Need more Python programming books'
    assert data['status'] in ('pending_review', 'approved')

def test_submit_comment_empty_text(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    res = client.post('/api/v1/comments/', json={
        'title': 'Empty test',
        'comment_text': '   '
    }, headers=headers)
    assert res.status_code == 422

def test_submit_comment_unauthenticated(client):
    res = client.post('/api/v1/comments/', json={
        'title': 'Test title',
        'comment_text': 'Test comment text for checking unauthorized submission.'
    })
    assert res.status_code == 401

def test_exact_duplicate_detection(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    payload = {
        'title': 'Quiet study space requested',
        'comment_text': 'Please make sure the third floor remains an absolute quiet study zone for students.',
        'category': 'library_facility'
    }
    res1 = client.post('/api/v1/comments/', json=payload, headers=headers)
    assert res1.status_code == 201

    res2 = client.post('/api/v1/comments/', json=payload, headers=headers)
    assert res2.status_code == 201
    data2 = res2.get_json()['data']
    assert data2['status'] == 'duplicate'
    assert data2['duplicate_of_id'] == res1.get_json()['data']['id']

def test_near_duplicate_detection(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    res1 = client.post('/api/v1/comments/', json={
        'title': 'Slow wifi connection in the library reading room',
        'comment_text': 'The wifi connection in the reading room is constantly dropping and very slow.',
        'category': 'wifi_digital'
    }, headers=headers)
    assert res1.status_code == 201

    # Slightly altered wording with high token overlap
    res2 = client.post('/api/v1/comments/', json={
        'title': 'Wifi connection in the library reading room is slow',
        'comment_text': 'The wifi connection in the reading room is slow and constantly dropping.',
        'category': 'wifi_digital'
    }, headers=headers)
    assert res2.status_code == 201
    data2 = res2.get_json()['data']
    assert data2['status'] in ('duplicate', 'near_duplicate')

def test_irrelevant_comment_flagged(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    res = client.post('/api/v1/comments/', json={
        'title': 'Delicious pasta recipe',
        'comment_text': 'To cook delicious pasta boil water with salt and tomato garlic sauce.'
    }, headers=headers)
    assert res.status_code == 201
    data = res.get_json()['data']
    assert data['status'] == 'irrelevant'
    assert data['is_flagged'] is True

def test_inappropriate_comment_flagged(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    res = client.post('/api/v1/comments/', json={
        'title': 'Check this library deal out',
        'comment_text': 'Visit this online casino spam link for free money immediately!'
    }, headers=headers)
    assert res.status_code == 201
    data = res.get_json()['data']
    assert data['status'] == 'inappropriate'
    assert data['is_flagged'] is True
