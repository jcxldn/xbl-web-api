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
        # jcxLDN has stats for Forza Motorsport 6
        "gamertag": "jcxLDN",
        "xuid": "2535469727531765",
        "titleID": "1694054782"
    }

    titleidstats_params_nostats = {
        # x11net does not have stats for Forza Motorsport 6
        "gamertag": "x11net",
        "xuid": "2535453932267307"
    }


class BaseTest(unittest.TestCase):
    def tearDown(self):
        # After every test, sleep 0.5 seconds to hopefully avoid 429 responses. (Too Many Requests)
        time.sleep(0.5)

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


class TestFriends(BaseTest):
    def assertIsValidSummaryResponse(self, req):
        self.assertIs200(req)
        self.assertIsJSON(req)
        self.assertIn("followers", req.json)
        self.assertIn("following", req.json)
        self.assertTrue(isinstance(req.json["followers"], int))
        self.assertTrue(isinstance(req.json["following"], int))

    def test_summary_xuid(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/friends/summary/xuid/{}".format(Data.xuid_valid["xuid"]))
            self.assertIsValidSummaryResponse(req)

    def test_summary_gamertag(self):
        with server.app.test_request_context():
            req = self.app.get(
                "/friends/summary/gamertag/{}".format(Data.xuid_valid["gamertag"]))
            self.assertIsValidSummaryResponse(req)

    # Probably a good idea to add invalid tests, see GH-1


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

    def test_titleinfo(self):
        with server.app.test_request_context():
            # Forza Motorsport 6
            req = self.app.get(
                "/titleinfo/" + Data.titleidstats_params["titleID"])
            self.assertIs200(req)
            self.assertIsJSON(req)

            data = req.json["titles"][0]

            # Ensure the titleId matches
            self.assertEqual(
                data["titleId"], Data.titleidstats_params["titleID"])
            self.assertEqual(data["modernTitleId"],
                             Data.titleidstats_params["titleID"])

            # Ensure some data matches
            self.assertEqual(data["name"], "Forza Motorsport 6")
            self.assertEqual(data["type"], "Game")
            self.assertEqual(data["mediaItemType"], "Application")
            self.assertEqual(
                data["pfn"], "Microsoft.MonumentBaseGame_8wekyb3d8bbwe")
            self.assertEqual(data["serviceConfigId"],
                             "417d0100-b230-41cf-975d-3eaa64f9397e")

    def test_legacysearch(self):
        with server.app.test_request_context():
            # This will return some data, currently 9 items
            req = self.app.get("/legacysearch/Halo")
            self.assertIs200(req)
            self.assertIsJSON(req)

            total_count = req.json["Totals"][0]["Count"]
            self.assertEqual(len(req.json["Items"]), total_count)

            self.assertEqual(total_count, 9)

            self.assertEqual(req.json["Totals"][0]["Name"], "GameType")

    def test_legacysearch_nodata(self):
        with server.app.test_request_context():
            # This will not return any results
            req = self.app.get("/legacysearch/123456789")
            self.assertIs200(req)
            self.assertIsJSON(req)

            self.assertEqual(req.json["Totals"][0]["Name"], "GameType")
            self.assertEqual(req.json["Totals"][0]["Count"], 0)

    def test_gamertag_check(self):
        with server.app.test_request_context():
            req = self.app.get("/gamertag/check/Prouser123")
            self.assertIs200(req)
            self.assertIsJSON(req)

            self.assertEqual(req.json["available"], "false")
            self.assertEqual(req.json["code"], 409)

    def test_gamertag_check_free(self):
        with server.app.test_request_context():
            req = self.app.get("/gamertag/check/sdakjdwaskwad")
            self.assertIs200(req)
            self.assertIsJSON(req)

            self.assertEqual(req.json["available"], "true")
            self.assertEqual(req.json["code"], 200)

    def test_usercolors_define(self):
        with server.app.test_request_context():
            req = self.app.get("/usercolors/define/1/2/3")
            self.assertIs200(req)
            self.assertEqual(req.mimetype, "image/svg+xml")
            # TODO: Check the Response content

    def test_usercolors_get_xuid(self):
        with server.app.test_request_context():
            req = self.app.get("/usercolors/get/xuid/" +
                               Data.xuid_valid["xuid"])
            self.assertIs200(req)
            self.assertEqual(req.mimetype, "image/svg+xml")
            # TODO: Check the Response content

    def test_usercolors_get_gamertag(self):
        with server.app.test_request_context():
            req = self.app.get("/usercolors/get/gamertag/" +
                               Data.xuid_valid["gamertag"])
            self.assertIs200(req)
            self.assertEqual(req.mimetype, "image/svg+xml")
            # TODO: Check the Response content


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
