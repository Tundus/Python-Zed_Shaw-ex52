from nose.tools import assert_equal, assert_in
from app1 import app1


app1.config['TESTING']=True
web = app1.test_client()

def test_index():
    rv = web.get('/', follow_redirects=True)
    assert_equal(rv.status_code, 404)

    rv = web.get('/hello', follow_redirects=True)
    assert_equal(rv.status_code, 200)
    assert_in(b'Fill out this form', rv.data)

    data = {'name': 'Bandi', 'greet': 'Szia'}
    rv = web.post('/hello', follow_redirects=True, data=data)
    assert_in(b'Bandi', rv.data)
    assert_in(b'Szia', rv.data) 