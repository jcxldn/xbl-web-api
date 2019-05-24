import json
import unittest
import os
import time

import server
import main

import routes.xuid


class Data():
    xuid_valid = {
        "gamertag": "x11net",
        "xuid": "2535453932267307"
    }

    xuid_invalid = {
        "error": 404,
        "gamertag": " ",
        "message": "user not found"
    }

    titleidstats_params = {
        # Prouser123 has stats for Forza Motorsport 6
        "gamertag": "Prouser123",
        "xuid": "2535469727531765",
        "titleID": "1694054782"
    }

    titleidstats_params_nostats = {
        # x11net does not have stats for Forza Motorsport 6
        "gamertag": "x11net",
        "xuid": "2535453932267307"
    }


class BaseTest(unittest.TestCase):
    def printCurrentTest(self):
        # print(": " + self.id().split('.')[-1])
        print("\n" + self.id().split('__.')[1])

    def assertIs200(self, req):
        return self.assertEqual(req.status_code, 200)

    def assertIsJSON(self, req):
        return self.assertEqual(req.mimetype, "application/json")

    def setUp(self):
        server.app.config["TESTING"] = True
        self.app = server.app.test_client()
        self.printCurrentTest()


class TestXuid(BaseTest):
    def test_xuid(self):
        with server.app.test_request_context():
            req = self.app.get("/xuid/x11net")
            # self.assertEqual(data["xuid"], req.json)
            self.assertDictEqual(Data.xuid_valid, req.json)

    def test_xuid_raw(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/xuid/{}/raw".format(Data.xuid_valid["gamertag"]))
            self.assertEqual(int(Data.xuid_valid["xuid"]), int(req.data))
            self.assertIs200(req)

    def test_xuid_invalid(self):
        with server.app.test_request_context():
            req = self.app.get("/xuid/%20")
            self.assertEqual(req.status_code, 404)
            self.assertEqual(req.mimetype, "application/json")
            self.assertDictEqual(Data.xuid_invalid, req.json)


class TestProfile(BaseTest):
    def assertIsValidProfileUsersResponse(self, req):
        self.assertIs200(req)
        self.assertIsJSON(req)
        self.assertIn("profileUsers", req.json)
        self.assertEqual(req.json["profileUsers"]
                         [0]["id"], Data.xuid_valid["xuid"])

    def test_xuid(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/profile/xuid/{}".format(Data.xuid_valid["xuid"]))
            self.assertIsValidProfileUsersResponse(req)

    def test_gamertag(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/profile/gamertag/{}".format(Data.xuid_valid["gamertag"]))
            self.assertIsValidProfileUsersResponse(req)

    def test_xuid_invalid_length(self):
        with server.app.test_request_context():
            req = self.app.get("/profile/xuid/123")
            self.assertEqual(req.status_code, 400)
            self.assertEqual(req.mimetype, "application/json")
            self.assertDictEqual(
                {"error": 400, "message": "invalid xuid"}, req.json)

    def test_xuid_invalid_user(self):
        with server.app.test_request_context():
            req = self.app.get("/profile/xuid/2584878536129842")
            self.assertEqual(req.status_code, 404)
            self.assertEqual(req.mimetype, "application/json")
            self.assertDictEqual(
                {"error": 404, "message": "user not found"}, req.json)

    def test_gamertag_invalid(self):
        with server.app.test_request_context():
            req = self.app.get("/profile/gamertag/%20")
            self.assertEqual(req.status_code, 404)
            self.assertEqual(req.mimetype, "application/json")
            self.assertDictEqual(Data.xuid_invalid, req.json)

    def test_xuid_settings(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/profile/settings/xuid/{}".format(Data.xuid_valid["xuid"]))
            self.assertIsValidProfileUsersResponse(req)

    def test_gamertag_settings(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/profile/settings/gamertag/{}".format(Data.xuid_valid["gamertag"]))
            self.assertIsValidProfileUsersResponse(req)


class TestUserStats(BaseTest):

    def assertTitleIdMatchesOriginalRequest(self, req):
        return self.assertEqual(req.json["groups"][0]["titleid"],
                                Data.titleidstats_params["titleID"])

    def assertXuidMatchesOriginalRequest(self, req, params):
        return self.assertEqual(req.json["groups"][0]["statlistscollection"]
                                [0]["arrangebyfieldid"], params["xuid"])

    def assertIsValidTitleIdResponse(self, req):
        self.assertIs200(req)
        self.assertIsJSON(req)
        # TitleID matches original request
        self.assertTitleIdMatchesOriginalRequest(req)
        # XUID matches original request
        self.assertXuidMatchesOriginalRequest(req, Data.titleidstats_params)
        # User has stats in the game
        self.assertIn("value", req.json["groups"]
                      [0]["statlistscollection"][0]["stats"][0])

    def assertIsValidTitleIdResponseNoStats(self, req):
        self.assertIs200(req)
        self.assertIsJSON(req)
        # TitleID matches original request
        self.assertTitleIdMatchesOriginalRequest(req)
        # XUID matches original request
        self.assertXuidMatchesOriginalRequest(
            req, Data.titleidstats_params_nostats)
        # User DOES NOT have stats in the game
        self.assertNotIn("value", req.json["groups"]
                         [0]["statlistscollection"][0]["stats"][0])

    def test_titleidstats_gamertag(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/userstats/gamertag/{}/titleid/{}".format(
                    Data.titleidstats_params["gamertag"],
                    Data.titleidstats_params["titleID"]
                ))
            self.assertIsValidTitleIdResponse(req)

    def test_titleidstats_xuid(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/userstats/xuid/{}/titleid/{}".format(
                    Data.titleidstats_params["xuid"],
                    Data.titleidstats_params["titleID"]
                ))
            self.assertIsValidTitleIdResponse(req)

    def test_titleidstats_gamertag_no_stats(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/userstats/gamertag/{}/titleid/{}".format(
                    Data.titleidstats_params_nostats["gamertag"],
                    Data.titleidstats_params["titleID"]
                ))
            self.assertIsValidTitleIdResponseNoStats(req)

    def test_titleidstats_xuid_no_stats(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/userstats/xuid/{}/titleid/{}".format(
                    Data.titleidstats_params_nostats["xuid"],
                    Data.titleidstats_params["titleID"]
                ))
            self.assertIsValidTitleIdResponseNoStats(req)


class TestMisc(BaseTest):
    def test_info(self):
        with server.app.test_request_context():
            req = self.app.get("/info")
            self.assertIs200(req)
            self.assertIsJSON(req)
            self.assertEqual(req.json["sha"], server.get_sha())
            self.assertEqual(req.json["routes"], server.get_routes())

    def test_readme(self):
        with server.app.test_request_context():
            req = self.app.get("/readme")
            self.assertIs200(req)
            with open("README.md") as f:
                self.assertEqual(req.get_data(
                    as_text=True).replace("\r", ""), f.read())

    def test_index(self):
        with server.app.test_request_context():
            req = self.app.get("/")
            self.assertIs200(req)
            with open("static/index.html") as f:
                self.assertEqual(req.get_data(
                    as_text=True).replace("\r", ""), f.read())


class TestDev(BaseTest):

    def isTimestamp(self, str):
        try:
            time.strptime(str, '%a, %d %b %Y %H:%M:%S %Z')
            # %a, %d %B %Y %T %Z - from strftime.net
        except ValueError:
            return False
        else:
            return True

    def test_reauth(self):
        with server.app.test_request_context():
            req = self.app.get("/dev/reauth")
            self.assertIs200(req)
            self.assertIsJSON(req)
            self.assertEqual(req.json["message"], "success")

    def test_isauth_true(self):
        with server.app.test_request_context():
            req = self.app.get("/dev/isauth")
            self.assertIs200(req)
            self.assertIsJSON(req)

            self.assertEqual(req.json["authenticated"], True)
            self.assertEqual(req.json["gt"], main.auth_mgr.userinfo.gamertag)

            self.assertTrue(self.isTimestamp(req.json["access"]["expires"]))
            self.assertTrue(self.isTimestamp(req.json["access"]["issued"]))

            self.assertTrue(self.isTimestamp(req.json["user"]["expires"]))
            self.assertTrue(self.isTimestamp(req.json["user"]["issued"]))


if __name__ == '__main__':
    print("HAI")
    main.authenticate()
    print("----------------------------------------------------------------------")
    unittest.main(warnings='ignore')
    # unittest.main()
