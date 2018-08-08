from json import loads

from preggy import expect


def test_enqueue1(client):
    """Test enqueue a job works"""

    data = {
        "container": "ubuntu",
        "command": "ls",
    }

    rv = client.post('/jobs', data=data, follow_redirects=True)

    obj = loads(rv.data)
    expect(obj['job']).not_to_be_null()
    expect(obj['status']).to_equal("queued")

    hash_key = f'rq:job:{obj["job"]}'
    app = client.application

    res = app.redis.exists(hash_key)
    expect(res).to_be_true()

    res = app.redis.hget(hash_key, 'status')
    expect(res).to_equal('queued')

    res = app.redis.hexists(hash_key, 'created_at')
    expect(res).to_be_true()

    res = app.redis.hexists(hash_key, 'enqueued_at')
    expect(res).to_be_true()

    res = app.redis.hexists(hash_key, 'data')
    expect(res).to_be_true()

    res = app.redis.hget(hash_key, 'origin')
    expect(res).to_equal('default')

    res = app.redis.hget(hash_key, 'description')
    expect(res).to_equal("easyq.worker.job.run_job('ubuntu', 'ls')")

    res = app.redis.hget(hash_key, 'timeout')
    expect(res).to_equal('180')
