import unittest2
import responses
import zensend

try:
  from urlparse import parse_qsl
except:
  from urllib.parse import parse_qsl


try:
  from urllib import urlencode
except:
  from urllib.parse import urlencode

class TestZenSend(unittest2.TestCase):

  def canonicalize(self, body):
    params = parse_qsl(body)
    params.sort()
    return urlencode(params)

  @responses.activate
  def test_check_balance(self):
    responses.add(responses.GET, "https://api.zensend.io/v3/checkbalance", body='{"success":{"balance":100.2}}', status=200,
                  content_type='application/json')
    
    client = zensend.Client("api_key")
    self.assertEqual(client.check_balance(), 100.2)
    self.assertEqual(len(responses.calls), 1)
    self.assertEqual(responses.calls[0].request.headers["X-API-KEY"], "api_key")

  @responses.activate
  def test_get_prices(self):
    responses.add(responses.GET, "https://api.zensend.io/v3/prices", body='{"success":{"prices_in_pence":{"GB":1.23,"US":1.24}}}', status=200,
                  content_type='application/json')
    
    client = zensend.Client("api_key")
    self.assertEqual(client.get_prices(), {"GB":1.23, "US":1.24})
    self.assertEqual(len(responses.calls), 1)
    self.assertEqual(responses.calls[0].request.headers["X-API-KEY"], "api_key")

  @responses.activate 
  def test_send_sms(self):
    responses.add(responses.POST,  "https://api.zensend.io/v3/sendsms", body="""
    {
      "success": {
          "txguid": "7CDEB38F-4370-18FD-D7CE-329F21B99209",
          "numbers": 2,
          "smsparts": 1,
          "encoding": "gsm",
          "cost_in_pence": 5.4,
          "new_balance_in_pence":10.2
      }
    }
""", status=200, content_type='application/json')

    client = zensend.Client("api_key")
    response = client.send_sms(body = "BODY", originator = "ORIG", numbers = ["447796354848","447796354849"])
    self.assertEqual(response.numbers, 2)
    self.assertEqual(response.sms_parts, 1)
    self.assertEqual(response.encoding, "gsm")
    self.assertEqual(response.cost_in_pence, 5.4)
    self.assertEqual(response.new_balance_in_pence, 10.2)
    self.assertEqual(response.tx_guid, "7CDEB38F-4370-18FD-D7CE-329F21B99209")

    self.assertEqual(len(responses.calls), 1)
    self.assertEqual(responses.calls[0].request.headers["X-API-KEY"], "api_key")
    self.assertEqual(self.canonicalize(responses.calls[0].request.body), self.canonicalize("BODY=BODY&ORIGINATOR=ORIG&NUMBERS=447796354848%2C447796354849"))

  @responses.activate
  def test_create_msisdn_verification(self):
    responses.add(responses.POST, "https://verify.zensend.io/api/msisdn_verify", body="""
    {
      "success": {
        "session": "SESS"
      }
    }
""", status = 200, content_type = 'application/json')

    client = zensend.Client("api_key")

    session = client.create_msisdn_verification("44123456790")
    self.assertEqual(session, "SESS")
    self.assertEqual(self.canonicalize(responses.calls[0].request.body), self.canonicalize("NUMBER=44123456790"))

  @responses.activate
  def test_create_msisdn_verification_with_params(self):
    responses.add(responses.POST, "https://verify.zensend.io/api/msisdn_verify", body="""
    {
      "success": {
        "session": "SESS"
      }
    }
""", status = 200, content_type = 'application/json')

    client = zensend.Client("api_key")

    session = client.create_msisdn_verification("44123456790", "message", "orig")
    self.assertEqual(session, "SESS")
    self.assertEqual(self.canonicalize(responses.calls[0].request.body), self.canonicalize("NUMBER=44123456790&MESSAGE=message&ORIGINATOR=orig"))

  @responses.activate
  def test_msisdn_verification_status(self):
    responses.add(responses.GET, "https://verify.zensend.io/api/msisdn_verify", body="""
    {
      "success": {"msisdn": "441234567890"}
    }
""", status=200, content_type='application/json')

    client = zensend.Client("api_key")
    msisdn = client.msisdn_verification_status("SESS")
    self.assertEqual(msisdn, "441234567890")
    self.assertEqual(len(responses.calls), 1)

    self.assertEqual(responses.calls[0].request.url, "https://verify.zensend.io/api/msisdn_verify?SESSION=SESS")

  @responses.activate 
  def test_operator_lookup(self):
    responses.add(responses.GET,  "https://api.zensend.io/v3/operator_lookup", body="""
    {
      "success": {
          "mcc": "123",
          "mnc": "456",
          "operator": "o2-uk",
          "cost_in_pence": 2.5,
          "new_balance_in_pence":100.0
      }
    }
""", status=200, content_type='application/json')

    client = zensend.Client("api_key")
    response = client.lookup_operator("441234567890")
    self.assertEqual(response.mcc, "123")
    self.assertEqual(response.mnc, "456")
    self.assertEqual(response.operator, "o2-uk")
    self.assertEqual(response.cost_in_pence, 2.5)
    self.assertEqual(response.new_balance_in_pence, 100.0)

    self.assertEqual(len(responses.calls), 1)
    self.assertEqual(responses.calls[0].request.headers["X-API-KEY"], "api_key")


  @responses.activate 
  def test_operator_lookup_fails(self):
    responses.add(responses.GET,  "https://api.zensend.io/v3/operator_lookup", body="""
    {
      "failure": {
          "failcode": "DATA_MISSING",
          "cost_in_pence": 2.5,
          "new_balance_in_pence":100.0
      }
    }
""", status=503, content_type='application/json')


    client = zensend.Client("api_key")

    with self.assertRaises(zensend.ZenSendException) as cm:
      client.lookup_operator("441234567890")

    self.assertEqual(cm.exception.failcode, "DATA_MISSING")
    self.assertEqual(cm.exception.cost_in_pence, 2.5)
    self.assertEqual(cm.exception.new_balance_in_pence, 100.0)


  @responses.activate 
  def test_send_sms_with_optional_paramters(self):
    responses.add(responses.POST,  "https://api.zensend.io/v3/sendsms", body="""
    {
      "success": {
          "txguid": "7CDEB38F-4370-18FD-D7CE-329F21B99209",
          "numbers": 2,
          "smsparts": 1,
          "encoding": "gsm",
          "cost_in_pence": 2.5,
          "new_balance_in_pence": 100.0
      }
    }
  """, status=200, content_type='application/json')

    client = zensend.Client("api_key")
    response = client.send_sms(body = "BODY", originator = "ORIG", numbers = ["447796354848","447796354849"], originator_type = "alpha", encoding = "gsm", timetolive_in_minutes = 60)
    self.assertEqual(response.numbers, 2)
    self.assertEqual(response.sms_parts, 1)
    self.assertEqual(response.encoding, "gsm")
    self.assertEqual(response.tx_guid, "7CDEB38F-4370-18FD-D7CE-329F21B99209")

    self.assertEqual(len(responses.calls), 1)
    self.assertEqual(responses.calls[0].request.headers["X-API-KEY"], "api_key")


    self.assertEqual(self.canonicalize(responses.calls[0].request.body), self.canonicalize("BODY=BODY&ORIGINATOR=ORIG&ORIGINATOR_TYPE=alpha&ENCODING=gsm&TIMETOLIVE=60&NUMBERS=447796354848%2C447796354849"))


  @responses.activate
  def test_handle_wrong_content_type(self):
    responses.add(responses.POST,  "https://api.zensend.io/v3/sendsms", body="Gateway Timeout", status=503, content_type='text/plain')
    client = zensend.Client("api_key")
    with self.assertRaises(zensend.ZenSendException) as cm:
      client.send_sms(body = "BODY", originator = "ORIG", numbers = ["447796354848","447796354849"])

    self.assertEqual(cm.exception.http_code, 503)

  @responses.activate
  def test_handle_json_with_missing_keys(self):
    responses.add(responses.POST,  "https://api.zensend.io/v3/sendsms", body="{}", status=503, content_type='application/json')
    client = zensend.Client("api_key")
    with self.assertRaises(zensend.ZenSendException) as cm:
      client.send_sms(body = "BODY", originator = "ORIG", numbers = ["447796354848","447796354849"])

    self.assertEqual(cm.exception.http_code, 503)

  @responses.activate
  def test_handle_parameter_error(self):
    responses.add(responses.POST,  "https://api.zensend.io/v3/sendsms", body="""
    {
      "failure": {
          "failcode": "IS_EMPTY",
          "parameter": "BODY"

      }
    }""", status=400, content_type='application/json')
    client = zensend.Client("api_key")
    with self.assertRaises(zensend.ZenSendException) as cm:
      client.send_sms(body = "BODY", originator = "ORIG", numbers = ["447796354848","447796354849"])

    self.assertEqual(cm.exception.http_code, 400)
    self.assertEqual(cm.exception.failcode, "IS_EMPTY")
    self.assertEqual(cm.exception.parameter, "BODY")

  @responses.activate
  def test_handle_generic_error(self):
    responses.add(responses.POST,  "https://api.zensend.io/v3/sendsms", body="""
    {
      "failure": {
          "failcode": "FAILURE"
      }
    }""", status=400, content_type='application/json')
    client = zensend.Client("api_key")
    with self.assertRaises(zensend.ZenSendException) as cm:
      client.send_sms(body = "BODY", originator = "ORIG", numbers = ["447796354848","447796354849"])

    self.assertEqual(cm.exception.http_code, 400)
    self.assertEqual(cm.exception.failcode, "FAILURE")


  @responses.activate
  def test_does_not_allow_commas_in_numbers(self):

    client = zensend.Client("api_key")
    with self.assertRaises(ValueError) as cm:
      client.send_sms(body = "BODY", originator = "ORIG", numbers = ["44779635,4848"])

if __name__ == '__main__':
    unittest2.main()
