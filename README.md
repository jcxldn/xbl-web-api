# xbl-web-api

![Jenkins](https://img.shields.io/jenkins/build/https/ci.prouser123.me/xbl-web-api?label=production%20build&logo=jenkins&logoColor=white)
[![coverage badge](https://img.shields.io/codecov/c/gh/prouser123/xbl-web-api.svg)](https://codecov.io/gh/Prouser123/xbl-web-api)
![python3.7 badge](https://img.shields.io/badge/python-3.7-blue.svg)

[Live Instance](https://xbl-api.prouser123.me/)

All routes return JSON unless otherwise specified.

## Routes

- `/titleinfo/<int:titleid>`

  Get title information by its title ID.

- `/legacysearch/<str:query>`

  Search the Xbox 360 Marketplace.

- `/profile/xuid/<int:xuid>`

  Get a profile by the user's XUID.

- `/profile/gamertag<str:gamertag>`

  Get a profile by the user's gamertag.

- `/profile/settings/xuid/<int:xuid>`

  Get profile settings (less data) by the user's XUID.

- `/profile/settings/gamertag/<str:gamertag>`

  Get profile settings (less data) by the user's gamertag.

- `/userstats/xuid/<int:xuid>/titleid/<int:titleid>`

  Get a user's stats for a game by Title ID and user XUID.

- `/userstats/gamertag/<str:gamertag>/titleid/<int:titleid>`

  Get a user's stats for a game by Title ID and user gamertag.

- `/xuid/<str:gamertag>`

  Get a user's XUID by their gamertag.

- `/xuid/<str:gamertag>/raw`

  Get a user's XUID by their gamertag and return as text.
