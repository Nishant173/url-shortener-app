# url-shortener-app
URL shortener API application

## CURLs
- Home page (GET): ```curl --location 'http://127.0.0.1:8000/'```
- Create user (POST):
```
curl --location 'http://127.0.0.1:8000/users/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "some-username-13"
}'
```
- List all short URLs by user (GET):
```
curl --location 'http://127.0.0.1:8000/short-urls/' \
--header 'Authorization: Bearer UD9NAR4BIY20W50MUCR3'
```
- Create one short URL (POST):
```
curl --location 'http://127.0.0.1:8000/short-urls/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer UD9NAR4BIY20W50MUCR3' \
--data '{
    "long_url": "https://en.wikipedia.org/wiki/FC_Bayern_Munich",
    "expires_at": "2023-12-01 17:30:00+0530",
    "expires_in_minutes": 2,
    "max_usage_count": 5
}'
```
- Get one short URL (GET):
```curl --location 'http://127.0.0.1:8000/short-urls/yitcwhgh.abc'```
- Get one short URL redirect (GET):
```
curl --location 'http://127.0.0.1:8000/short-urls/yitcwhgh.abc/redirect' \
--header 'Authorization: Bearer BPJ8N5AE2W6OMT7E4V1E'
```
- List short URL access log (GET):
```
curl --location 'http://127.0.0.1:8000/short-urls-log/'
```
