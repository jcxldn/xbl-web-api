# xbl-web-api

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Prouser123/xbl-web-api/build?logo=github&logoColor=white)
![Uptime Robot ratio (7 days)](https://img.shields.io/uptimerobot/ratio/7/m782558122-d298b8bb4b0d1c15272b7ddf)
[![coverage badge](https://img.shields.io/codecov/c/gh/prouser123/xbl-web-api.svg)](https://codecov.io/gh/Prouser123/xbl-web-api)
![python3 badge](https://img.shields.io/badge/python-3.10-blue.svg)

[Live Instance](https://xbl-api.prouser123.me/)

All routes return JSON unless otherwise specified.

## Routes

- `/titleinfo/<int:titleid>`

  Get title information by its title ID.

- `/legacysearch/<str:query>`

  Search the Xbox 360 Marketplace.

- `/gamertag/check/<str:username>`

  Check if the specified gamertag is available or taken.

- `/usercolors/define/<str:primary>/<str:secondary>/<str:tertiary>`

  Get an SVG representation of the defined colors.

- `/usercolors/get/xuid/<int:xuid>`

  Get an SVG representation of the user's colors.

- `/usercolors/get/gamertag/<gamertag>`

  Get an SVG representation of the user's colors.

### Profiles

- `/profile/xuid/<int:xuid>`

  Get a profile by the user's XUID.

- `/profile/gamertag<str:gamertag>`

  Get a profile by the user's gamertag.

- `/profile/settings/xuid/<int:xuid>`

  Get profile settings (less data) by the user's XUID.

- `/profile/settings/gamertag/<str:gamertag>`

  Get profile settings (less data) by the user's gamertag.

### Friends

- `/friends/summary/xuid/<int:xuid>`

  Get a user's friend summary (followers and following count) by their XUID.

- `/friends/summary/gamertag/<gamertag>`

  Get a user's friend summary (followers and following count) by their gamertag.

### Presence

- `/presence/xuid/<int:xuid>`

  Get a user's presence (status) by their XUID.

- `/presence/gamertag/<str:gamertag>`

  Get a user's presence (status) by their gamertag.

### User Stats

- `/userstats/xuid/<int:xuid>/titleid/<int:titleid>`

  Get a user's stats for a game by Title ID and user XUID.

- `/userstats/gamertag/<str:gamertag>/titleid/<int:titleid>`

  Get a user's stats for a game by Title ID and user gamertag.

### XUIDs

- `/xuid/<str:gamertag>`

  Get a user's XUID by their gamertag.

- `/xuid/<str:gamertag>/raw`

  Get a user's XUID by their gamertag and return as text.

### Achievements

- `/achievements/1/recent/<int:xuid>`

  Get the recent Xbox One achievements for a user XUID.

- `/achievements/360/recent/<int:xuid>`

  Get the recent Xbox 360 achievements for a user XUID.

- `/achievements/1/titleprogress/<int:xuid>/<int:titleid>`

  Get all achievements (both unlocked and locked) for an Xbox One user from their XUID and the game's Title ID.

- `/achievements/360/titleprogress/all/<int:xuid>/<int:titleid>`

  Get all available achievements for an Xbox 360 user from their XUID and the game's Title ID.

- `/achievements/360/titleprogress/earned/<int:xuid>/<int:titleid>`

  Get all earned / unlocked achievements for an Xbox 360 user from their XUID and the game's Title ID.

- `/achievements/1/titleprogress/detail/<int:xuid>/<uuid:scid>/<int:achievementid>`

  Get the achievement details for an Xbox One user from their XUID, the game's SCID (Service Config ID) and an achievement ID.
