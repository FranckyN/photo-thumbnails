"""
    test_app
    ~~~~~~~~~~~~~
    Integration test cases
    copyright: ©2019 by Franck Nassé
"""
import requests as rq
import time
import pytest
import json
import os


def is_json(json_candidate):
    try:
        json.dumps(json_candidate)
        return True
    except:
        return False


def test_status_ok_pending(get_url_pending):
    response = rq.get(get_url_pending)
    assert response.status_code == 200


def test_json_ok(get_url_pending):
    response = rq.get(get_url_pending)
    assert is_json(response.json())


def test_photo_count(get_url_pending):
    response = rq.get(get_url_pending)
    assert len(response.json()) == 5


def test_pending_count(db_update_status, get_url_pending, all_uuids):
    curr_uuid = all_uuids()[0]
    response = rq.get(get_url_pending)
    curr_json = response.json()
    assert curr_uuid == next((x['uuid'] for x in curr_json if
                              x['uuid'] == curr_uuid), None)
    db_update_status('processing', curr_uuid)
    response = rq.get(get_url_pending)
    db_update_status('pending', curr_uuid)
    curr_json = response.json()
    assert next((x for x in curr_json if x['uuid'] == curr_uuid),
                None) is None and len(response.json()) == 4


def test_photo_process_bad_uuid(get_url_process):
    payload = {"data": ["DROP TABLE photos", "dfddf"]}
    response = rq.post(get_url_process, json=payload)
    assert is_json(response.json())
    curr_json = response.json()
    assert len(curr_json) == 2
    for x in curr_json:
        if x['uuid'] == "DROP TABLE photos" or x['uuid'] == "dfddf":
            assert not x['success'] and x['error']


def test_photo_process_good_uuid(get_url_process, all_uuids, db_photo_status,
                                 db_thumbnail):
    """
    Testing if the endpoint /photos/process is capable of processing 
    successfully two uuids.
    status should be completed.
    thumbnail image should be generated and accessible.
    table 'photo_thumbnails' should be updated.
    """
    uuids = all_uuids()
    payload = {"data": [uuids[1], uuids[0]]}
    response = rq.post(get_url_process, json=payload)
    assert is_json(response.json())
    curr_json = response.json()
    assert len(curr_json) == 2
    time.sleep(5)
    for x in curr_json:
        if x['uuid'] == uuids[1] or x['uuid'] == uuids[0]:
            assert x['success'] and not x['error']
        assert db_photo_status(x['uuid']) == 'completed'
        thumb_data = db_thumbnail(x['uuid'])
        print(thumb_data['url'])
        assert os.path.exists(thumb_data['url']) and thumb_data['width'] <= 320 \
               and thumb_data['height'] <= 320


def test_process_missing_photo(get_url_process,
                               ms_uuids,
                               db_photo_status,
                               db_insert_missing_image,
                               db_delete_missing_image):
    """
    Testing the processing of a missing image, the status
    should be 'failed'.
    """
    db_insert_missing_image()
    ms_uuid = ms_uuids()
    payload = {"data": [ms_uuid]}
    response = rq.post(get_url_process, json=payload)
    assert is_json(response.json())
    curr_json = response.json()
    assert len(curr_json) == 1
    time.sleep(5)
    assert curr_json[0]['uuid'] == ms_uuid and curr_json[0]['success']
    assert db_photo_status(curr_json[0]['uuid']) == 'failed'
    db_delete_missing_image()
