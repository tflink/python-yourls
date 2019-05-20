## python-yourls

python-yourls is a simple python based API client for use with the YOURLS URL shortener (http://yourls.org/).

The details of what is possible with the API can be found at: http://yourls.org/#API

### Usage
```
from yourls.client import YourlsClient

client = YourlsClient(YOURLS_API_URL, token=YOURLS_SIGNATURE)
```

Or with username and password:
```
client = YourlsClient(YOURLS_API_URL, username=USERNAME, password=PASSWORD)
```

Creating short links:
```
short_url, page_title = client.shorten(ORIGINAL_URL, custom=SHORT)
```

Expanding short links:
```
url = client.expand(SHORT)
```

View URL stats:
```
stats = client.url_stats(SHORT)
```

View stats for a set of links:
```
links_stats = client.stats('top')
```

View site stats:
```
site_stats = client.db_stats()
```

### TODO
- Add test cases for new API calls.
- Confirm it works on Python 2.
- Port test cases to `unittest`.



**Credits:** Originally  created by Tim Flink (https://github.com/tflink/python-yourls). Forked and ported to Python 3, added support for new API calls by Setu Shah (https://github.com/setu4993/python-yourls).