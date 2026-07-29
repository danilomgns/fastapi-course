import requests

headers = {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzgzMTIxNDc5fQ.55ek3lRJ0ZXA--q91J2t-e0HX-GlI3lxzaRHpMgCXG4"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)

print(requisicao)
print(requisicao.json())