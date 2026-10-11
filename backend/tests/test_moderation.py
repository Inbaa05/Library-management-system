"""Automated pytest test suite for librarian moderation actions and RBAC."""
import pytest
from app.models.comment import Comment
from tests.conftest import auth_headers

def test_librarian_can_approve_comment(client, librarian_user, student_user, db):
    # Student submits comment
    c = Comment(
        user_id=student_user.id,
        title='Book Request',
        comment_text='Please acquire more Clean Architecture books.',
        category='book_suggestion',
        status='pending_review'
    )
    db.session.add(c)
    db.session.commit()

    headers = auth_headers(client, librarian_user.email, 'LibPass@123')
    res = client.post(f'/api/v1/moderation/{c.id}/approve', json={'note': 'Approved for catalog'}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()['data']['status'] == 'approved'

def test_student_cannot_access_moderation_queue(client, student_user):
    headers = auth_headers(client, student_user.email, 'TestPass@123')
    res = client.get('/api/v1/moderation/queue', headers=headers)
    assert res.status_code == 403

def test_librarian_can_flag_comment(client, librarian_user, student_user, db):
    c = Comment(
        user_id=student_user.id,
        title='Flag test',
        comment_text='Some questionable comment that requires review.',
        category='general_feedback',
        status='pending_review'
    )
    db.session.add(c)
    db.session.commit()

    headers = auth_headers(client, librarian_user.email, 'LibPass@123')
    res = client.post(f'/api/v1/moderation/{c.id}/flag', json={
        'reason': 'Violates policy',
        'status': 'inappropriate'
    }, headers=headers)
    assert res.status_code == 200
    assert res.get_json()['data']['status'] == 'inappropriate'
    assert res.get_json()['data']['is_flagged'] is True

def test_dashboard_summary_counts(client, librarian_user):
    headers = auth_headers(client, librarian_user.email, 'LibPass@123')
    res = client.get('/api/v1/dashboard/summary', headers=headers)
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'total_comments' in data
    assert 'approved' in data
    assert 'pending_review' in data

def test_report_export_access_control(client, librarian_user, student_user):
    lib_headers = auth_headers(client, librarian_user.email, 'LibPass@123')
    res_lib = client.get('/api/v1/reports/export.csv', headers=lib_headers)
    assert res_lib.status_code == 200
    assert 'text/csv' in res_lib.content_type

    stu_headers = auth_headers(client, student_user.email, 'TestPass@123')
    res_stu = client.get('/api/v1/reports/export.csv', headers=stu_headers)
    assert res_stu.status_code == 403
